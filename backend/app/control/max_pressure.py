"""
UATMMS Max-Pressure Controller
Implements decentralized Max-Pressure control (Varaiya 2013) by calculating:
  P_phase = sum(q_in) - sum(q_out)
and selecting the movement that maximizes upstream-to-downstream pressure relief.
"""
from typing import Dict, Any
from backend.app.control.base import BaseSignalController


class MaxPressureController(BaseSignalController):
    """
    Decentralized Max-Pressure Traffic Controller.
    Guarantees network stability by equalizing queue differentials between
    upstream inflow edges and downstream receiving edges.
    """

    def __init__(
        self,
        controller_id: str = "max_pressure",
        name: str = "Max-Pressure Controller",
        min_green_s: float = 10.0,
        max_green_s: float = 90.0,
        yellow_s: float = 3.0,
        all_red_s: float = 2.0,
        switching_threshold: float = 2.0  # Pressure differential needed to justify switch
    ):
        super().__init__(controller_id, name)
        self.min_green_s = min_green_s
        self.max_green_s = max_green_s
        self.yellow_s = yellow_s
        self.all_red_s = all_red_s
        self.switching_threshold = switching_threshold

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

            # Inflow and Outflow queues
            in_ns = state.get("in_queue_ns", state.get("ns_queue", 0))
            out_ns = state.get("out_queue_ns", 0)
            pressure_ns = in_ns - out_ns

            in_ew = state.get("in_queue_ew", state.get("ew_queue", 0))
            out_ew = state.get("out_queue_ew", 0)
            pressure_ew = in_ew - out_ew

            next_phase = curr_phase

            # Stage 0: NS Green
            if curr_phase == 0:
                if elapsed >= self.max_green_s:
                    next_phase = 1
                elif elapsed >= self.min_green_s:
                    # Switch if EW pressure exceeds NS pressure by switching threshold
                    if pressure_ew - pressure_ns >= self.switching_threshold:
                        next_phase = 1

            # Stage 1: NS Yellow
            elif curr_phase == 1:
                if elapsed >= self.yellow_s:
                    next_phase = 2

            # Stage 2: All-Red
            elif curr_phase == 2:
                if elapsed >= self.all_red_s:
                    next_phase = 3  # Grant EW Green

            # Stage 3: EW Green
            elif curr_phase == 3:
                if elapsed >= self.max_green_s:
                    next_phase = 4
                elif elapsed >= self.min_green_s:
                    # Switch if NS pressure exceeds EW pressure by switching threshold
                    if pressure_ns - pressure_ew >= self.switching_threshold:
                        next_phase = 4

            # Stage 4: EW Yellow
            elif curr_phase == 4:
                if elapsed >= self.yellow_s:
                    next_phase = 5

            # Stage 5: All-Red
            elif curr_phase == 5:
                if elapsed >= self.all_red_s:
                    next_phase = 0  # Grant NS Green

            if next_phase != curr_phase:
                self._phase_start_times[j_id] = sim_time_s
                self._current_phases[j_id] = next_phase

            target_phases[j_id] = next_phase

        return target_phases
