"""
UATMMS Base Signal Controller
Defines the abstract interface for all traffic signal controllers with mandatory
deterministic SafetyValidator gating and performance telemetry.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.app.safety.validator import safety_validator
from backend.app.core.logging import logger


class BaseSignalController(ABC):
    """
    Abstract Base Class for Traffic Signal Controllers.
    Enforces that every phase switch decision is gated through SafetyValidator.
    """

    def __init__(self, controller_id: str, name: str):
        self.controller_id = controller_id
        self.name = name
        self.total_decisions: int = 0
        self.transitions_requested: int = 0
        self.transitions_approved: int = 0
        self.transitions_rejected: int = 0

    @abstractmethod
    def compute_target_phases(
        self,
        sim_time_s: float,
        junction_states: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Subclasses implement their specific control policy here.
        Returns: {junction_id: desired_target_phase_index}
        """
        pass

    def step(
        self,
        sim_time_s: float,
        junction_states: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Executes controller step and passes all desired decisions through the SafetyValidator.
        Returns: {junction_id: safe_applied_phase_index}
        """
        self.total_decisions += 1
        desired_phases = self.compute_target_phases(sim_time_s, junction_states)
        applied_phases: Dict[str, int] = {}

        for j_id, target_phase in desired_phases.items():
            state = junction_states.get(j_id, {})
            current_phase = state.get("current_phase", 0)

            # Ensure junction is registered in SafetyValidator at initial observation time
            if j_id not in safety_validator._junctions:
                safety_validator.register_junction(
                    junction_id=j_id,
                    initial_phase=current_phase,
                    initial_phase_time_s=sim_time_s
                )

            if target_phase == current_phase:
                applied_phases[j_id] = current_phase
                continue


            self.transitions_requested += 1
            is_valid, reason = safety_validator.validate_phase_transition(
                junction_id=j_id,
                target_phase=target_phase,
                current_sim_time_s=sim_time_s
            )

            if is_valid:
                safety_validator.apply_phase_transition(
                    junction_id=j_id,
                    new_phase=target_phase,
                    sim_time_s=sim_time_s
                )
                applied_phases[j_id] = target_phase
                self.transitions_approved += 1
            else:
                # Safety fallback: hold current safe phase
                applied_phases[j_id] = current_phase
                self.transitions_rejected += 1
                logger.debug(
                    f"[{self.name}] Safety rejected phase change for {j_id} "
                    f"to {target_phase}: {reason}. Retaining {current_phase}."
                )

        return applied_phases

    def get_stats(self) -> Dict[str, Any]:
        return {
            "controller_id": self.controller_id,
            "name": self.name,
            "total_decisions": self.total_decisions,
            "transitions_requested": self.transitions_requested,
            "transitions_approved": self.transitions_approved,
            "transitions_rejected": self.transitions_rejected,
            "rejection_rate": (
                round(self.transitions_rejected / self.transitions_requested, 4)
                if self.transitions_requested > 0 else 0.0
            )
        }
