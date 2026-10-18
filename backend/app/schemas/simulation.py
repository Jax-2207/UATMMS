from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VehicleSnapshot(BaseModel):
    vehicle_id: str
    edge_id: str
    lane_index: int = 0
    position_m: float
    speed_mps: float
    vehicle_type: str = "passenger"


class JunctionSignalSnapshot(BaseModel):
    junction_id: str
    current_phase_index: int
    current_phase_name: str
    elapsed_time_s: float
    min_green_s: float
    max_green_s: float


class SimulationStateResponse(BaseModel):
    run_id: str
    status: str = Field(description="running, paused, stopped, error")
    step: int
    simulation_time_s: float
    active_vehicle_count: int
    average_speed_mps: float
    average_waiting_time_s: float
    vehicles: List[VehicleSnapshot] = []
    signals: List[JunctionSignalSnapshot] = []
    metadata: Dict[str, Any] = {}


class SimulationControlRequest(BaseModel):
    scenario_id: Optional[str] = "default_6junctions"
    step_length_s: float = 1.0
    seed: int = 42
