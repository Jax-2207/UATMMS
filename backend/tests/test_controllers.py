"""
Tests for Phase 4: Baseline Traffic Signal Controllers (Fixed-Time, Queue-Adaptive, Max-Pressure)
and SignalControlManager with SafetyValidator gating.
"""
import pytest
from backend.app.control.base import BaseSignalController
from backend.app.control.fixed_time import FixedTimeController
from backend.app.control.queue_adaptive import QueueAdaptiveController
from backend.app.control.max_pressure import MaxPressureController
from backend.app.control.manager import signal_control_manager, SignalControlManager
from backend.app.safety.validator import safety_validator


@pytest.fixture(autouse=True)
def reset_safety_and_controllers():
    """Reset safety validator state between tests."""
    safety_validator._junctions.clear()
    safety_validator._audit_log.clear()


def test_fixed_time_controller_cycle():
    """Verify FixedTimeController cycles strictly according to Webster stage timings."""
    controller = FixedTimeController()
    j_id = "J1_MG_Road"
    state = {j_id: {"current_phase": 0}}

    # At t=0s: should hold Phase 0 (NS Green)
    res_0 = controller.step(sim_time_s=0.0, junction_states=state)
    assert res_0[j_id] == 0

    # At t=29s: still hold Phase 0 (< 30s)
    state[j_id]["current_phase"] = res_0[j_id]
    res_29 = controller.step(sim_time_s=29.0, junction_states=state)
    assert res_29[j_id] == 0

    # At t=30s: transition to Phase 1 (NS Yellow)
    state[j_id]["current_phase"] = res_29[j_id]
    res_30 = controller.step(sim_time_s=30.0, junction_states=state)
    assert res_30[j_id] == 1

    # At t=33s: transition to Phase 2 (All-Red)
    state[j_id]["current_phase"] = res_30[j_id]
    res_33 = controller.step(sim_time_s=33.0, junction_states=state)
    assert res_33[j_id] == 2

    # At t=35s: transition to Phase 3 (EW Green)
    state[j_id]["current_phase"] = res_33[j_id]
    res_35 = controller.step(sim_time_s=35.0, junction_states=state)
    assert res_35[j_id] == 3


def test_queue_adaptive_gap_out_and_extension():
    """Verify QueueAdaptive gaps out on empty queues and extends on heavy queues."""
    controller = QueueAdaptiveController()
    j_id = "J1_MG_Road"

    # Start at t=100s with Phase 0 (NS Green)
    state = {j_id: {"current_phase": 0, "ns_queue": 10, "ew_queue": 5}}
    controller.step(sim_time_s=100.0, junction_states=state)

    # At t=105s (before min green 10s): even if ns_queue is 0, cannot gap out
    state[j_id]["ns_queue"] = 0
    res_early = controller.step(sim_time_s=105.0, junction_states=state)
    assert res_early[j_id] == 0  # Held due to min green

    # At t=111s (after min green 10s): with ns_queue=0 and ew_queue>0, gaps out to Phase 1 (Yellow)
    res_gapout = controller.step(sim_time_s=111.0, junction_states=state)
    assert res_gapout[j_id] == 1


def test_max_pressure_controller():
    """Verify MaxPressure controller switches when cross-pressure exceeds current pressure."""
    controller = MaxPressureController(switching_threshold=2.0)
    j_id = "J1_MG_Road"

    # In Phase 0 (NS Green) with high NS pressure
    state = {
        j_id: {
            "current_phase": 0,
            "in_queue_ns": 20,
            "out_queue_ns": 2,  # P_NS = 18
            "in_queue_ew": 5,
            "out_queue_ew": 3   # P_EW = 2
        }
    }
    controller.step(sim_time_s=200.0, junction_states=state)

    # At t=215s: min green elapsed, but NS pressure (18) dominates EW (2) -> hold Phase 0
    res_hold = controller.step(sim_time_s=215.0, junction_states=state)
    assert res_hold[j_id] == 0

    # Surge on EW approach: P_EW becomes 25 - 0 = 25 vs P_NS = 5 - 0 = 5
    state[j_id]["in_queue_ns"] = 5
    state[j_id]["out_queue_ns"] = 0
    state[j_id]["in_queue_ew"] = 25
    state[j_id]["out_queue_ew"] = 0

    res_switch = controller.step(sim_time_s=216.0, junction_states=state)
    # Differential P_EW - P_NS = 20 >= threshold 2.0 -> initiates yellow clearance Phase 1
    assert res_switch[j_id] == 1


def test_safety_validator_gating_in_controller():
    """Verify BaseSignalController rejects unsafe transitions and holds current safe state."""
    controller = QueueAdaptiveController()
    j_id = "J1_MG_Road"

    # Start in Phase 0 at t=300s
    state = {j_id: {"current_phase": 0, "ns_queue": 0, "ew_queue": 10}}
    controller.step(sim_time_s=300.0, junction_states=state)

    # Force an illegal jump directly to Phase 3 after 2 seconds (violates min green + skips yellow/all-red)
    class MaliciousController(BaseSignalController):
        def compute_target_phases(self, sim_time_s, junction_states):
            return {j_id: 3}

    bad_controller = MaliciousController("bad", "Malicious")
    res = bad_controller.step(sim_time_s=302.0, junction_states=state)

    # Must be REJECTED: stays in Phase 0
    assert res[j_id] == 0
    assert bad_controller.transitions_rejected >= 1
    assert bad_controller.transitions_approved == 0


def test_signal_control_manager_switching():
    """Verify SignalControlManager properly switches and queries controllers."""
    mgr = SignalControlManager()
    controllers = mgr.list_controllers()
    assert "fixed_time" in controllers
    assert "queue_adaptive" in controllers
    assert "max_pressure" in controllers

    assert mgr.active_controller.controller_id == "fixed_time"

    mgr.set_active_controller("max_pressure")
    assert mgr.active_controller.controller_id == "max_pressure"

    # Invalid controller switch should raise ValueError
    with pytest.raises(ValueError):
        mgr.set_active_controller("non_existent_controller")
