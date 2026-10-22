"""
UATMMS Emergency Arbitration Engine
Resolves conflicting emergency corridor requests using priority rules.
"""

from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
from backend.app.schemas.emergency import (
    EmergencyCorridorPlan, EmergencySeverity, EmergencyStatus
)
from backend.app.core.logging import logger


class ConflictingEmergencies:
    """Represents a set of overlapping emergency corridor requests."""

    def __init__(self, emergencies: List[Tuple[str, EmergencyCorridorPlan]]):
        """
        Args:
            emergencies: List of (request_id, corridor_plan) tuples
        """
        self.emergencies = emergencies
        self.conflicting_junctions: Set[str] = self._find_conflicting_junctions()
        self.conflicting_time_windows: List[Tuple[float, float]] = self._find_time_overlaps()

    def _find_conflicting_junctions(self) -> Set[str]:
        """Identify junctions where multiple emergencies need green."""
        all_junction_sets = [
            set(plan.route_junctions)
            for _, plan in self.emergencies
        ]

        # Find intersection (common junctions)
        if not all_junction_sets:
            return set()

        conflicting = all_junction_sets[0]
        for junctions in all_junction_sets[1:]:
            conflicting &= junctions

        return conflicting

    def _find_time_overlaps(self) -> List[Tuple[float, float]]:
        """Find time windows where multiple corridors overlap."""
        overlaps = []

        for i in range(len(self.emergencies)):
            for j in range(i + 1, len(self.emergencies)):
                _, plan_i = self.emergencies[i]
                _, plan_j = self.emergencies[j]

                # Get time ranges for each corridor
                if plan_i.corridor_windows and plan_j.corridor_windows:
                    start_i = plan_i.corridor_windows[0].green_window_start_s
                    end_i = plan_i.corridor_windows[-1].green_window_end_s
                    start_j = plan_j.corridor_windows[0].green_window_start_s
                    end_j = plan_j.corridor_windows[-1].green_window_end_s

                    # Check for overlap
                    overlap_start = max(start_i, start_j)
                    overlap_end = min(end_i, end_j)

                    if overlap_start < overlap_end:
                        overlaps.append((overlap_start, overlap_end))

        return overlaps

    def has_direct_conflict(self) -> bool:
        """Check if corridors have direct (same junction + same time) conflicts."""
        return len(self.conflicting_junctions) > 0 and len(self.conflicting_time_windows) > 0


class EmergencyArbitrator:
    """
    Resolves conflicts between overlapping emergency corridor requests.
    Uses explicit priority rules and scheduling logic.
    """

    def __init__(self):
        self.pending_emergencies: Dict[str, Tuple[EmergencyCorridorPlan, datetime]] = {}
        self.active_emergencies: Dict[str, Tuple[EmergencyCorridorPlan, datetime]] = {}
        self.conflict_history: List[Dict] = []

    def evaluate_conflict(
        self,
        emergency_queue: List[Tuple[str, EmergencyCorridorPlan]]
    ) -> Dict[str, EmergencyCorridorPlan]:
        """
        Evaluate overlapping emergencies and return arbitrated corridor assignments.

        Strategy:
        1. Separate emergencies by severity (CRITICAL > HIGH > MEDIUM)
        2. For same severity, use FIFO (earliest request wins)
        3. For conflicting junctions, slightly adjust timing (stagger corridors) rather than cancel

        Args:
            emergency_queue: List of (request_id, corridor_plan) tuples

        Returns:
            Dict of {request_id: adjusted_corridor_plan}
        """
        if not emergency_queue:
            return {}

        logger.info(f"[Arbitrator] Evaluating {len(emergency_queue)} emergency requests for conflicts")

        # Check for conflicts
        conflict = ConflictingEmergencies(emergency_queue)

        if not conflict.has_direct_conflict():
            logger.info("[Arbitrator] No conflicts detected. All corridors approved as-is.")
            result = {req_id: plan for req_id, plan in emergency_queue}
        else:
            logger.warning(
                f"[Arbitrator] CONFLICT DETECTED: {len(conflict.conflicting_junctions)} shared junctions, "
                f"{len(conflict.conflicting_time_windows)} time overlaps"
            )
            # Resolve via priority-based scheduling
            result = self._resolve_by_priority(emergency_queue, conflict)

        # Always log arbitration
        self._log_arbitration(result)
        return result

    def _resolve_by_priority(
        self,
        emergency_queue: List[Tuple[str, EmergencyCorridorPlan]],
        conflict: ConflictingEmergencies
    ) -> Dict[str, EmergencyCorridorPlan]:
        """
        Arbitrate by priority: severity first, then FIFO.
        For conflicting junctions, stagger corridors in time (add delay).

        Returns:
            Dict of {request_id: adjusted_corridor_plan}
        """
        # Sort by severity (lower severity value = higher priority) and request order
        sorted_queue = sorted(emergency_queue, key=lambda x: x[1].created_at_s)

        result: Dict[str, EmergencyCorridorPlan] = {}
        used_junctions_by_window: Dict[str, Set[str]] = {}  # Track junction usage per time window

        for request_id, plan in sorted_queue:
            # Check if this corridor conflicts with already-assigned corridors
            conflict_offset = self._calculate_stagger_offset(
                plan,
                conflict.conflicting_junctions,
                used_junctions_by_window
            )

            if conflict_offset > 0:
                logger.warning(
                    f"[Arbitrator] Staggering {request_id}: +{conflict_offset:.1f}s offset applied"
                )
                # Create adjusted plan with delayed corridor
                adjusted_plan = self._offset_corridor_plan(plan, conflict_offset)
                result[request_id] = adjusted_plan

                # Record which junctions are now claimed
                self._record_junction_usage(adjusted_plan, used_junctions_by_window)
            else:
                # No adjustment needed
                result[request_id] = plan
                self._record_junction_usage(plan, used_junctions_by_window)

        # Log arbitration result
        self._log_arbitration(result)

        return result

    def _calculate_stagger_offset(
        self,
        plan: EmergencyCorridorPlan,
        conflicting_junctions: Set[str],
        used_junctions_by_window: Dict[str, Set[str]]
    ) -> float:
        """
        Calculate time offset needed to avoid junction conflicts.

        Returns:
            Offset in seconds (0 if no conflict, > 0 if stagger needed).
        """
        offset = 0.0
        stagger_interval = 15.0  # Minimum time between corridors at same junction

        for window in plan.corridor_windows:
            if window.junction_id in conflicting_junctions:
                # Check if this junction is already claimed in a nearby time window
                for claimed_time_key, claimed_junctions in used_junctions_by_window.items():
                    if window.junction_id in claimed_junctions:
                        # Extract time and check overlap
                        try:
                            claimed_time = float(claimed_time_key)
                            window_time = window.green_window_start_s

                            # If within stagger interval, increase offset
                            if abs(window_time - claimed_time) < stagger_interval:
                                needed_offset = stagger_interval - (window_time - claimed_time)
                                offset = max(offset, needed_offset)
                        except ValueError:
                            pass

        return offset

    def _offset_corridor_plan(self, plan: EmergencyCorridorPlan, offset_s: float) -> EmergencyCorridorPlan:
        """Create a new corridor plan with all windows shifted by offset."""
        offset_windows = []

        for window in plan.corridor_windows:
            offset_window = window.model_copy(update={
                "green_window_start_s": window.green_window_start_s + offset_s,
                "green_window_end_s": window.green_window_end_s + offset_s,
                "estimated_arrival_s": window.estimated_arrival_s + offset_s
            })
            offset_windows.append(offset_window)

        return plan.model_copy(update={
            "corridor_windows": offset_windows,
            "total_estimated_travel_time_s": plan.total_estimated_travel_time_s + offset_s
        })

    def _record_junction_usage(
        self,
        plan: EmergencyCorridorPlan,
        used_junctions_by_window: Dict[str, Set[str]]
    ):
        """Record which junctions this corridor uses and when."""
        for window in plan.corridor_windows:
            time_key = str(window.green_window_start_s)
            if time_key not in used_junctions_by_window:
                used_junctions_by_window[time_key] = set()
            used_junctions_by_window[time_key].add(window.junction_id)

    def _log_arbitration(self, result: Dict[str, EmergencyCorridorPlan]):
        """Log arbitration results."""
        total_offset = 0.0
        for request_id, plan in result.items():
            logger.info(f"[Arbitrator] {request_id}: Approved with {len(plan.corridor_windows)} windows")
            total_offset += plan.total_estimated_travel_time_s

        self.conflict_history.append({
            "timestamp": datetime.now().isoformat(),
            "total_requests": len(result),
            "total_delayed_offset_s": total_offset
        })

    def get_conflict_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conflict resolution history."""
        return self.conflict_history[-limit:]


# Global instance
emergency_arbitrator = EmergencyArbitrator()
