"""
UATMMS Incidents API Endpoints
REST endpoints for incident reporting, verification, and management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.app.schemas.incident import (
    IncidentCreate, IncidentResponse, IncidentStatusUpdate,
    IncidentHistoryResponse
)
from backend.app.incidents.manager import incident_manager
from backend.app.core.logging import logger
from backend.app.core.errors import ValidationError

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


@router.post("", response_model=IncidentResponse)
async def create_incident(req: IncidentCreate) -> IncidentResponse:
    """
    Report a new incident.

    Can be submitted by:
    - Automated detectors (low confidence)
    - Manual user reports (medium confidence)
    - Police/operator verification (high confidence)

    Low-confidence incidents require verification before activation.

    Args:
        req: Incident creation request

    Returns:
        IncidentResponse with assigned incident ID and status

    Raises:
        HTTPException: If incident parameters invalid
    """
    try:
        from backend.app.simulation.manager import simulation_manager
        current_sim_time = simulation_manager.get_current_time()

        response = incident_manager.create_incident(req, current_sim_time)
        logger.info(
            f"[API] Incident created: {response.incident_id} ({req.incident_type.value}) "
            f"on {req.location_edge_id} (confidence={req.confidence:.2f})"
        )
        return response

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Incident creation failed: {e}")
        raise HTTPException(status_code=500, detail="Incident creation failed")


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str) -> IncidentResponse:
    """
    Get incident details and current status.

    Args:
        incident_id: Incident ID

    Returns:
        IncidentResponse with current status and impact metrics

    Raises:
        HTTPException 404: If incident not found
    """
    response = incident_manager.get_incident(incident_id)

    if not response:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    return response


@router.post("/{incident_id}/verify", response_model=IncidentResponse)
async def verify_incident(
    incident_id: str,
    verifier_id: str
) -> IncidentResponse:
    """
    Verify an unverified incident (police/operator action).

    Activates the incident if it was previously only detected but not verified.

    Args:
        incident_id: Incident to verify
        verifier_id: User ID of verifier (must be authorized)

    Returns:
        Updated IncidentResponse with ACTIVE or VERIFIED status

    Raises:
        HTTPException: If incident not found or already in wrong state
    """
    try:
        from backend.app.simulation.manager import simulation_manager
        current_sim_time = simulation_manager.get_current_time()

        response = incident_manager.verify_incident(incident_id, verifier_id, current_sim_time)
        logger.info(f"[API] Incident {incident_id} verified by {verifier_id}")
        return response

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Incident verification failed: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")


@router.put("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: str,
    update: IncidentStatusUpdate
) -> IncidentResponse:
    """
    Update incident status (e.g., mark as resolved).

    Used to track incident lifecycle and clear capacity penalties.

    Args:
        incident_id: Incident to update
        update: Status update with new state

    Returns:
        Updated IncidentResponse

    Raises:
        HTTPException: If incident not found
    """
    try:
        from backend.app.simulation.manager import simulation_manager
        current_sim_time = simulation_manager.get_current_time()

        response = incident_manager.update_incident_status(update, current_sim_time)
        logger.info(f"[API] Incident {incident_id} status updated to {update.new_status.value}")
        return response

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Incident status update failed: {e}")
        raise HTTPException(status_code=500, detail="Update failed")


@router.get("/active", response_model=List[IncidentResponse])
async def get_active_incidents() -> List[IncidentResponse]:
    """
    Get all currently active incidents.

    Used by dashboard to show traffic impediments and alerts.

    Returns:
        List of active IncidentResponse objects
    """
    return incident_manager.get_active_incidents()


@router.get("/history", response_model=List[IncidentHistoryResponse])
async def get_incident_history(limit: int = 20) -> List[IncidentHistoryResponse]:
    """
    Get historical record of resolved incidents.

    Useful for post-incident analysis and metrics.

    Args:
        limit: Maximum number of historical incidents to return (default: 20)

    Returns:
        List of resolved IncidentHistoryResponse objects
    """
    return incident_manager.get_incident_history(limit)


@router.get("/stats", response_model=dict)
async def get_incident_statistics() -> dict:
    """
    Get incident system statistics.

    Returns:
        Dictionary with active incident count and historical metrics
    """
    return {
        "active_incidents": incident_manager.get_active_incident_count(),
        "total_incidents": len(incident_manager.incidents),
        "resolved_incidents": len(incident_manager.resolved_incidents)
    }
