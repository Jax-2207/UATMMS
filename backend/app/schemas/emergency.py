from typing import List, Optional
from pydantic import BaseModel, Field


class EmergencyRequest(BaseModel):
    vehicle_id: str
    vehicle_type: str = Field(default="ambulance", description="ambulance, fire_brigade, police")
    origin_edge_id: str
    destination_edge_id: str
    urgency_level: int = Field(default=1, ge=1, le=5, description="1 is highest urgency")
    notes: Optional[str] = None


class GreenCorridorResponse(BaseModel):
    request_id: str
    vehicle_id: str
    status: str = Field(description="scheduled, active, completed, rejected")
    assigned_route: List[str]
    estimated_travel_time_s: float
    affected_junctions: List[str]
    safety_approved: bool
    rejection_reason: Optional[str] = None
