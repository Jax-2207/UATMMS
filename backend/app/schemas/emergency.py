"""
UATMMS Emergency Request Schemas
Defines data models for emergency vehicle requests, corridors, and status tracking.
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from datetime import datetime


class EmergencyType(str, Enum):
    """Emergency vehicle classification."""
    AMBULANCE = "ambulance"
    FIRE = "fire"
    POLICE = "police"


class EmergencySeverity(int, Enum):
    """Emergency priority classification."""
    CRITICAL = 1  # Life-threatening: cardiac, severe trauma, respiratory failure
    HIGH = 2      # Urgent: major accidents, fires, non-critical transfer
    MEDIUM = 3    # Standard: regular transport, non-emergency police


class EmergencyStatus(str, Enum):
    """Emergency workflow lifecycle."""
    REQUESTED = "requested"        # Initial request submitted
    ROUTE_PLANNED = "route_planned"  # Route calculated, awaiting corridor
    CORRIDOR_ACTIVE = "corridor_active"  # Green corridor being enforced
    COMPLETED = "completed"        # Vehicle reached destination
    FAILED = "failed"              # Unresolvable conflict or timeout
    CANCELLED = "cancelled"        # User-cancelled


class CorridorWindow(BaseModel):
    """Green window for a single junction on emergency route."""
    junction_id: str
    edge_id_incoming: str
    target_phase: int
    green_window_start_s: float = Field(..., description="ETA - buffer (simulation time)")
    green_window_end_s: float = Field(..., description="ETA + clearance (simulation time)")
    estimated_arrival_s: float = Field(..., description="Estimated arrival at junction")
    priority: int = Field(default=1, description="Corridor priority rank (1=highest)")


class EmergencyCorridorPlan(BaseModel):
    """Complete corridor plan for an emergency vehicle."""
    request_id: str
    vehicle_id: str
    route_edges: List[str] = Field(..., description="Ordered list of edge IDs from origin to destination")
    route_junctions: List[str] = Field(..., description="Ordered list of junction IDs along route")
    corridor_windows: List[CorridorWindow]
    total_estimated_travel_time_s: float
    created_at_s: float = Field(..., description="Simulation time when corridor was planned")


class EmergencyRequest(BaseModel):
    """Emergency request submission."""
    vehicle_id: str = Field(..., description="Unique vehicle identifier")
    origin_junction: str = Field(..., description="Starting junction ID")
    destination_junction: str = Field(..., description="Destination junction ID")
    vehicle_type: EmergencyType
    severity: EmergencySeverity
    requester_id: str = Field(..., description="User ID requesting the emergency")
    metadata: dict = Field(default_factory=dict, description="Additional context (e.g., hospital code)")


class EmergencyRequestResponse(BaseModel):
    """Acknowledgment of emergency request."""
    request_id: str
    vehicle_id: str
    status: EmergencyStatus
    corridor_plan: Optional[EmergencyCorridorPlan] = None
    created_at: datetime
    message: str


class EmergencyStatusUpdate(BaseModel):
    """Status update for tracking emergency progress."""
    request_id: str
    vehicle_id: str
    status: EmergencyStatus
    current_junction_id: Optional[str] = None
    current_simulation_time_s: float
    red_signals_encountered: int = 0
    travel_time_so_far_s: float = 0.0
    estimated_arrival_s: Optional[float] = None


class EmergencyCompletionReport(BaseModel):
    """Final report after emergency passage."""
    request_id: str
    vehicle_id: str
    actual_travel_time_s: float
    red_signals_encountered: int
    route_edges_traversed: List[str]
    safety_violations: int
    completion_status: str  # "success", "timeout", "conflict", "aborted"
    notes: Optional[str] = None
