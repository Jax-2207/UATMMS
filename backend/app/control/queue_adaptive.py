"""
UATMMS Queue-Based Adaptive Controller
Dynamically extends green phases when vehicle queues persist, up to G_max = 90s,
and clears empty approaches early down to G_min = 10s.
"""
from typing import Dict, Any
from backend.app.control.base import BaseSignalController


class QueueAdaptiveController(BaseSignalController):
    """
    Queue-Based Actuated Traffic Controller.
    Transitions:
      Phase 0 (NS Green) -> Phase 1 (NS Yellow, 3s) -> Phase 2 (All-Red, 2s)
      -> Phase 3 (EW Green) -> Phase 4 (EW Yellow, 3s) -> Phase 5 (All-Red, 2s) -> Phase 0
    Rules:
      - Green phases (0, 3) obey Min Green (10s) and Max Green (90s).
      - If active green queue is cleared (queue == 0) after Min Green, gap-out early to yellow.
      - If active green queue persists and cross-street queue is small, extend green up to Max Green.
    """

    def __init__(
        self,
        controller_id: str = "queue_adaptive",
        name: str = "Queue-Based Adaptive Controller",
        min_green_s: float = 10.0,
        max_green_s: float = 90.0,
        yellow_s: float = 3.0,
        all_red_s: float = 2.0
    ):
        super().__init__(controller_id, name)
        self.min_green_s = min_green_s
        self.max_green_s = max_green_s
        self.yellow_s = yellow_s
        self.all_red_s = all_red_s

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
            ns_queue = state.get("ns_queue", state.get("total_queue", 0) // 2)
            ew_queue = state.get("ew_queue", state.get("total_queue", 0) // 2)

            next_phase = curr_phase

            # Stage 0: NS Green
            if curr_phase == 0:
                if elapsed >= self.max_green_s:
                    next_phase = 1  # Force Max-Out
                elif elapsed >= self.min_green_s:
                    if ns_queue == 0 and ew_queue > 0:
                        next_phase = 1  # Gap-Out: service cross street

            # Stage 1: NS Yellow
            elif curr_phase == 1:
                if elapsed >= self.yellow_s:
                    next_phase = 2

            # Stage 2: All-Red
            elif curr_phase == 2:
                if elapsed >= self.all_red_s:
                    next_phase = 3  # Switch to EW Green

            # Stage 3: EW Green
            elif curr_phase == 3:
                if elapsed >= self.max_green_s:
                    next_phase = 4  # Force Max-Out
                elif elapsed >= self.min_green_s:
                    if ew_queue == 0 and ns_queue > 0:
                        next_phase = 4  # Gap-Out: service cross street

            # Stage 4: EW Yellow
            elif curr_phase == 4:
                if elapsed >= self.yellow_s:
                    next_phase = 5

            # Stage 5: All-Red
            elif curr_phase == 5:
                if elapsed >= self.all_red_s:
                    next_phase = 0  # Switch to NS Green

            if next_phase != curr_phase:
                self._phase_start_times[j_id] = sim_time_s
                self._current_phases[j_id] = next_phase

            target_phases[j_id] = next_phase

        return target_phases
