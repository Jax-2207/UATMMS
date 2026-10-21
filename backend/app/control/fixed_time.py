"""
UATMMS Fixed-Time Signal Controller
Cycles cyclically through pre-timed stages regardless of real-time queues.
"""
from typing import Dict, Any, List
from backend.app.control.base import BaseSignalController


class FixedTimeController(BaseSignalController):
    """
    Fixed-Time (Pre-timed) Signal Controller.
    Implements standard Webster/IRC 6-stage signal cycle:
      Stage 0 (Phase 0): NS Green (30s)
      Stage 1 (Phase 1): NS Yellow (3s)
      Stage 2 (Phase 2): All-Red Clearance (2s)
      Stage 3 (Phase 3): EW Green (25s)
      Stage 4 (Phase 4): EW Yellow (3s)
      Stage 5 (Phase 5): All-Red Clearance (2s)
    Total Cycle Length = 65s.
    """

    DEFAULT_PHASE_DURATIONS: List[float] = [30.0, 3.0, 2.0, 25.0, 3.0, 2.0]

    def __init__(
        self,
        controller_id: str = "fixed_time",
        name: str = "Fixed-Time Controller",
        phase_durations: List[float] = None
    ):
        super().__init__(controller_id, name)
        self.phase_durations = phase_durations or self.DEFAULT_PHASE_DURATIONS
        self.num_phases = len(self.phase_durations)
        # Tracking phase start times per junction: {junction_id: sim_time_s}
        self._phase_start_times: Dict[str, float] = {}
        self._current_phases: Dict[str, int] = {}

    def compute_target_phases(
        self,
        sim_time_s: float,
        junction_states: Dict[str, Any]
    ) -> Dict[str, int]:
        target_phases: Dict[str, int] = {}

        for j_id, state in junction_states.items():
            curr_phase = state.get("current_phase", self._current_phases.get(j_id, 0))

            if j_id not in self._phase_start_times:
                self._phase_start_times[j_id] = sim_time_s
                self._current_phases[j_id] = curr_phase

            elapsed = sim_time_s - self._phase_start_times[j_id]
            scheduled_duration = self.phase_durations[curr_phase]

            if elapsed >= scheduled_duration:
                # Advance to next phase in round-robin cycle
                next_phase = (curr_phase + 1) % self.num_phases
                target_phases[j_id] = next_phase
                self._phase_start_times[j_id] = sim_time_s
                self._current_phases[j_id] = next_phase
            else:
                target_phases[j_id] = curr_phase

        return target_phases
