import pytest
import time
from backend.app.safety.validator import SafetyValidator


def test_safety_validator_minimum_green():
    validator = SafetyValidator()
    junction = "J_Test_1"
    now = 100.0
    validator.register_junction(junction, initial_phase=0, min_green_s=10.0)
    validator._junctions[junction].phase_started_at_s = now

    # Attempt to change phase after only 4 seconds (should be REJECTED)
    valid, reason = validator.validate_phase_transition(
        junction_id=junction,
        target_phase=1,
        current_sim_time_s=now + 4.0
    )
    assert not valid
    assert "Minimum green violation" in reason

    # Attempt to change phase after 11 seconds (should be APPROVED)
    valid_after, reason_after = validator.validate_phase_transition(
        junction_id=junction,
        target_phase=1,
        current_sim_time_s=now + 11.0
    )
    assert valid_after
    assert "satisfied" in reason_after


def test_safety_validator_conflicting_phases():
    validator = SafetyValidator()
    junction = "J_Test_Conflict"
    now = 100.0
    # Register conflict between phase 0 and phase 2
    validator.register_junction(
        junction_id=junction,
        initial_phase=0,
        min_green_s=5.0,
        conflicting_phases={(0, 2)}
    )
    validator._junctions[junction].phase_started_at_s = now

    # Try transitioning directly to conflicting phase 2 after min_green has elapsed
    valid, reason = validator.validate_phase_transition(
        junction_id=junction,
        target_phase=2,
        current_sim_time_s=now + 10.0
    )
    assert not valid
    assert "Conflicting movement violation" in reason
