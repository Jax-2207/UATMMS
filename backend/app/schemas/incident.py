from typing import Optional
from pydantic import BaseModel, Field


class IncidentReport(BaseModel):
    incident_type: str = Field(description="blocked_lane, accident, animal_crossing, rash_driving, signal_failure")
    edge_id: str
    lane_index: Optional[int] = 0
    severity: int = Field(default=2, ge=1, le=5, description="1 is low, 5 is critical road blockage")
    description: Optional[str] = None
    source: str = Field(default="operator_report", description="operator_report, simulated_injection, perception_cv")


class IncidentResponse(BaseModel):
    incident_id: str
    incident_type: str
    edge_id: str
    severity: int
    status: str = Field(default="active", description="active, verifying, resolved")
    rerouting_triggered: bool
    created_at_s: float
