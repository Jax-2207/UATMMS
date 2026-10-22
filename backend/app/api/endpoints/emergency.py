"""
UATMMS Emergency API Endpoints
REST endpoints for emergency corridor requests and management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from backend.app.schemas.emergency import (
    EmergencyRequest, EmergencyRequestResponse, EmergencyStatusUpdate,
    EmergencyCompletionReport, EmergencyCorridorPlan
)
from backend.app.emergency.manager import emergency_manager
from backend.app.core.logging import logger
from backend.app.core.errors import ValidationError

router = APIRouter(prefix="/api/v1/emergencies", tags=["emergency"])


@router.post("", response_model=EmergencyRequestResponse)
async def create_emergency_request(req: EmergencyRequest) -> EmergencyRequestResponse:
    """
    Submit an emergency request.

    Dispatched by authorized emergency vehicles (ambulance, fire, police).
    Backend validates identity and immediately initiates corridor planning and arbitration.

    Args:
        req: Emergency request with origin, destination, vehicle type, and severity

    Returns:
        EmergencyRequestResponse with assigned request ID and initial status

    Raises:
        HTTPException: If request invalid or system overloaded
    """
    try:
        # Get current simulation time (normally injected from simulation state)
        from backend.app.simulation.manager import simulation_manager
        current_sim_time = simulation_manager.get_current_time()

        response = emergency_manager.create_emergency_request(req, current_sim_time)
        logger.info(f"[API] Emergency request {response.request_id} created for {req.vehicle_id}")
        return response

    except ValidationError as e:
        logger.error(f"[API] Emergency request validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Emergency request creation failed: {e}")
        raise HTTPException(status_code=500, detail="Emergency request processing failed")


@router.get("/{request_id}", response_model=EmergencyRequestResponse)
async def get_emergency_status(request_id: str) -> EmergencyRequestResponse:
    """
    Get current status of an emergency request.

    Includes corridor plan, current position, and ETA at destination.

    Args:
        request_id: Emergency request ID

    Returns:
        Current EmergencyRequestResponse

    Raises:
        HTTPException 404: If request not found
    """
    response = emergency_manager.get_request_status(request_id)

    if not response:
        raise HTTPException(status_code=404, detail=f"Emergency request {request_id} not found")

    return response


@router.put("/{request_id}/status", response_model=dict)
async def update_emergency_status(
    request_id: str,
    update: EmergencyStatusUpdate
) -> dict:
    """
    Update emergency vehicle progress during transit.

    Called as vehicle progresses to track completion and metrics.

    Args:
        request_id: Emergency request ID
        update: Status update with current position and metrics

    Returns:
        Status update acknowledgment

    Raises:
        HTTPException: If update fails
    """
    try:
        from backend.app.simulation.manager import simulation_manager
        current_sim_time = simulation_manager.get_current_time()

        success, message = emergency_manager.update_emergency_status(update, current_sim_time)

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return {"status": "updated", "message": message}

    except Exception as e:
        logger.error(f"[API] Emergency status update failed: {e}")
        raise HTTPException(status_code=500, detail="Status update failed")


@router.post("/{request_id}/complete", response_model=dict)
async def complete_emergency(
    request_id: str,
    report: EmergencyCompletionReport
) -> dict:
    """
    Mark emergency as completed and record final metrics.

    Called when emergency vehicle reaches destination.

    Args:
        request_id: Emergency request ID
        report: Completion report with actual travel time, red signals, etc.

    Returns:
        Completion acknowledgment

    Raises:
        HTTPException: If completion fails
    """
    try:
        from backend.app.simulation.manager import simulation_manager
        current_sim_time = simulation_manager.get_current_time()

        response = emergency_manager.complete_emergency(request_id, report, current_sim_time)

        logger.info(
            f"[API] Emergency {request_id} completed: "
            f"{report.actual_travel_time_s:.1f}s travel time, "
            f"{report.red_signals_encountered} red signals"
        )

        return {
            "status": "completed",
            "request_id": request_id,
            "metrics": {
                "travel_time_s": report.actual_travel_time_s,
                "red_signals": report.red_signals_encountered,
                "safety_violations": report.safety_violations
            }
        }

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Emergency completion failed: {e}")
        raise HTTPException(status_code=500, detail="Completion recording failed")


@router.get("/active/corridors", response_model=List[EmergencyCorridorPlan])
async def get_active_corridors() -> List[EmergencyCorridorPlan]:
    """
    Get all currently active emergency corridors.

    Used by dashboard to visualize active emergency routes and green windows.

    Returns:
        List of active EmergencyCorridorPlan objects
    """
    corridors = emergency_manager.get_active_corridors()
    return corridors


@router.get("/stats", response_model=dict)
async def get_emergency_statistics() -> dict:
    """
    Get emergency system statistics.

    Includes request counts, active corridors, completion rates, and metrics.

    Returns:
        Dictionary of statistics
    """
    return emergency_manager.get_statistics()
