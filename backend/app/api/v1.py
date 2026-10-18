from fastapi import APIRouter
from backend.app.api.endpoints import health, simulation, emergencies, incidents

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
api_router.include_router(emergencies.router, prefix="/emergencies", tags=["Emergencies"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
