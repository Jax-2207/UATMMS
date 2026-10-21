"""
UATMMS Routing API Endpoints
Provides route planning (A*, Dijkstra) and dynamic reroute evaluation with hysteresis.
"""
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.routing import (
    RoutePlanRequest,
    RoutePlanResponse,
    RerouteEvaluationRequest,
    RerouteEvaluationResponse
)
from backend.app.routing.router import dynamic_router

router = APIRouter()


@router.post("/plan", response_model=RoutePlanResponse, summary="Plan optimal vehicle route")
def plan_route(request: RoutePlanRequest):
    try:
        return dynamic_router.plan_route(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing calculation failed: {str(e)}"
        )


@router.post("/evaluate", response_model=RerouteEvaluationResponse, summary="Evaluate dynamic reroute with hysteresis")
def evaluate_reroute(request: RerouteEvaluationRequest):
    try:
        return dynamic_router.evaluate_reroute(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reroute evaluation failed: {str(e)}"
        )
