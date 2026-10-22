"""
Unit tests for incident management and detection.
"""

import pytest
from backend.app.schemas.incident import (
    IncidentType, IncidentSeverity, IncidentStatus, IncidentSource,
    IncidentCreate
)
from backend.app.incidents.manager import IncidentManager
from backend.app.core.errors import ValidationError


class TestIncidentCreation:
    """Test incident creation and validation."""

    @pytest.fixture
    def manager(self):
        return IncidentManager()

    @pytest.fixture
    def sample_incident(self):
        return IncidentCreate(
            incident_type=IncidentType.BLOCKED_LANE,
            severity=IncidentSeverity.HIGH,
            location_edge_id="edge_42",
            capacity_reduction_pct=50.0,
            source=IncidentSource.DETECTOR,
            confidence=0.95
        )

    def test_create_incident_basic(self, manager, sample_incident):
        """Test basic incident creation."""
        response = manager.create_incident(sample_incident, current_sim_time_s=10.0)

        assert response.incident_id is not None
        assert response.location_edge_id == "edge_42"
        assert response.severity == IncidentSeverity.HIGH
        # High confidence should auto-activate
        assert response.status == IncidentStatus.ACTIVE

    def test_create_incident_low_confidence(self, manager):
        """Test that low-confidence incidents require verification."""
        incident = IncidentCreate(
            incident_type=IncidentType.ANIMAL_CROSSING,
            severity=IncidentSeverity.LOW,
            location_edge_id="edge_1",
            capacity_reduction_pct=30.0,
            source=IncidentSource.DETECTOR,
            confidence=0.5  # Low confidence
        )

        response = manager.create_incident(incident, current_sim_time_s=10.0)

        # Should require verification before activation
        assert response.status == IncidentStatus.UNVERIFIED

    def test_create_incident_invalid_capacity(self, manager):
        """Test that invalid capacity reduction is rejected at Pydantic validation."""
        from pydantic_core import ValidationError as PydanticValidationError
        
        # Pydantic should reject this at object creation
        with pytest.raises(PydanticValidationError):
            incident = IncidentCreate(
                incident_type=IncidentType.ACCIDENT,
                severity=IncidentSeverity.CRITICAL,
                location_edge_id="edge_99",
                capacity_reduction_pct=150.0,  # Invalid: > 100%
                source=IncidentSource.USER_REPORT,
                confidence=0.8
            )

    def test_create_incident_invalid_confidence(self, manager):
        """Test that invalid confidence is rejected at Pydantic validation."""
        from pydantic_core import ValidationError as PydanticValidationError
        
        # Pydantic should reject this at object creation
        with pytest.raises(PydanticValidationError):
            incident = IncidentCreate(
                incident_type=IncidentType.ROADWORK,
                severity=IncidentSeverity.MEDIUM,
                location_edge_id="edge_5",
                capacity_reduction_pct=40.0,
                source=IncidentSource.USER_REPORT,
                confidence=1.5  # Invalid: > 1.0
            )


class TestIncidentVerification:
    """Test incident verification workflow."""

    @pytest.fixture
    def manager(self):
        return IncidentManager()

    def test_verify_low_confidence_incident(self, manager):
        """Test verifying an unverified incident."""
        incident = IncidentCreate(
            incident_type=IncidentType.ACCIDENT,
            severity=IncidentSeverity.HIGH,
            location_edge_id="edge_10",
            capacity_reduction_pct=70.0,
            source=IncidentSource.DETECTOR,
            confidence=0.6
        )

        # Create unverified incident
        response = manager.create_incident(incident, current_sim_time_s=10.0)
        incident_id = response.incident_id
        assert response.status == IncidentStatus.UNVERIFIED

        # Verify it
        verified_response = manager.verify_incident(incident_id, "OFFICER001", current_sim_time_s=15.0)
        assert verified_response.status == IncidentStatus.ACTIVE

    def test_verify_nonexistent_incident(self, manager):
        """Test that verifying nonexistent incident fails."""
        with pytest.raises(ValidationError):
            manager.verify_incident("NONEXISTENT", "OFFICER001", 10.0)


class TestIncidentStatus:
    """Test incident status updates and lifecycle."""

    @pytest.fixture
    def manager(self):
        return IncidentManager()

    def test_update_incident_status(self, manager):
        """Test updating incident status."""
        incident = IncidentCreate(
            incident_type=IncidentType.BLOCKED_LANE,
            severity=IncidentSeverity.MEDIUM,
            location_edge_id="edge_7",
            capacity_reduction_pct=50.0,
            source=IncidentSource.USER_REPORT,
            confidence=0.9
        )

        response = manager.create_incident(incident, current_sim_time_s=10.0)
        incident_id = response.incident_id

        # Update to recovery
        from backend.app.schemas.incident import IncidentStatusUpdate
        update = IncidentStatusUpdate(
            incident_id=incident_id,
            new_status=IncidentStatus.RECOVERY
        )

        updated = manager.update_incident_status(update, current_sim_time_s=30.0)
        assert updated.status == IncidentStatus.RECOVERY

    def test_resolve_incident(self, manager):
        """Test resolving an incident."""
        incident = IncidentCreate(
            incident_type=IncidentType.DEBRIS,
            severity=IncidentSeverity.LOW,
            location_edge_id="edge_3",
            capacity_reduction_pct=20.0,
            source=IncidentSource.DETECTOR,
            confidence=0.85
        )

        response = manager.create_incident(incident, current_sim_time_s=10.0)
        incident_id = response.incident_id
        assert incident_id in manager.active_incidents

        # Resolve it
        from backend.app.schemas.incident import IncidentStatusUpdate
        update = IncidentStatusUpdate(
            incident_id=incident_id,
            new_status=IncidentStatus.RESOLVED
        )

        resolved = manager.update_incident_status(update, current_sim_time_s=50.0)
        assert resolved.status == IncidentStatus.RESOLVED

        # Should move from active to resolved
        assert incident_id not in manager.active_incidents
        assert incident_id in manager.resolved_incidents


class TestIncidentQuerying:
    """Test incident retrieval and statistics."""

    @pytest.fixture
    def manager_with_incidents(self):
        mgr = IncidentManager()

        # Create several incidents
        for i in range(3):
            incident = IncidentCreate(
                incident_type=IncidentType.ACCIDENT if i % 2 == 0 else IncidentType.BLOCKED_LANE,
                severity=IncidentSeverity.CRITICAL if i % 2 == 0 else IncidentSeverity.HIGH,
                location_edge_id=f"edge_{i}",
                capacity_reduction_pct=50.0 + i * 10,
                source=IncidentSource.DETECTOR,
                confidence=0.8
            )
            mgr.create_incident(incident, current_sim_time_s=float(i * 5))

        return mgr

    def test_get_incident(self, manager_with_incidents):
        """Test retrieving incident by ID."""
        incident_ids = list(manager_with_incidents.incidents.keys())
        assert len(incident_ids) > 0

        incident = manager_with_incidents.get_incident(incident_ids[0])
        assert incident is not None
        assert incident.incident_id == incident_ids[0]

    def test_get_active_incidents(self, manager_with_incidents):
        """Test retrieving all active incidents."""
        active = manager_with_incidents.get_active_incidents()
        assert len(active) > 0
        assert all(inc.status == IncidentStatus.ACTIVE for inc in active)

    def test_get_incident_history(self, manager_with_incidents):
        """Test retrieving incident history."""
        # Resolve some incidents
        incident_ids = list(manager_with_incidents.incidents.keys())
        from backend.app.schemas.incident import IncidentStatusUpdate

        for incident_id in incident_ids[:2]:
            update = IncidentStatusUpdate(
                incident_id=incident_id,
                new_status=IncidentStatus.RESOLVED
            )
            manager_with_incidents.update_incident_status(update, current_sim_time_s=100.0)

        history = manager_with_incidents.get_incident_history()
        assert len(history) >= 2

    def test_incident_count(self, manager_with_incidents):
        """Test incident count statistics."""
        count = manager_with_incidents.get_active_incident_count()
        assert count >= 1


class TestIncidentTypes:
    """Test various incident types."""

    def test_all_incident_types_valid(self):
        """Test that all incident types can be created."""
        for incident_type in IncidentType:
            incident = IncidentCreate(
                incident_type=incident_type,
                severity=IncidentSeverity.MEDIUM,
                location_edge_id="edge_test",
                capacity_reduction_pct=50.0,
                source=IncidentSource.USER_REPORT,
                confidence=0.8
            )
            assert incident.incident_type == incident_type

    def test_all_severity_levels_valid(self):
        """Test that all severity levels are valid."""
        for severity in IncidentSeverity:
            incident = IncidentCreate(
                incident_type=IncidentType.ACCIDENT,
                severity=severity,
                location_edge_id="edge_test",
                capacity_reduction_pct=50.0,
                source=IncidentSource.DETECTOR,
                confidence=0.8
            )
            assert incident.severity == severity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
