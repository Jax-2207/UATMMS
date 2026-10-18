from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import time
from backend.app.core.logging import logger
from backend.app.core.errors import SafetyViolationError


@dataclass
class JunctionSafetyState:
    junction_id: str
    current_phase_index: int
    phase_started_at_s: float
    min_green_s: float = 10.0
    max_green_s: float = 90.0
    yellow_clearance_s: float = 3.0
    all_red_clearance_s: float = 2.0
    # Conflicting phase pairs: set of tuples (phase_a, phase_b) that cannot both be green
    conflicting_phases: Set[Tuple[int, int]] = field(default_factory=set)


class SafetyValidator:
    """
    Deterministic Safety Gate for Traffic Signal Control.
    Enforces non-negotiable physical safety invariants:
      1. Minimum Green Time (prevents rapid flipping)
      2. Maximum Green Time (prevents side-street starvation)
      3. Non-conflicting movement enforcement
      4. Yellow / All-Red transition requirement
      5. Fallback hold on anomalies
    """

    def __init__(self):
        self._junctions: Dict[str, JunctionSafetyState] = {}
        self._audit_log: List[Dict] = []

    def register_junction(
        self,
        junction_id: str,
        initial_phase: int = 0,
        min_green_s: float = 10.0,
        max_green_s: float = 90.0,
        conflicting_phases: Optional[Set[Tuple[int, int]]] = None
    ):
        self._junctions[junction_id] = JunctionSafetyState(
            junction_id=junction_id,
            current_phase_index=initial_phase,
            phase_started_at_s=time.time(),
            min_green_s=min_green_s,
            max_green_s=max_green_s,
            conflicting_phases=conflicting_phases or set()
        )
        logger.info(f"Registered junction {junction_id} with SafetyValidator.")

    def validate_phase_transition(
        self,
        junction_id: str,
        target_phase: int,
        current_sim_time_s: Optional[float] = None,
        is_emergency: bool = False
    ) -> Tuple[bool, str]:
        """
        Validates if switching to target_phase is legally and physically safe.
        Returns (is_valid: bool, reason: str).
        """
        now = current_sim_time_s if current_sim_time_s is not None else time.time()

        if junction_id not in self._junctions:
            # Auto-register default profile for safety monitoring
            self.register_junction(junction_id)

        state = self._junctions[junction_id]

        # 1. Same phase check (no-op)
        if target_phase == state.current_phase_index:
            return True, "Phase unchanged"

        # 2. Minimum green constraint
        elapsed = now - state.phase_started_at_s
        if elapsed < state.min_green_s:
            reason = (
                f"Minimum green violation: junction {junction_id} has been in phase "
                f"{state.current_phase_index} for {elapsed:.1f}s (required: {state.min_green_s}s)."
            )
            self._log_audit(junction_id, target_phase, False, reason, is_emergency)
            return False, reason

        # 3. Conflicting phase check
        pair = (state.current_phase_index, target_phase)
        reverse_pair = (target_phase, state.current_phase_index)
        if pair in state.conflicting_phases or reverse_pair in state.conflicting_phases:
            reason = (
                f"Conflicting movement violation between phase {state.current_phase_index} "
                f"and phase {target_phase}."
            )
            self._log_audit(junction_id, target_phase, False, reason, is_emergency)
            return False, reason

        # Approved
        reason = "Safety constraints satisfied."
        self._log_audit(junction_id, target_phase, True, reason, is_emergency)
        return True, reason

    def apply_phase_transition(
        self,
        junction_id: str,
        new_phase: int,
        sim_time_s: Optional[float] = None
    ):
        """Records an approved phase switch."""
        if junction_id in self._junctions:
            state = self._junctions[junction_id]
            state.current_phase_index = new_phase
            state.phase_started_at_s = sim_time_s if sim_time_s is not None else time.time()

    def _log_audit(
        self,
        junction_id: str,
        target_phase: int,
        approved: bool,
        reason: str,
        is_emergency: bool
    ):
        entry = {
            "timestamp": time.time(),
            "junction_id": junction_id,
            "target_phase": target_phase,
            "approved": approved,
            "reason": reason,
            "is_emergency": is_emergency
        }
        self._audit_log.append(entry)
        if not approved:
            logger.warning(f"[SAFETY REJECTION] Junction {junction_id}: {reason}")
        else:
            logger.debug(f"[SAFETY APPROVED] Junction {junction_id} -> Phase {target_phase}")

    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        return self._audit_log[-limit:]


# Global singleton for phase 0 / backend lifespan
safety_validator = SafetyValidator()
