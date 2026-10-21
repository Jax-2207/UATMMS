from typing import List, Optional
from pydantic import BaseModel, Field


class RoutePlanRequest(BaseModel):
    origin_edge_id: str
    destination_edge_id: str
    vehicle_type: Optional[str] = "passenger_car"
    algorithm: Optional[str] = Field(default="astar", description="astar or dijkstra")
    avoid_incidents: bool = True


class RoutePlanResponse(BaseModel):
    route_id: str
    origin_edge_id: str
    destination_edge_id: str
    algorithm_used: str
    edge_sequence: List[str]
    junction_sequence: List[str]
    total_distance_m: float
    estimated_travel_time_s: float
    nodes_expanded: int = 0
    incident_detour_active: bool = False


class RerouteEvaluationRequest(BaseModel):
    current_route: List[str]
    current_edge_id: str
    destination_edge_id: str
    hysteresis_threshold: float = Field(default=0.15, description="Min relative time saving to trigger reroute")


class RerouteEvaluationResponse(BaseModel):
    should_reroute: bool
    current_remaining_time_s: float
    candidate_remaining_time_s: float
    relative_time_saved_ratio: float
    recommended_route: List[str]
    reason: str
