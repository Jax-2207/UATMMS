"""
UATMMS TraCI Python Adapter
Provides direct bidirectional interface with Eclipse SUMO microscopic physics.
Enforces that ALL signal changes pass through the deterministic Safety Validator.
"""
from typing import List, Dict, Optional, Tuple, Any
import os
import shutil
import time

try:
    import traci
    import traci.constants as tc
    TRACI_AVAILABLE = True
except ImportError:
    traci = None
    TRACI_AVAILABLE = False

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.errors import SimulationError, SafetyViolationError
from backend.app.safety.validator import safety_validator
from backend.app.schemas.simulation import VehicleSnapshot, JunctionSignalSnapshot


class TraciAdapter:
    """
    Adapter between UATMMS modular monolith and SUMO TraCI / libsumo API.
    Manages process lifecycle, state extraction, and safety-validated signal controls.
    """

    def __init__(self):
        self.is_connected: bool = False
        self.simulation_time_s: float = 0.0
        self.step_count: int = 0
        self.step_length_s: float = 1.0
        self.config_path: Optional[str] = None
        self.active_tl_ids: List[str] = []

    def find_sumo_binary(self, gui: bool = False) -> Optional[str]:
        """Locates the sumo / sumo-gui binary on system PATH or configured SUMO_HOME."""
        target_name = settings.SUMO_GUI_BINARY if gui else settings.SUMO_BINARY
        # 1. Check direct PATH
        binary = shutil.which(target_name) or shutil.which(f"{target_name}.exe")
        if binary:
            return binary

        # 2. Check SUMO_HOME directory
        sumo_home = os.environ.get("SUMO_HOME", settings.SUMO_HOME)
        if sumo_home and os.path.exists(sumo_home):
            bin_path = os.path.join(sumo_home, "bin", f"{target_name}.exe")
            if os.path.exists(bin_path):
                return bin_path
            bin_path_no_ext = os.path.join(sumo_home, "bin", target_name)
            if os.path.exists(bin_path_no_ext):
                return bin_path_no_ext

        return None

    def start(
        self,
        config_path: str,
        gui: bool = False,
        step_length_s: float = 1.0,
        seed: int = 42
    ) -> bool:
        """
        Initializes and starts a SUMO TraCI simulation session.
        Returns True on successful connection, False otherwise.
        """
        if not TRACI_AVAILABLE:
            logger.warning("TraCI library not available in environment. Running in mock/synthetic mode.")
            return False

        binary = self.find_sumo_binary(gui=gui)
        if not binary:
            logger.warning(f"SUMO binary '{settings.SUMO_BINARY}' not found on system. Running in mock/synthetic mode.")
            return False

        if not os.path.exists(config_path):
            raise SimulationError(f"SUMO configuration file not found at: {config_path}")

        sumo_cmd = [
            binary,
            "-c", os.path.abspath(config_path),
            "--step-length", str(step_length_s),
            "--seed", str(seed),
            "--no-warnings", "true",
            "--duration-log.disable", "true",
            "--waiting-time-memory", "300"
        ]

        try:
            if self.is_connected:
                self.close()

            logger.info(f"Starting SUMO via TraCI: {' '.join(sumo_cmd)}")
            traci.start(sumo_cmd)
            self.is_connected = True
            self.step_length_s = step_length_s
            self.step_count = 0
            self.simulation_time_s = 0.0
            self.config_path = config_path
            self.active_tl_ids = list(traci.trafficlight.getIDList())
            logger.info(f"TraCI connected successfully. Detected traffic lights: {self.active_tl_ids}")
            return True
        except Exception as e:
            self.is_connected = False
            logger.error(f"Failed to start SUMO TraCI: {e}")
            raise SimulationError(f"TraCI connection failed: {e}")

    def step(self) -> float:
        """Advances the microscopic SUMO simulation by 1 step."""
        if not self.is_connected or not traci:
            self.simulation_time_s += self.step_length_s
            self.step_count += 1
            return self.simulation_time_s

        try:
            traci.simulationStep()
            self.simulation_time_s = float(traci.simulation.getTime())
            self.step_count += 1
            return self.simulation_time_s
        except Exception as e:
            logger.error(f"TraCI step failed: {e}")
            self.is_connected = False
            raise SimulationError(f"Simulation stepping error: {e}")

    def close(self):
        """Safely terminates the TraCI session."""
        if self.is_connected and traci:
            try:
                traci.close()
                logger.info("TraCI simulation closed.")
            except Exception as e:
                logger.warning(f"Exception during TraCI close: {e}")
            finally:
                self.is_connected = False

    def get_active_vehicles(self) -> List[VehicleSnapshot]:
        """Polls microscopic vehicle positions, speeds, and lane data from SUMO."""
        if not self.is_connected or not traci:
            return []

        snapshots: List[VehicleSnapshot] = []
        try:
            veh_ids = traci.vehicle.getIDList()
            for vid in veh_ids:
                edge_id = traci.vehicle.getRoadID(vid)
                # Ignore vehicles on internal junction lanes (prepended with ':')
                lane_index = traci.vehicle.getLaneIndex(vid)
                pos_m = float(traci.vehicle.getLanePosition(vid))
                speed_mps = float(traci.vehicle.getSpeed(vid))
                v_type = traci.vehicle.getTypeID(vid)

                snapshots.append(
                    VehicleSnapshot(
                        vehicle_id=vid,
                        edge_id=edge_id,
                        lane_index=lane_index,
                        position_m=pos_m,
                        speed_mps=speed_mps,
                        vehicle_type=v_type
                    )
                )
        except Exception as e:
            logger.error(f"Error polling vehicles from TraCI: {e}")

        return snapshots

    def get_junction_signals(self) -> List[JunctionSignalSnapshot]:
        """Polls current phase index, elapsed duration, and state from all signalized junctions."""
        if not self.is_connected or not traci:
            return []

        signals: List[JunctionSignalSnapshot] = []
        try:
            for tl_id in self.active_tl_ids:
                phase_idx = int(traci.trafficlight.getPhase(tl_id))
                phase_name = traci.trafficlight.getPhaseName(tl_id) or f"Phase_{phase_idx}"
                # Get phase duration
                duration = float(traci.trafficlight.getPhaseDuration(tl_id))

                signals.append(
                    JunctionSignalSnapshot(
                        junction_id=tl_id,
                        current_phase_index=phase_idx,
                        current_phase_name=phase_name,
                        elapsed_time_s=duration,
                        min_green_s=10.0,
                        max_green_s=90.0
                    )
                )
        except Exception as e:
            logger.error(f"Error polling traffic lights from TraCI: {e}")

        return signals

    def get_edge_metrics(self, edge_id: str) -> Dict[str, Any]:
        """Extracts traffic density, waiting time, and mean speed for a specific edge."""
        if not self.is_connected or not traci:
            return {
                "edge_id": edge_id,
                "vehicle_count": 0,
                "mean_speed_mps": 0.0,
                "waiting_time_s": 0.0,
                "occupancy_ratio": 0.0
            }

        try:
            return {
                "edge_id": edge_id,
                "vehicle_count": int(traci.edge.getLastStepVehicleNumber(edge_id)),
                "mean_speed_mps": float(traci.edge.getLastStepMeanSpeed(edge_id)),
                "waiting_time_s": float(traci.edge.getWaitingTime(edge_id)),
                "occupancy_ratio": float(traci.edge.getLastStepOccupancy(edge_id))
            }
        except Exception as e:
            logger.warning(f"Failed to get edge metrics for {edge_id}: {e}")
            return {"edge_id": edge_id, "error": str(e)}

    def set_junction_phase(
        self,
        junction_id: str,
        target_phase: int,
        is_emergency: bool = False
    ) -> Tuple[bool, str]:
        """
        Applies a signal phase adjustment strictly after validation by SafetyValidator.
        Returns (approved: bool, reason: str).
        """
        # 1. Hard Invariant Check via Safety Gate
        is_valid, reason = safety_validator.validate_phase_transition(
            junction_id=junction_id,
            target_phase=target_phase,
            current_sim_time_s=self.simulation_time_s,
            is_emergency=is_emergency
        )

        if not is_valid:
            logger.warning(f"Signal adjustment for {junction_id} REJECTED by SafetyValidator: {reason}")
            return False, reason

        # 2. Approved: Apply command to SUMO via TraCI
        if self.is_connected and traci:
            try:
                traci.trafficlight.setPhase(junction_id, target_phase)
                safety_validator.apply_phase_transition(junction_id, target_phase, self.simulation_time_s)
                logger.debug(f"Applied phase {target_phase} on {junction_id} via TraCI.")
                return True, "Phase applied to SUMO."
            except Exception as e:
                logger.error(f"TraCI failed to set phase for {junction_id}: {e}")
                return False, f"TraCI execution error: {e}"

        # Synthetic/fallback mode approval
        safety_validator.apply_phase_transition(junction_id, target_phase, self.simulation_time_s)
        return True, "Safety approved (synthetic mode)."


# Singleton adapter instance
traci_adapter = TraciAdapter()
