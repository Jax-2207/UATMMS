import os
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter()


@router.get("/health", summary="System Health & Module Verification")
async def health_check():
    sumo_installed = os.path.exists(settings.SUMO_HOME) or bool(os.environ.get("SUMO_HOME"))
    return {
        "status": "healthy",
        "system": "UATMMS Backend",
        "version": settings.VERSION,
        "environment": settings.UATMMS_ENV,
        "active_modules": [
            "core",
            "safety_validator",
            "simulation_manager",
            "routing_engine",
            "emergency_scheduler",
            "incident_manager"
        ],
        "sumo_detected": sumo_installed,
        "mock_auth_active": settings.MOCK_AUTH_FOR_DEV
    }
