"""
UATMMS Incident Manager
Handles incident lifecycle, impact modeling, and automated response.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from backend.app.schemas.incident import (
    IncidentType, IncidentSeverity, IncidentStatus, IncidentSource,
    IncidentCreate, IncidentResponse, IncidentStatusUpdate,
    IncidentImpactMetrics, IncidentHistoryResponse
)
from backend.app.core.logging import logger
from backend.app.core.errors import ValidationError
import uuid


class Incident:
    """Internal incident tracking object."""

    def __init__(self, incident_id: str, create_req: IncidentCreate, sim_time_s: float):
        self.incident_id = incident_id
        self.incident_type = create_req.incident_type
        self.severity = create_req.severity
        self.location_edge_id = create_req.location_edge_id
        self.location_lane_id = create_req.location_lane_id
        self.status = IncidentStatus.DETECTED
        self.source = create_req.source
        self.confidence = create_req.confidence
        self.capacity_reduction_pct = create_req.capacity_reduction_pct
        self.created_at = datetime.now()
        self.detected_at_s = sim_time_s
        self.resolved_at_s: Optional[float] = None
        self.reporter_id = create_req.reporter_id
        self.metadata = create_req.metadata
        self.duration_estimate_s = create_req.duration_estimate_s
        self.affected_routes: List[str] = []  # Route IDs affected by this incident
        self.rerouted_vehicles: List[str] = []  # Vehicle IDs that were rerouted
        self.impact_metrics: Optional[IncidentImpactMetrics] = None

    def to_response(self) -> IncidentResponse:
        """Convert to API response object."""
        return IncidentResponse(
            incident_id=self.incident_id,
            incident_type=self.incident_type,
            severity=self.severity,
            location_edge_id=self.location_edge_id,
            location_lane_id=self.location_lane_id,
            status=self.status,
            source=self.source,
            confidence=self.confidence,
            capacity_reduction_pct=self.capacity_reduction_pct,
            created_at=self.created_at,
            detected_at_s=self.detected_at_s,
            resolved_at_s=self.resolved_at_s,
            duration_actual_s=(self.resolved_at_s - self.detected_at_s) if self.resolved_at_s else None,
            affected_routes_count=len(self.affected_routes),
            rerouted_vehicles_count=len(self.rerouted_vehicles),
            metadata=self.metadata
        )


class IncidentManager:
    """
    Manages incident lifecycle and automated response:
    1. Detection / reporting
    2. Verification (if needed)
    3. Impact modeling (capacity reduction, route updates)
    4. Resolution and recovery
    """

    def __init__(self):
        self.incidents: Dict[str, Incident] = {}  # incident_id -> Incident
        self.active_incidents: Dict[str, Incident] = {}  # Currently active incidents
        self.resolved_incidents: Dict[str, Incident] = {}  # History of resolved incidents
        self.edge_base_capacity: Dict[str, float] = {}  # Normal edge capacity (vehicles/hour)

    def create_incident(
        self,
        create_req: IncidentCreate,
        current_sim_time_s: float
    ) -> IncidentResponse:
        """
        Create and register a new incident.

        Args:
            create_req: Incident creation request
            current_sim_time_s: Current simulation time

        Returns:
            IncidentResponse with incident ID and initial status

        Raises:
            ValidationError: If incident parameters invalid
        """
        # Validate
        if create_req.capacity_reduction_pct < 0 or create_req.capacity_reduction_pct > 100:
            raise ValidationError("capacity_reduction_pct must be 0-100")

        if create_req.confidence < 0 or create_req.confidence > 1.0:
            raise ValidationError("confidence must be 0.0-1.0")

        # Create incident
        incident_id = str(uuid.uuid4())[:8]
        incident = Incident(incident_id, create_req, current_sim_time_s)

        self.incidents[incident_id] = incident

        # If high confidence, immediately activate
        if create_req.confidence >= 0.8:
            self._activate_incident(incident_id, current_sim_time_s)
        else:
            # Otherwise mark as needing verification
            incident.status = IncidentStatus.UNVERIFIED

        logger.info(
            f"[IncidentManager] Created incident {incident_id}: {incident.incident_type.value} "
            f"on {incident.location_edge_id} (severity={incident.severity.value})"
        )

        return incident.to_response()

    def _activate_incident(self, incident_id: str, current_sim_time_s: float):
        """Activate incident: update edge costs and trigger rerouting."""
        if incident_id not in self.incidents:
            return

        incident = self.incidents[incident_id]
        incident.status = IncidentStatus.ACTIVE
        self.active_incidents[incident_id] = incident

        # Step 1: Update edge cost in dynamic cost model
        self._update_edge_capacity(incident, current_sim_time_s)

        # Step 2: Trigger rerouting for affected routes
        affected_routes = self._trigger_rerouting(incident, current_sim_time_s)
        incident.affected_routes = affected_routes

        logger.info(
            f"[IncidentManager] Activated incident {incident_id}: "
            f"updated {incident.location_edge_id}, affected {len(affected_routes)} routes"
        )

    def _update_edge_capacity(self, incident: Incident, current_sim_time_s: float):
        """Update edge capacity in dynamic cost model to reflect incident impact."""
        try:
            from backend.app.routing.cost_model import dynamic_cost_model

            # Calculate reduced capacity
            reduction_factor = 1.0 - (incident.capacity_reduction_pct / 100.0)

            # Update the edge condition with incident flag and cost penalty
            # This makes the edge less attractive for routing
            dynamic_cost_model.update_condition(
                edge_id=incident.location_edge_id,
                vehicle_count=0,
                mean_speed=1.0,  # Severely reduced speed due to incident
                queue_length=999,  # Indicate blocked/severely congested
                occupancy=100.0,  # Full occupancy
                incident_severity=incident.severity.value,
                incident_flag=True
            )

            logger.debug(
                f"[IncidentManager] Updated edge {incident.location_edge_id}: "
                f"capacity reduction {incident.capacity_reduction_pct}%"
            )
        except Exception as e:
            logger.error(f"Failed to update edge capacity: {e}")

    def _trigger_rerouting(self, incident: Incident, current_sim_time_s: float) -> List[str]:
        """
        Identify routes affected by incident and trigger rerouting.
        In full implementation, this would notify routing module to recalculate routes.

        Returns:
            List of affected route IDs (placeholder for testing)
        """
        # In production: query routing module for routes using incident edge
        affected_routes = []

        # Placeholder: simulate finding 2-5 routes that use this edge
        for i in range(2):
            affected_routes.append(f"route_{incident.location_edge_id}_{i}")

        logger.info(
            f"[IncidentManager] Identified {len(affected_routes)} affected routes for incident {incident.incident_id}"
        )

        return affected_routes

    def verify_incident(
        self,
        incident_id: str,
        verifier_id: str,
        current_sim_time_s: float
    ) -> IncidentResponse:
        """
        Verify an unverified incident (typically by police or operator).

        Args:
            incident_id: Incident to verify
            verifier_id: User ID of verifier
            current_sim_time_s: Current simulation time

        Returns:
            Updated IncidentResponse

        Raises:
            ValidationError: If incident not found or already verified
        """
        if incident_id not in self.incidents:
            raise ValidationError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]

        if incident.status != IncidentStatus.UNVERIFIED:
            raise ValidationError(f"Incident {incident_id} is already in {incident.status.value} state")

        # Activate the incident
        self._activate_incident(incident_id, current_sim_time_s)

        logger.info(f"[IncidentManager] Incident {incident_id} verified by {verifier_id}")

        return incident.to_response()

    def update_incident_status(
        self,
        update_req: IncidentStatusUpdate,
        current_sim_time_s: float
    ) -> IncidentResponse:
        """Update incident status manually."""
        incident_id = update_req.incident_id

        if incident_id not in self.incidents:
            raise ValidationError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]

        # Update status
        incident.status = update_req.new_status

        # Update capacity if provided
        if update_req.capacity_reduction_pct is not None:
            incident.capacity_reduction_pct = update_req.capacity_reduction_pct

        # If resolving, clean up
        if update_req.new_status == IncidentStatus.RESOLVED:
            self._resolve_incident(incident_id, current_sim_time_s)

        logger.info(f"[IncidentManager] Updated incident {incident_id} to {update_req.new_status.value}")

        return incident.to_response()

    def _resolve_incident(self, incident_id: str, current_sim_time_s: float):
        """Resolve incident: clear edge penalty, move to history."""
        if incident_id not in self.incidents:
            return

        incident = self.incidents[incident_id]
        incident.resolved_at_s = current_sim_time_s

        # Restore normal edge capacity
        try:
            from backend.app.routing.cost_model import dynamic_cost_model

            dynamic_cost_model.update_condition(
                edge_id=incident.location_edge_id,
                vehicle_count=0,
                mean_speed=15.0,  # Restore to normal
                queue_length=0,
                occupancy=0.0,
                incident_severity=0,
                incident_flag=False
            )

            logger.info(f"[IncidentManager] Resolved incident {incident_id}: edge capacity restored")
        except Exception as e:
            logger.error(f"Failed to restore edge capacity: {e}")

        # Move from active to resolved
        if incident_id in self.active_incidents:
            del self.active_incidents[incident_id]

        self.resolved_incidents[incident_id] = incident

    def get_incident(self, incident_id: str) -> Optional[IncidentResponse]:
        """Get incident by ID."""
        if incident_id not in self.incidents:
            return None

        return self.incidents[incident_id].to_response()

    def get_active_incidents(self) -> List[IncidentResponse]:
        """Get all currently active incidents."""
        return [incident.to_response() for incident in self.active_incidents.values()]

    def get_incident_history(self, limit: int = 20) -> List[IncidentHistoryResponse]:
        """Get resolved incidents history."""
        history = []
        for incident in list(self.resolved_incidents.values())[-limit:]:
            history.append(IncidentHistoryResponse(
                incident_id=incident.incident_id,
                incident_type=incident.incident_type,
                severity=incident.severity,
                location_edge_id=incident.location_edge_id,
                status_final=incident.status,
                duration_s=(incident.resolved_at_s - incident.detected_at_s) if incident.resolved_at_s else 0.0,
                created_at=incident.created_at,
                impact_metrics=incident.impact_metrics
            ))

        return history

    def get_active_incident_count(self) -> int:
        """Get count of active incidents."""
        return len(self.active_incidents)


# Global instance
incident_manager = IncidentManager()
