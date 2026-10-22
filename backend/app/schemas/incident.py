"""
UATMMS Incident Schemas
Defines data models for traffic incidents, obstacles, and hazards.
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class IncidentType(str, Enum):
    """Classification of traffic incidents."""
    BLOCKED_LANE = "blocked_lane"
    ACCIDENT = "accident"
    ANIMAL_CROSSING = "animal_crossing"
    WRONG_WAY_VEHICLE = "wrong_way_vehicle"
    SIGNAL_FAILURE = "signal_failure"
    ROADWORK = "roadwork"
    FLOODING = "flooding"
    DEBRIS = "debris"


class IncidentSeverity(int, Enum):
    """Impact severity on traffic."""
    CRITICAL = 5   # Complete closure, major spillback
    HIGH = 4       # Significant capacity reduction
    MEDIUM = 3     # Moderate impact
    LOW = 2        # Minor impact
    INFO = 1       # Informational only


class IncidentSource(str, Enum):
    """Where incident information originated."""
    SIMULATION = "simulation"      # Injected by test scenario
    DETECTOR = "detector"          # Automated computer vision / sensor
    USER_REPORT = "user_report"    # Manual report from app
    POLICE = "police"              # Police verification/report


class IncidentStatus(str, Enum):
    """Incident lifecycle."""
    DETECTED = "detected"        # Initially observed
    UNVERIFIED = "unverified"    # Needs police/operator confirmation
    VERIFIED = "verified"        # Confirmed, impact models active
    ACTIVE = "active"            # Currently blocking traffic
    RECOVERY = "recovery"        # Being cleared
    RESOLVED = "resolved"        # Completely cleared
    FALSE_ALARM = "false_alarm"  # Confirmed as no-incident


class IncidentCreate(BaseModel):
    """Incident submission."""
    incident_type: IncidentType
    severity: IncidentSeverity
    location_edge_id: str = Field(..., description="Edge ID where incident occurred")
    location_lane_id: Optional[str] = Field(None, description="Specific lane if applicable")
    duration_estimate_s: Optional[float] = Field(None, description="Expected duration in seconds")
    capacity_reduction_pct: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="% capacity reduction (0-100%)"
    )
    source: IncidentSource
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Detection confidence (0.0-1.0)"
    )
    reporter_id: Optional[str] = Field(None, description="User ID if manual report")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class IncidentResponse(BaseModel):
    """Incident record in database."""
    incident_id: str
    incident_type: IncidentType
    severity: IncidentSeverity
    location_edge_id: str
    location_lane_id: Optional[str]
    status: IncidentStatus
    source: IncidentSource
    confidence: float
    capacity_reduction_pct: float
    created_at: datetime
    detected_at_s: float = Field(..., description="Simulation time when detected")
    resolved_at_s: Optional[float] = Field(None, description="Simulation time when resolved")
    duration_actual_s: Optional[float] = Field(None, description="Actual duration")
    affected_routes_count: int = 0
    rerouted_vehicles_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentStatusUpdate(BaseModel):
    """Update incident status."""
    incident_id: str
    new_status: IncidentStatus
    capacity_reduction_pct: Optional[float] = None
    duration_estimate_s: Optional[float] = None
    verifier_id: Optional[str] = None
    notes: Optional[str] = None


class IncidentImpactMetrics(BaseModel):
    """Measured impact of an incident."""
    incident_id: str
    edge_id: str
    baseline_travel_time_s: float = Field(..., description="Normal travel time without incident")
    incident_travel_time_s: float = Field(..., description="Travel time during incident")
    baseline_throughput_veh_h: float = Field(..., description="Normal throughput")
    incident_throughput_veh_h: float = Field(..., description="Throughput during incident")
    queue_length_increase: float = Field(..., description="Additional vehicles queued")
    routes_affected: int = Field(..., description="Number of affected routes")
    vehicles_rerouted: int = Field(..., description="Vehicles redirected away")
    recovery_time_s: float = Field(..., description="Time to return to baseline conditions")


class IncidentHistoryResponse(BaseModel):
    """Historical record of resolved incident."""
    incident_id: str
    incident_type: IncidentType
    severity: IncidentSeverity
    location_edge_id: str
    status_final: IncidentStatus
    duration_s: float
    created_at: datetime
    impact_metrics: Optional[IncidentImpactMetrics] = None
