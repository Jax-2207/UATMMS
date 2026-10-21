from fastapi import APIRouter
from backend.app.api.endpoints import health, simulation, emergencies, incidents, network, routing

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
api_router.include_router(network.router, prefix="/network", tags=["Network"])
api_router.include_router(emergencies.router, prefix="/emergencies", tags=["Emergencies"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(routing.router, prefix="/routes", tags=["Routing"])


