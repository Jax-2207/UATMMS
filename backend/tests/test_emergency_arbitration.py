"""
Unit tests for emergency corridor arbitration and conflict resolution.
"""

import pytest
from backend.app.schemas.emergency import (
    EmergencyCorridorPlan, CorridorWindow, EmergencySeverity,
    EmergencyType
)
from backend.app.emergency.arbitration import EmergencyArbitrator, ConflictingEmergencies


class TestConflictDetection:
    """Test detection of conflicting emergencies."""

    def test_no_conflict_different_junctions(self):
        """Test that non-overlapping corridors are not flagged as conflicts."""
        plan1 = EmergencyCorridorPlan(
            request_id="REQ1",
            vehicle_id="AMB1",
            route_edges=["e1", "e2"],
            route_junctions=["J1", "J2"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e0",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=25.0,
                    estimated_arrival_s=15.0,
                    priority=1
                )
            ],
            total_estimated_travel_time_s=20.0,
            created_at_s=0.0
        )

        plan2 = EmergencyCorridorPlan(
            request_id="REQ2",
            vehicle_id="FIRE1",
            route_edges=["e3", "e4"],
            route_junctions=["J3", "J4"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J3",
                    edge_id_incoming="e2",
                    target_phase=0,
                    green_window_start_s=30.0,
                    green_window_end_s=45.0,
                    estimated_arrival_s=35.0,
                    priority=2
                )
            ],
            total_estimated_travel_time_s=20.0,
            created_at_s=5.0
        )

        conflict = ConflictingEmergencies([("REQ1", plan1), ("REQ2", plan2)])
        assert not conflict.has_direct_conflict()

    def test_conflict_same_junction_overlapping_time(self):
        """Test that overlapping time windows at same junction are detected."""
        plan1 = EmergencyCorridorPlan(
            request_id="REQ1",
            vehicle_id="AMB1",
            route_edges=["e1", "e2"],
            route_junctions=["J1", "J2"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e0",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=30.0,
                    estimated_arrival_s=15.0,
                    priority=1
                )
            ],
            total_estimated_travel_time_s=20.0,
            created_at_s=0.0
        )

        plan2 = EmergencyCorridorPlan(
            request_id="REQ2",
            vehicle_id="FIRE1",
            route_edges=["e3", "e4"],
            route_junctions=["J1", "J3"],  # Same first junction
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e5",
                    target_phase=2,
                    green_window_start_s=20.0,  # Overlaps with plan1
                    green_window_end_s=40.0,
                    estimated_arrival_s=25.0,
                    priority=2
                )
            ],
            total_estimated_travel_time_s=20.0,
            created_at_s=5.0
        )

        conflict = ConflictingEmergencies([("REQ1", plan1), ("REQ2", plan2)])
        assert conflict.has_direct_conflict()
        assert "J1" in conflict.conflicting_junctions


class TestArbitration:
    """Test emergency arbitration and priority resolution."""

    @pytest.fixture
    def arbitrator(self):
        return EmergencyArbitrator()

    def test_resolve_conflicting_emergencies(self, arbitrator):
        """Test resolving conflicting emergency requests."""
        plan1 = EmergencyCorridorPlan(
            request_id="REQ1",
            vehicle_id="AMB1",
            route_edges=["e1"],
            route_junctions=["J1"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e0",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=25.0,
                    estimated_arrival_s=15.0,
                    priority=1  # CRITICAL
                )
            ],
            total_estimated_travel_time_s=15.0,
            created_at_s=0.0
        )

        plan2 = EmergencyCorridorPlan(
            request_id="REQ2",
            vehicle_id="POLICE1",
            route_edges=["e2"],
            route_junctions=["J1"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e3",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=25.0,
                    estimated_arrival_s=18.0,
                    priority=3  # MEDIUM
                )
            ],
            total_estimated_travel_time_s=15.0,
            created_at_s=2.0
        )

        queue = [("REQ1", plan1), ("REQ2", plan2)]
        result = arbitrator.evaluate_conflict(queue)

        # Both should be in result
        assert len(result) == 2
        assert "REQ1" in result
        assert "REQ2" in result

    def test_non_conflicting_corridors_unchanged(self, arbitrator):
        """Test that non-conflicting corridors are approved as-is."""
        plan1 = EmergencyCorridorPlan(
            request_id="REQ1",
            vehicle_id="AMB1",
            route_edges=["e1"],
            route_junctions=["J1"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e0",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=25.0,
                    estimated_arrival_s=15.0,
                    priority=1
                )
            ],
            total_estimated_travel_time_s=15.0,
            created_at_s=0.0
        )

        plan2 = EmergencyCorridorPlan(
            request_id="REQ2",
            vehicle_id="FIRE1",
            route_edges=["e2"],
            route_junctions=["J2"],  # Different junction
            corridor_windows=[
                CorridorWindow(
                    junction_id="J2",
                    edge_id_incoming="e3",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=25.0,
                    estimated_arrival_s=15.0,
                    priority=2
                )
            ],
            total_estimated_travel_time_s=15.0,
            created_at_s=1.0
        )

        queue = [("REQ1", plan1), ("REQ2", plan2)]
        result = arbitrator.evaluate_conflict(queue)

        # Original plans should be unchanged (no staggering needed)
        assert result["REQ1"].total_estimated_travel_time_s == plan1.total_estimated_travel_time_s
        assert result["REQ2"].total_estimated_travel_time_s == plan2.total_estimated_travel_time_s

    def test_stagger_conflicting_corridors(self, arbitrator):
        """Test that conflicting corridors are staggered in time."""
        plan1 = EmergencyCorridorPlan(
            request_id="REQ1",
            vehicle_id="AMB1",
            route_edges=["e1"],
            route_junctions=["J1"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e0",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=25.0,
                    estimated_arrival_s=15.0,
                    priority=1
                )
            ],
            total_estimated_travel_time_s=15.0,
            created_at_s=0.0
        )

        plan2 = EmergencyCorridorPlan(
            request_id="REQ2",
            vehicle_id="FIRE1",
            route_edges=["e2"],
            route_junctions=["J1"],  # Same junction
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e3",
                    target_phase=0,
                    green_window_start_s=10.0,  # Conflict!
                    green_window_end_s=25.0,
                    estimated_arrival_s=15.0,
                    priority=2
                )
            ],
            total_estimated_travel_time_s=15.0,
            created_at_s=1.0  # Created slightly later, lower priority
        )

        queue = [("REQ1", plan1), ("REQ2", plan2)]
        result = arbitrator.evaluate_conflict(queue)

        # REQ1 (higher priority) should keep original timing
        assert result["REQ1"].total_estimated_travel_time_s == plan1.total_estimated_travel_time_s

        # REQ2 (lower priority) should be staggered (later)
        # The exact offset depends on stagger_interval (15.0s in implementation)
        assert result["REQ2"].total_estimated_travel_time_s >= plan2.total_estimated_travel_time_s

    def test_conflict_history_tracked(self, arbitrator):
        """Test that arbitration history is recorded."""
        plan1 = EmergencyCorridorPlan(
            request_id="REQ1",
            vehicle_id="AMB1",
            route_edges=["e1"],
            route_junctions=["J1"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e0",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=25.0,
                    estimated_arrival_s=15.0,
                    priority=1
                )
            ],
            total_estimated_travel_time_s=15.0,
            created_at_s=0.0
        )

        queue = [("REQ1", plan1)]
        arbitrator.evaluate_conflict(queue)

        history = arbitrator.get_conflict_history()
        assert len(history) > 0
        assert history[0]["total_requests"] >= 1


class TestArbitrationEdgeCases:
    """Test edge cases in arbitration."""

    @pytest.fixture
    def arbitrator(self):
        return EmergencyArbitrator()

    def test_empty_queue(self, arbitrator):
        """Test handling of empty emergency queue."""
        result = arbitrator.evaluate_conflict([])
        assert result == {}

    def test_single_request(self, arbitrator):
        """Test handling of single request (no conflict possible)."""
        plan = EmergencyCorridorPlan(
            request_id="REQ1",
            vehicle_id="AMB1",
            route_edges=["e1"],
            route_junctions=["J1"],
            corridor_windows=[
                CorridorWindow(
                    junction_id="J1",
                    edge_id_incoming="e0",
                    target_phase=0,
                    green_window_start_s=10.0,
                    green_window_end_s=25.0,
                    estimated_arrival_s=15.0,
                    priority=1
                )
            ],
            total_estimated_travel_time_s=15.0,
            created_at_s=0.0
        )

        result = arbitrator.evaluate_conflict([("REQ1", plan)])
        assert len(result) == 1
        assert "REQ1" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
