"""
UATMMS Phase 9: Data Serializers
Convert database objects to JSON-serializable format for dashboard.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.auth.firebase_auth import FirebaseAuthContext
from backend.app.db.models import (
    Network, Intersection, RoadSegment, SignalEvent,
    MetricSnapshot, Incident, EmergencyRequest,
    IncidentType, EmergencyRequestType
)


# ============================================================================
# Network Topology Serialization
# ============================================================================

def serialize_network_state(db: Session, auth_context: Optional[FirebaseAuthContext] = None) -> Dict[str, Any]:
    """
    Serialize network topology and current signal state.
    
    Args:
        db: Database session
        auth_context: Optional auth context for filtering
    
    Returns:
        Dictionary with network, intersections, and road segments
    """
    networks = db.query(Network).all()
    
    result = {
        "networks": [],
        "total_junctions": 0,
        "total_segments": 0
    }
    
    for network in networks:
        intersections = db.query(Intersection).filter(
            Intersection.network_id == network.id
        ).all()
        
        segments = db.query(RoadSegment).filter(
            RoadSegment.network_id == network.id
        ).all()
        
        # Get latest signal state for each intersection
        signal_states = {}
        for intersection in intersections:
            latest_event = db.query(SignalEvent).filter(
                SignalEvent.intersection_id == intersection.id
            ).order_by(SignalEvent.timestamp.desc()).first()
            
            signal_states[intersection.id] = {
                "phase": latest_event.new_phase if latest_event else 0,
                "duration": latest_event.duration_seconds if latest_event else 0,
                "timestamp": latest_event.timestamp.isoformat() if latest_event else None
            }
        
        network_data = {
            "id": network.id,
            "name": network.name,
            "junctions": [
                {
                    "id": j.id,
                    "name": j.name,
                    "latitude": j.latitude,
                    "longitude": j.longitude,
                    "signal_state": signal_states.get(j.id, {"phase": 0, "duration": 0, "timestamp": None})
                }
                for j in intersections
            ],
            "segments": [
                {
                    "id": s.id,
                    "from": s.from_junction_id,
                    "to": s.to_junction_id,
                    "lanes": s.lanes,
                    "length_m": s.length_m
                }
                for s in segments
            ]
        }
        
        result["networks"].append(network_data)
        result["total_junctions"] += len(intersections)
        result["total_segments"] += len(segments)
    
    return result


# ============================================================================
# Traffic Metrics Serialization
# ============================================================================

def serialize_traffic_metrics(db: Session, auth_context: Optional[FirebaseAuthContext] = None) -> Dict[str, Any]:
    """
    Serialize traffic metrics aggregated by intersection.
    
    Args:
        db: Database session
        auth_context: Optional auth context
    
    Returns:
        Dictionary with traffic metrics
    """
    metrics = db.query(MetricSnapshot).all()
    
    # Aggregate by intersection
    by_intersection = {}
    
    for metric in metrics:
        intersection_id = metric.intersection_id
        
        if intersection_id not in by_intersection:
            by_intersection[intersection_id] = []
        
        by_intersection[intersection_id].append({
            "waiting_time": metric.avg_waiting_time_s,
            "queue_length": metric.avg_queue_length,
            "throughput_vph": metric.throughput_vph,
            "occupancy_rate": metric.occupancy_rate,
            "timestamp": metric.timestamp.isoformat()
        })
    
    return {
        "metrics": [
            {
                "intersection_id": intersection_id,
                "latest": metrics_list[-1] if metrics_list else None,
                "history": metrics_list[-10:]  # Last 10 metrics
            }
            for intersection_id, metrics_list in by_intersection.items()
        ],
        "total_intersections": len(by_intersection),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Incident Serialization
# ============================================================================

def serialize_incidents(db: Session, auth_context: Optional[FirebaseAuthContext] = None) -> Dict[str, Any]:
    """
    Serialize incidents with filtering based on auth context.
    
    Args:
        db: Database session
        auth_context: Optional auth context for filtering
    
    Returns:
        Dictionary with incidents
    """
    incidents = db.query(Incident).all()
    
    # Filter by auth context if provided
    if auth_context:
        # Police can see all, public can only see verified
        if not any(role in ["admin", "police"] for role in auth_context.roles):
            incidents = [i for i in incidents if i.status == "verified"]
    
    result = {
        "incidents": [],
        "by_status": {
            "reported": 0,
            "verified": 0,
            "resolved": 0
        },
        "by_severity": {
            1: 0, 2: 0, 3: 0, 4: 0, 5: 0
        }
    }
    
    for incident in incidents:
        incident_data = {
            "id": incident.id,
            "type": incident.incident_type.value,
            "severity": incident.severity,
            "status": incident.status,
            "description": incident.description,
            "network_id": incident.network_id,
            "reported_at": incident.reported_at.isoformat(),
            "verified_at": incident.verified_at.isoformat() if incident.verified_at else None
        }
        
        result["incidents"].append(incident_data)
        result["by_status"][incident.status] += 1
        result["by_severity"][incident.severity] += 1
    
    return result


# ============================================================================
# Emergency Request Serialization
# ============================================================================

def serialize_emergencies(db: Session, auth_context: Optional[FirebaseAuthContext] = None) -> Dict[str, Any]:
    """
    Serialize emergency requests with filtering based on auth context.
    
    Args:
        db: Database session
        auth_context: Optional auth context for filtering
    
    Returns:
        Dictionary with emergency requests
    """
    emergencies = db.query(EmergencyRequest).all()
    
    # Filter by auth context if provided
    if auth_context:
        # Emergency services can see all
        # Public can only see active emergencies
        if not any(role in ["admin", "operator", "ambulance", "fire", "police"] for role in auth_context.roles):
            emergencies = [e for e in emergencies if e.status == "active"]
    
    result = {
        "emergencies": [],
        "by_type": {
            "ambulance": 0,
            "fire": 0,
            "police": 0
        },
        "by_status": {
            "pending": 0,
            "approved": 0,
            "active": 0,
            "completed": 0,
            "cancelled": 0
        }
    }
    
    for emergency in emergencies:
        emergency_data = {
            "id": emergency.id,
            "type": emergency.request_type.value,
            "status": emergency.status,
            "origin": {
                "id": emergency.origin_junction_id,
                "destination_id": emergency.destination_junction_id
            },
            "network_id": emergency.network_id,
            "submitted_at": emergency.submitted_at.isoformat(),
            "activated_at": emergency.activated_at.isoformat() if emergency.activated_at else None,
            "arrived_at": emergency.arrived_at.isoformat() if emergency.arrived_at else None,
            "corridor": emergency.assigned_corridor if emergency.assigned_corridor else None
        }
        
        result["emergencies"].append(emergency_data)
        result["by_type"][emergency.request_type.value] += 1
        result["by_status"][emergency.status] += 1
    
    return result


# ============================================================================
# Dashboard Summary Serialization
# ============================================================================

def serialize_dashboard_summary(db: Session, auth_context: Optional[FirebaseAuthContext] = None) -> Dict[str, Any]:
    """
    Serialize complete dashboard summary with all key metrics.
    
    Args:
        db: Database session
        auth_context: Optional auth context
    
    Returns:
        Complete dashboard state
    """
    return {
        "network": serialize_network_state(db, auth_context),
        "metrics": serialize_traffic_metrics(db, auth_context),
        "incidents": serialize_incidents(db, auth_context),
        "emergencies": serialize_emergencies(db, auth_context),
        "timestamp": datetime.utcnow().isoformat(),
        "user": auth_context.user.email if auth_context else "anonymous",
        "roles": auth_context.roles if auth_context else []
    }


# ============================================================================
# Delta Encoding (for bandwidth optimization)
# ============================================================================

def create_delta_update(old_state: Dict[str, Any], new_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a delta (only changes) between old and new state.
    
    Args:
        old_state: Previous state
        new_state: New state
    
    Returns:
        Dictionary containing only changed fields
    """
    delta = {
        "timestamp": new_state.get("timestamp"),
        "changes": {}
    }
    
    # Compare each field
    for key in new_state:
        if key not in old_state or old_state[key] != new_state[key]:
            delta["changes"][key] = new_state[key]
    
    return delta
