from fastapi import APIRouter
from backend.app.schemas.simulation import (
    SimulationStateResponse,
    SimulationControlRequest
)
from backend.app.simulation.manager import simulation_manager

router = APIRouter()


@router.get("/state", response_model=SimulationStateResponse, summary="Get Current Simulation State")
async def get_simulation_state():
    return simulation_manager.get_state()


@router.post("/start", response_model=SimulationStateResponse, summary="Start Simulation Scenario")
async def start_simulation(request: SimulationControlRequest):
    return simulation_manager.start(scenario_id=request.scenario_id or "default", seed=request.seed)


@router.post("/pause", response_model=SimulationStateResponse, summary="Pause Simulation")
async def pause_simulation():
    return simulation_manager.pause()


@router.post("/resume", response_model=SimulationStateResponse, summary="Resume Simulation")
async def resume_simulation():
    return simulation_manager.resume()


@router.post("/reset", response_model=SimulationStateResponse, summary="Reset Simulation")
async def reset_simulation():
    return simulation_manager.reset()


@router.post("/step", response_model=SimulationStateResponse, summary="Advance Simulation by 1 Step")
async def step_simulation():
    return simulation_manager.step_forward()
