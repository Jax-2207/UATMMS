"""
Unit tests for emergency corridor scheduling and request management.
"""

import pytest
from backend.app.schemas.emergency import (
    EmergencyRequest, EmergencyType, EmergencySeverity, EmergencyStatus
)
from backend.app.emergency.manager import EmergencyRequestManager
from backend.app.emergency.corridor_scheduler import CorridorScheduler
from backend.app.core.errors import ValidationError


class TestCorridorScheduler:
    """Test emergency corridor scheduling."""

    @pytest.fixture
    def scheduler(self):
        return CorridorScheduler(buffer_s=5.0, clearance_s=3.0)

    def test_schedule_corridor_basic(self, scheduler):
        """Test basic corridor scheduling with ETA calculations."""
        plan = scheduler.schedule_corridor(
            request_id="EMG001",
            vehicle_id="AMB001",
            origin_junction="J1",
            destination_junction="J5",
            vehicle_type=EmergencyType.AMBULANCE,
            severity=EmergencySeverity.CRITICAL,
            current_sim_time_s=0.0
        )

        assert plan.request_id == "EMG001"
        assert plan.vehicle_id == "AMB001"
        assert len(plan.corridor_windows) > 0
        assert plan.total_estimated_travel_time_s > 0

    def test_corridor_windows_timing(self, scheduler):
        """Test that corridor windows are properly spaced with ETA calculations."""
        plan = scheduler.schedule_corridor(
            request_id="EMG002",
            vehicle_id="FIRE001",
            origin_junction="J1",
            destination_junction="J3",
            vehicle_type=EmergencyType.FIRE,
            severity=EmergencySeverity.HIGH,
            current_sim_time_s=100.0
        )

        # Verify window structure
        for i, window in enumerate(plan.corridor_windows):
            # Each window should have valid time bounds
            assert window.green_window_start_s < window.green_window_end_s
            # Window duration should be reasonable
            duration = window.green_window_end_s - window.green_window_start_s
            assert duration >= scheduler.green_window_min_duration_s

    def test_validate_corridor_feasibility(self, scheduler):
        """Test corridor feasibility validation."""
        plan = scheduler.schedule_corridor(
            request_id="EMG003",
            vehicle_id="AMB003",
            origin_junction="J1",
            destination_junction="J4",
            vehicle_type=EmergencyType.AMBULANCE,
            severity=EmergencySeverity.CRITICAL,
            current_sim_time_s=0.0
        )

        # Recent corridor should be feasible
        is_feasible, reason = scheduler.validate_corridor_feasibility(plan, 0.0)
        assert is_feasible

        # Very old corridor should be infeasible
        is_feasible, reason = scheduler.validate_corridor_feasibility(plan, 1000.0)
        assert not is_feasible


class TestEmergencyRequestManager:
    """Test emergency request management."""

    @pytest.fixture
    def manager(self):
        mgr = EmergencyRequestManager()
        mgr.max_concurrent_corridors = 5  # Allow more for testing
        return mgr

    @pytest.fixture
    def sample_request(self):
        return EmergencyRequest(
            vehicle_id="AMB001",
            origin_junction="J1",
            destination_junction="J5",
            vehicle_type=EmergencyType.AMBULANCE,
            severity=EmergencySeverity.CRITICAL,
            requester_id="USER001"
        )

    def test_create_request_basic(self, manager, sample_request):
        """Test basic emergency request creation."""
        response = manager.create_emergency_request(sample_request, current_sim_time_s=0.0)

        assert response.request_id is not None
        assert response.vehicle_id == "AMB001"
        assert response.status in [EmergencyStatus.REQUESTED, EmergencyStatus.ROUTE_PLANNED]

    def test_create_request_validation(self, manager):
        """Test request validation catches errors."""
        invalid_request = EmergencyRequest(
            vehicle_id="AMB001",
            origin_junction="J1",
            destination_junction="J1",  # Same as origin - invalid!
            vehicle_type=EmergencyType.AMBULANCE,
            severity=EmergencySeverity.CRITICAL,
            requester_id="USER001"
        )

        with pytest.raises(ValidationError):
            manager.create_emergency_request(invalid_request, current_sim_time_s=0.0)

    def test_multiple_requests_queuing(self, manager, sample_request):
        """Test that multiple requests are queued properly."""
        # Create multiple requests
        for i in range(3):
            req = sample_request.model_copy(update={"vehicle_id": f"AMB{i:03d}"})
            manager.create_emergency_request(req, current_sim_time_s=0.0)

        # Should process them (exact state depends on arbitration)
        total_requests = len(manager.requests)
        assert total_requests >= 3

    def test_get_request_status(self, manager, sample_request):
        """Test retrieving request status."""
        response = manager.create_emergency_request(sample_request, current_sim_time_s=0.0)
        request_id = response.request_id

        # Retrieve status
        status = manager.get_request_status(request_id)
        assert status is not None
        assert status.request_id == request_id
        assert status.vehicle_id == "AMB001"

    def test_get_nonexistent_request(self, manager):
        """Test that nonexistent requests return None."""
        status = manager.get_request_status("NONEXISTENT")
        assert status is None

    def test_complete_emergency(self, manager, sample_request):
        """Test completing an emergency request and recording metrics."""
        from backend.app.schemas.emergency import EmergencyCompletionReport

        response = manager.create_emergency_request(sample_request, current_sim_time_s=0.0)
        request_id = response.request_id

        # Complete the emergency
        completion_report = EmergencyCompletionReport(
            request_id=request_id,
            vehicle_id="AMB001",
            actual_travel_time_s=45.5,
            red_signals_encountered=0,
            route_edges_traversed=["edge1", "edge2", "edge3"],
            safety_violations=0,
            completion_status="success"
        )

        completed = manager.complete_emergency(request_id, completion_report, current_sim_time_s=50.0)
        assert completed.status == EmergencyStatus.COMPLETED

        # Verify it moved to completed
        assert request_id in manager.completed_requests

    def test_get_statistics(self, manager, sample_request):
        """Test statistics generation."""
        # Create a few requests
        for i in range(2):
            req = sample_request.model_copy(update={"vehicle_id": f"AMB{i:03d}"})
            manager.create_emergency_request(req, current_sim_time_s=0.0)

        stats = manager.get_statistics()

        assert stats["total_requests"] >= 2
        assert stats["active_corridors"] >= 0
        assert stats["max_concurrent_corridors"] > 0


class TestEmergencyValidation:
    """Test safety constraints for emergencies."""

    def test_request_missing_required_fields(self):
        """Test that requests with missing fields are rejected."""
        from pydantic_core import ValidationError as PydanticValidationError
        with pytest.raises(PydanticValidationError):
            EmergencyRequest(
                vehicle_id="AMB001",
                # Missing required fields
            )

    def test_request_invalid_severity(self):
        """Test severity levels."""
        # Valid severity should work
        req = EmergencyRequest(
            vehicle_id="AMB001",
            origin_junction="J1",
            destination_junction="J5",
            vehicle_type=EmergencyType.AMBULANCE,
            severity=EmergencySeverity.CRITICAL,
            requester_id="USER001"
        )
        assert req.severity == EmergencySeverity.CRITICAL
        assert req.severity.value == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
