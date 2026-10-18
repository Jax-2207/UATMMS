import time
import uuid
from typing import Dict, List, Optional
from backend.app.core.logging import logger
from backend.app.schemas.simulation import (
    SimulationStateResponse,
    VehicleSnapshot,
    JunctionSignalSnapshot
)
from backend.app.safety.validator import safety_validator


class SimulationManager:
    """
    Simulation Lifecycle and State Manager.
    In Phase 0, operates as an authoritative state coordinator with synthetic test feeds.
    In Phase 1+, binds directly to SUMO microscopic physics via TraCI / libsumo.
    """

    def __init__(self):
        self.run_id: str = str(uuid.uuid4())[:8]
        self.status: str = "stopped"  # stopped, running, paused
        self.step: int = 0
        self.sim_time_s: float = 0.0
        self.step_length_s: float = 1.0
        self.active_vehicles: Dict[str, VehicleSnapshot] = {}
        self.active_signals: Dict[str, JunctionSignalSnapshot] = {}
        self._init_demo_topology()

    def _init_demo_topology(self):
        """Initializes a representative 6-junction network representation for Phase 0."""
        junction_names = ["J1_MG_Road", "J2_Brigade_Rd", "J3_Residency_Rd", "J4_Church_St", "J5_Commercial_St", "J6_Lavelle_Rd"]
        for j_id in junction_names:
            self.active_signals[j_id] = JunctionSignalSnapshot(
                junction_id=j_id,
                current_phase_index=0,
                current_phase_name="North-South Green",
                elapsed_time_s=12.0,
                min_green_s=10.0,
                max_green_s=60.0
            )
            safety_validator.register_junction(j_id, initial_phase=0, min_green_s=10.0)

    def start(self, scenario_id: str = "default_6junctions", seed: int = 42) -> SimulationStateResponse:
        self.run_id = str(uuid.uuid4())[:8]
        self.status = "running"
        self.step = 0
        self.sim_time_s = 0.0
        logger.info(f"Simulation started [run_id={self.run_id}, scenario={scenario_id}, seed={seed}]")
        return self.get_state()

    def pause(self) -> SimulationStateResponse:
        self.status = "paused"
        logger.info(f"Simulation paused [run_id={self.run_id}, step={self.step}]")
        return self.get_state()

    def resume(self) -> SimulationStateResponse:
        self.status = "running"
        logger.info(f"Simulation resumed [run_id={self.run_id}]")
        return self.get_state()

    def reset(self) -> SimulationStateResponse:
        self.status = "stopped"
        self.step = 0
        self.sim_time_s = 0.0
        self.active_vehicles.clear()
        self._init_demo_topology()
        logger.info(f"Simulation reset [run_id={self.run_id}]")
        return self.get_state()

    def step_forward(self) -> SimulationStateResponse:
        if self.status != "running":
            return self.get_state()

        self.step += 1
        self.sim_time_s += self.step_length_s

        # Update synthetic vehicles for Phase 0 preview
        if len(self.active_vehicles) < 15:
            v_id = f"veh_{self.step}"
            self.active_vehicles[v_id] = VehicleSnapshot(
                vehicle_id=v_id,
                edge_id="E_MG_Road_North",
                lane_index=0,
                position_m=10.0,
                speed_mps=11.5,
                vehicle_type="passenger" if self.step % 3 != 0 else "auto_rickshaw"
            )

        # Advance vehicles
        to_remove = []
        for vid, v in self.active_vehicles.items():
            v.position_m += v.speed_mps * self.step_length_s
            if v.position_m > 300.0:
                to_remove.append(vid)

        for vid in to_remove:
            del self.active_vehicles[vid]

        # Update signal elapsed time
        for j_id, sig in self.active_signals.items():
            sig.elapsed_time_s += self.step_length_s

        return self.get_state()

    def get_state(self) -> SimulationStateResponse:
        return SimulationStateResponse(
            run_id=self.run_id,
            status=self.status,
            step=self.step,
            simulation_time_s=self.sim_time_s,
            active_vehicle_count=len(self.active_vehicles),
            average_speed_mps=10.8 if self.active_vehicles else 0.0,
            average_waiting_time_s=4.2 if self.active_vehicles else 0.0,
            vehicles=list(self.active_vehicles.values()),
            signals=list(self.active_signals.values()),
            metadata={
                "engine": "UATMMS Authoritative Controller",
                "backend_version": "0.1.0-phase0"
            }
        )


simulation_manager = SimulationManager()
