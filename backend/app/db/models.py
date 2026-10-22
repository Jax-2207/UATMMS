"""
UATMMS Database Models (Phase 8)
SQLAlchemy ORM models for PostgreSQL persistence layer.
Includes: users, roles, permissions, simulation data, audit logging.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    ForeignKey, Text, JSON, Enum, UniqueConstraint, Index,
    Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

# ============================================================================
# RBAC Models
# ============================================================================

# Association tables for many-to-many relationships
user_role_association = Table(
    'user_role',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True)
)

role_permission_association = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', String, ForeignKey('permissions.id'), primary_key=True)
)


class User(Base):
    """User account with Firebase integration."""
    __tablename__ = 'users'

    id = Column(String(128), primary_key=True)  # Firebase UID
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    firebase_uid = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    roles = relationship(
        'Role',
        secondary=user_role_association,
        back_populates='users'
    )
    audit_events = relationship('AuditEvent', back_populates='user')

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_firebase_uid', 'firebase_uid'),
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Role(Base):
    """Role definition (admin, operator, police, ambulance, fire, public)."""
    __tablename__ = 'roles'

    id = Column(String(50), primary_key=True)  # 'admin', 'operator', etc.
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Role hierarchy
    priority = Column(Integer, default=0, nullable=False)  # Higher = more privileged
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship(
        'User',
        secondary=user_role_association,
        back_populates='roles'
    )
    permissions = relationship(
        'Permission',
        secondary=role_permission_association,
        back_populates='roles'
    )

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    """Permission (action on resource)."""
    __tablename__ = 'permissions'

    id = Column(String(100), primary_key=True)  # 'view_signals', 'approve_corridor', etc.
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False)  # 'signal', 'corridor', 'network', etc.
    action = Column(String(50), nullable=False)  # 'view', 'modify', 'approve', etc.

    # Relationships
    roles = relationship(
        'Role',
        secondary=role_permission_association,
        back_populates='permissions'
    )

    def __repr__(self):
        return f"<Permission {self.id}>"


# ============================================================================
# Simulation & Network Models
# ============================================================================

class Network(Base):
    """Traffic network configuration."""
    __tablename__ = 'networks'

    id = Column(String(50), primary_key=True)  # 'bengaluru_core'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Network geometry
    junctions_count = Column(Integer, nullable=False)
    edges_count = Column(Integer, nullable=False)
    
    # Metadata
    osm_region = Column(String(255), nullable=True)  # 'Bangalore MG Road'
    sumo_net_file = Column(String(500), nullable=True)  # Path to .net.xml
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    junctions = relationship('Intersection', back_populates='network')
    edges = relationship('RoadSegment', back_populates='network')
    simulation_runs = relationship('SimulationRun', back_populates='network')

    def __repr__(self):
        return f"<Network {self.name}>"


class Intersection(Base):
    """Junction/intersection in network."""
    __tablename__ = 'intersections'

    id = Column(String(50), primary_key=True)  # 'J1_MG_Road'
    network_id = Column(String(50), ForeignKey('networks.id'), nullable=False)
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Signal configuration
    signal_phases = Column(Integer, default=8, nullable=False)
    min_green = Column(Float, default=10.0, nullable=False)
    max_green = Column(Float, default=90.0, nullable=False)
    yellow_time = Column(Float, default=3.0, nullable=False)
    all_red_time = Column(Float, default=2.0, nullable=False)
    
    # Metadata
    name = Column(String(255), nullable=True)
    sumo_id = Column(String(100), nullable=True, index=True)

    # Relationships
    network = relationship('Network', back_populates='junctions')
    signals = relationship('SignalEvent', back_populates='intersection')
    metrics = relationship('MetricSnapshot', back_populates='intersection')

    __table_args__ = (
        Index('idx_intersection_network', 'network_id'),
        Index('idx_intersection_sumo_id', 'sumo_id'),
    )

    def __repr__(self):
        return f"<Intersection {self.id}>"


class RoadSegment(Base):
    """Directed edge/road segment."""
    __tablename__ = 'road_segments'

    id = Column(String(100), primary_key=True)  # 'J1_to_J2'
    network_id = Column(String(50), ForeignKey('networks.id'), nullable=False)
    
    # Topology
    from_junction_id = Column(String(50), ForeignKey('intersections.id'), nullable=False)
    to_junction_id = Column(String(50), ForeignKey('intersections.id'), nullable=False)
    
    # Geometry
    lanes = Column(Integer, default=2, nullable=False)
    length_m = Column(Float, nullable=False)
    max_speed_kmh = Column(Float, default=50.0, nullable=False)
    
    # Metadata
    is_arterial = Column(Boolean, default=False, nullable=False)
    sumo_id = Column(String(100), nullable=True, index=True)

    # Relationships
    network = relationship('Network', back_populates='edges')

    __table_args__ = (
        Index('idx_segment_network', 'network_id'),
        Index('idx_segment_sumo_id', 'sumo_id'),
    )

    def __repr__(self):
        return f"<RoadSegment {self.id}>"


# ============================================================================
# Simulation Run & Model Version
# ============================================================================

class SimulationRun(Base):
    """Recorded simulation execution."""
    __tablename__ = 'simulation_runs'

    id = Column(String(50), primary_key=True)  # UUID or run_id
    network_id = Column(String(50), ForeignKey('networks.id'), nullable=False)
    
    # Scenario
    scenario_name = Column(String(255), nullable=False)
    random_seed = Column(Integer, nullable=False)
    traffic_demand = Column(String(50), nullable=False)  # 'off_peak', 'standard', 'peak'
    
    # Execution
    start_time_utc = Column(DateTime, nullable=False)
    end_time_utc = Column(DateTime, nullable=True)
    sim_steps = Column(Integer, default=0, nullable=False)
    
    # Configuration
    signal_controller = Column(String(100), nullable=False)  # 'fixed_time', 'adaptive', 'ppo'
    controller_config = Column(JSON, nullable=True)
    
    # Results
    metrics = Column(JSON, nullable=True)  # {avg_waiting, throughput, safety_violations, ...}

    # Relationships
    network = relationship('Network', back_populates='simulation_runs')

    __table_args__ = (
        Index('idx_simulation_network', 'network_id'),
    )

    def __repr__(self):
        return f"<SimulationRun {self.id}>"


class ModelVersion(Base):
    """RL model version tracking."""
    __tablename__ = 'model_versions'

    id = Column(String(50), primary_key=True)  # 'ppo_j1_v1'
    network_id = Column(String(50), ForeignKey('networks.id'), nullable=True)
    
    # Model info
    model_type = Column(String(50), nullable=False)  # 'ppo', 'dqn', 'a2c'
    junction_id = Column(String(50), nullable=True)  # Single junction training
    
    # Versioning
    version_number = Column(Integer, nullable=False)
    checkpoint_path = Column(String(500), nullable=False)
    
    # Performance metrics
    mean_reward = Column(Float, nullable=True)
    mean_waiting_time = Column(Float, nullable=True)
    safety_violations = Column(Integer, default=0, nullable=False)
    
    # Status
    is_promoted = Column(Boolean, default=False, nullable=False)
    promoted_at = Column(DateTime, nullable=True)
    promoted_by = Column(String(128), ForeignKey('users.id'), nullable=True)
    
    # Metadata
    evaluation_episodes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_model_version_network', 'network_id'),
        Index('idx_model_version_promoted', 'is_promoted'),
    )

    def __repr__(self):
        return f"<ModelVersion {self.id}>"


# ============================================================================
# Operational Models (Incidents, Emergency, Traffic Events)
# ============================================================================

class IncidentType(enum.Enum):
    """Incident classification."""
    ACCIDENT = "accident"
    CONGESTION = "congestion"
    BLOCKAGE = "blockage"
    WEATHER = "weather"
    BREAKDOWN = "breakdown"
    ANIMAL = "animal"
    OTHER = "other"


class Incident(Base):
    """Reported or detected incident."""
    __tablename__ = 'incidents'

    id = Column(String(50), primary_key=True)
    
    # Location
    network_id = Column(String(50), ForeignKey('networks.id'), nullable=False)
    intersection_id = Column(String(50), ForeignKey('intersections.id'), nullable=True)
    
    # Details
    incident_type = Column(Enum(IncidentType), nullable=False)
    severity = Column(Integer, default=3, nullable=False)  # 1-5 scale
    description = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default='reported', nullable=False)  # reported, verified, cleared
    verified_by = Column(String(128), ForeignKey('users.id'), nullable=True)
    
    # Timeline
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    cleared_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_incident_network', 'network_id'),
    )

    def __repr__(self):
        return f"<Incident {self.id}>"


class EmergencyRequestType(enum.Enum):
    """Emergency vehicle type."""
    AMBULANCE = "ambulance"
    FIRE = "fire"
    POLICE = "police"


class EmergencyRequest(Base):
    """Emergency vehicle routing request."""
    __tablename__ = 'emergency_requests'

    id = Column(String(50), primary_key=True)
    
    # Request details
    request_type = Column(Enum(EmergencyRequestType), nullable=False)
    network_id = Column(String(50), ForeignKey('networks.id'), nullable=False)
    
    # Route
    origin_junction_id = Column(String(50), ForeignKey('intersections.id'), nullable=False)
    destination_junction_id = Column(String(50), ForeignKey('intersections.id'), nullable=False)
    
    # Corridor
    assigned_corridor = Column(JSON, nullable=True)  # [J1, J2, J3, ...]
    
    # Status
    status = Column(String(50), default='pending', nullable=False)  # pending, active, arrived, canceled
    eta_seconds = Column(Float, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    activated_at = Column(DateTime, nullable=True)
    arrived_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_emergency_network', 'network_id'),
    )

    def __repr__(self):
        return f"<EmergencyRequest {self.id}>"


class SignalEvent(Base):
    """Traffic signal phase change event."""
    __tablename__ = 'signal_events'

    id = Column(String(50), primary_key=True)
    
    # Event
    intersection_id = Column(String(50), ForeignKey('intersections.id'), nullable=False, index=True)
    old_phase = Column(Integer, nullable=False)
    new_phase = Column(Integer, nullable=False)
    
    # Controller
    controller = Column(String(100), nullable=False)  # 'fixed_time', 'adaptive', 'ppo', 'emergency'
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_seconds = Column(Float, nullable=True)

    # Relationships
    intersection = relationship('Intersection', back_populates='signals')

    __table_args__ = (
        Index('idx_signal_event_intersection', 'intersection_id'),
        Index('idx_signal_event_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<SignalEvent {self.intersection_id}@{self.timestamp}>"


class MetricSnapshot(Base):
    """Time-series traffic metrics snapshot."""
    __tablename__ = 'metric_snapshots'

    id = Column(String(50), primary_key=True)
    
    # Location
    intersection_id = Column(String(50), ForeignKey('intersections.id'), nullable=False, index=True)
    
    # Metrics
    avg_waiting_time_s = Column(Float, nullable=False)
    avg_queue_length = Column(Float, nullable=False)
    throughput_vph = Column(Float, nullable=False)  # Vehicles per hour
    occupancy_rate = Column(Float, nullable=False)  # 0-1
    
    # Timestamp (bucketed to nearest 5 seconds)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    intersection = relationship('Intersection', back_populates='metrics')

    __table_args__ = (
        Index('idx_metric_intersection_time', 'intersection_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<MetricSnapshot {self.intersection_id}@{self.timestamp}>"


# ============================================================================
# Audit Logging
# ============================================================================

class AuditEvent(Base):
    """Immutable audit trail of all mutations."""
    __tablename__ = 'audit_events'

    id = Column(String(50), primary_key=True)
    
    # Actor
    user_id = Column(String(128), ForeignKey('users.id'), nullable=False, index=True)
    
    # Action
    action = Column(String(100), nullable=False)  # 'create_incident', 'approve_corridor', etc.
    resource_type = Column(String(50), nullable=False)  # 'incident', 'emergency_request', etc.
    resource_id = Column(String(100), nullable=False, index=True)
    
    # Changes
    before_state = Column(JSON, nullable=True)  # Old values
    after_state = Column(JSON, nullable=True)   # New values
    
    # Metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='audit_events')

    __table_args__ = (
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_resource', 'resource_id'),
        Index('idx_audit_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditEvent {self.action}@{self.timestamp}>"
