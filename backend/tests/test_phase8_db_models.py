"""
Phase 8: Database Model Tests
Tests SQLAlchemy ORM models, relationships, and constraints.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.app.db.models import (
    Base, User, Role, Permission, Network, Intersection, RoadSegment,
    SimulationRun, ModelVersion, Incident, IncidentType, EmergencyRequest,
    EmergencyRequestType, SignalEvent, MetricSnapshot, AuditEvent
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db_session = SessionLocal()
    yield db_session
    db_session.close()


# ============================================================================
# User & RBAC Model Tests
# ============================================================================

class TestUserModel:
    """Test User model."""
    
    def test_user_creation(self, db):
        """Test creating a user."""
        user = User(
            id="user123",
            email="test@example.com",
            firebase_uid="firebase_uid_123",
            display_name="Test User",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        db_user = db.query(User).filter(User.id == "user123").first()
        assert db_user is not None
        assert db_user.email == "test@example.com"
        assert db_user.is_active is True
    
    def test_user_email_unique(self, db):
        """Test email uniqueness constraint."""
        user1 = User(
            id="user1", email="same@example.com",
            firebase_uid="fb1", created_at=datetime.utcnow()
        )
        user2 = User(
            id="user2", email="same@example.com",
            firebase_uid="fb2", created_at=datetime.utcnow()
        )
        db.add(user1)
        db.commit()
        
        db.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            db.commit()
    
    def test_user_firebase_uid_unique(self, db):
        """Test Firebase UID uniqueness."""
        user1 = User(
            id="user1", email="test1@example.com",
            firebase_uid="same_fb", created_at=datetime.utcnow()
        )
        user2 = User(
            id="user2", email="test2@example.com",
            firebase_uid="same_fb", created_at=datetime.utcnow()
        )
        db.add(user1)
        db.commit()
        
        db.add(user2)
        with pytest.raises(Exception):
            db.commit()
    
    def test_user_last_login_update(self, db):
        """Test last login timestamp."""
        user = User(
            id="user1", email="test@example.com",
            firebase_uid="fb1", created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        now = datetime.utcnow()
        user.last_login_at = now
        db.commit()
        
        db_user = db.query(User).filter(User.id == "user1").first()
        assert db_user.last_login_at is not None


class TestRoleModel:
    """Test Role model."""
    
    def test_role_creation(self, db):
        """Test creating a role."""
        role = Role(
            id="admin",
            name="Administrator",
            description="Admin role",
            priority=100
        )
        db.add(role)
        db.commit()
        
        db_role = db.query(Role).filter(Role.id == "admin").first()
        assert db_role is not None
        assert db_role.priority == 100
    
    def test_role_hierarchy(self, db):
        """Test role hierarchy."""
        roles_data = [
            ("admin", 100),
            ("operator", 60),
            ("police", 50),
            ("public", 10),
        ]
        
        for role_id, priority in roles_data:
            role = Role(id=role_id, name=role_id.title(), priority=priority)
            db.add(role)
        db.commit()
        
        admin = db.query(Role).filter(Role.id == "admin").first()
        public = db.query(Role).filter(Role.id == "public").first()
        
        assert admin.priority > public.priority


class TestPermissionModel:
    """Test Permission model."""
    
    def test_permission_creation(self, db):
        """Test creating permissions."""
        perm = Permission(
            id="view_signals",
            name="View Signals",
            resource="signal",
            action="view"
        )
        db.add(perm)
        db.commit()
        
        db_perm = db.query(Permission).filter(Permission.id == "view_signals").first()
        assert db_perm is not None
        assert db_perm.resource == "signal"
    
    def test_role_permission_relationship(self, db):
        """Test role-permission many-to-many relationship."""
        role = Role(id="operator", name="Operator", priority=60)
        perm1 = Permission(id="view_signals", name="View Signals", resource="signal", action="view")
        perm2 = Permission(id="approve_corridor", name="Approve Corridor", resource="corridor", action="approve")
        
        db.add_all([role, perm1, perm2])
        db.commit()
        
        role.permissions.append(perm1)
        role.permissions.append(perm2)
        db.commit()
        
        db_role = db.query(Role).filter(Role.id == "operator").first()
        assert len(db_role.permissions) == 2
        assert perm1 in db_role.permissions


class TestUserRoleRelationship:
    """Test user-role relationship."""
    
    def test_user_role_assignment(self, db):
        """Test assigning roles to users."""
        user = User(id="user1", email="test@example.com", firebase_uid="fb1", created_at=datetime.utcnow())
        role = Role(id="operator", name="Operator", priority=60)
        
        db.add(user)
        db.add(role)
        db.commit()
        
        user.roles.append(role)
        db.commit()
        
        db_user = db.query(User).filter(User.id == "user1").first()
        assert len(db_user.roles) == 1
        assert db_user.roles[0].id == "operator"


# ============================================================================
# Network Model Tests
# ============================================================================

class TestNetworkModels:
    """Test network-related models."""
    
    def test_network_creation(self, db):
        """Test creating a network."""
        network = Network(
            id="bengaluru_core",
            name="Bangalore Core Network",
            junctions_count=8,
            edges_count=16,
            osm_region="Bangalore MG Road"
        )
        db.add(network)
        db.commit()
        
        db_network = db.query(Network).filter(Network.id == "bengaluru_core").first()
        assert db_network is not None
        assert db_network.junctions_count == 8
    
    def test_intersection_in_network(self, db):
        """Test intersection-network relationship."""
        network = Network(id="net1", name="Network 1", junctions_count=1, edges_count=1)
        intersection = Intersection(
            id="J1",
            network_id="net1",
            latitude=13.0352,
            longitude=77.5245,
            name="MG Road"
        )
        
        db.add(network)
        db.commit()
        
        intersection.network_id = "net1"
        db.add(intersection)
        db.commit()
        
        db_intersection = db.query(Intersection).filter(Intersection.id == "J1").first()
        assert db_intersection.network_id == "net1"
    
    def test_road_segment_topology(self, db):
        """Test road segment connectivity."""
        network = Network(id="net1", name="Network 1", junctions_count=2, edges_count=1)
        j1 = Intersection(id="J1", network_id="net1", latitude=13.0, longitude=77.5)
        j2 = Intersection(id="J2", network_id="net1", latitude=13.1, longitude=77.6)
        segment = RoadSegment(
            id="J1_to_J2",
            network_id="net1",
            from_junction_id="J1",
            to_junction_id="J2",
            lanes=2,
            length_m=500.0
        )
        
        db.add_all([network, j1, j2, segment])
        db.commit()
        
        db_segment = db.query(RoadSegment).filter(RoadSegment.id == "J1_to_J2").first()
        assert db_segment.from_junction_id == "J1"
        assert db_segment.to_junction_id == "J2"


# ============================================================================
# Simulation Model Tests
# ============================================================================

class TestSimulationModels:
    """Test simulation-related models."""
    
    def test_simulation_run_creation(self, db):
        """Test creating simulation run record."""
        network = Network(id="net1", name="Network 1", junctions_count=1, edges_count=1)
        db.add(network)
        db.commit()
        
        run = SimulationRun(
            id="run_001",
            network_id="net1",
            scenario_name="peak_rush",
            random_seed=42,
            traffic_demand="peak",
            start_time_utc=datetime.utcnow(),
            signal_controller="ppo"
        )
        db.add(run)
        db.commit()
        
        db_run = db.query(SimulationRun).filter(SimulationRun.id == "run_001").first()
        assert db_run is not None
        assert db_run.signal_controller == "ppo"
    
    def test_model_version_creation(self, db):
        """Test creating model version."""
        model = ModelVersion(
            id="ppo_j1_v1",
            model_type="ppo",
            junction_id="J1",
            version_number=1,
            checkpoint_path="/models/ppo_j1_v1.zip",
            mean_reward=-6.5,
            mean_waiting_time=22.5,
            safety_violations=0
        )
        db.add(model)
        db.commit()
        
        db_model = db.query(ModelVersion).filter(ModelVersion.id == "ppo_j1_v1").first()
        assert db_model is not None
        assert db_model.is_promoted is False
    
    def test_model_promotion(self, db):
        """Test model promotion workflow."""
        user = User(id="admin1", email="admin@example.com", firebase_uid="fb1", created_at=datetime.utcnow())
        model = ModelVersion(
            id="ppo_j1_v1",
            model_type="ppo",
            version_number=1,
            checkpoint_path="/models/ppo_j1_v1.zip"
        )
        
        db.add(user)
        db.add(model)
        db.commit()
        
        model.is_promoted = True
        model.promoted_at = datetime.utcnow()
        model.promoted_by = "admin1"
        db.commit()
        
        db_model = db.query(ModelVersion).filter(ModelVersion.id == "ppo_j1_v1").first()
        assert db_model.is_promoted is True
        assert db_model.promoted_by == "admin1"


# ============================================================================
# Operational Model Tests
# ============================================================================

class TestIncidentModel:
    """Test Incident model."""
    
    def test_incident_creation(self, db):
        """Test creating incident."""
        network = Network(id="net1", name="Network 1", junctions_count=1, edges_count=1)
        db.add(network)
        db.commit()
        
        incident = Incident(
            id="incident_001",
            network_id="net1",
            incident_type=IncidentType.ACCIDENT,
            severity=4,
            description="Multi-vehicle collision",
            status="reported"
        )
        db.add(incident)
        db.commit()
        
        db_incident = db.query(Incident).filter(Incident.id == "incident_001").first()
        assert db_incident is not None
        assert db_incident.severity == 4


class TestEmergencyRequestModel:
    """Test EmergencyRequest model."""
    
    def test_emergency_creation(self, db):
        """Test creating emergency request."""
        network = Network(id="net1", name="Network 1", junctions_count=2, edges_count=1)
        j1 = Intersection(id="J1", network_id="net1", latitude=13.0, longitude=77.5)
        j2 = Intersection(id="J2", network_id="net1", latitude=13.1, longitude=77.6)
        
        db.add_all([network, j1, j2])
        db.commit()
        
        emergency = EmergencyRequest(
            id="emg_001",
            request_type=EmergencyRequestType.AMBULANCE,
            network_id="net1",
            origin_junction_id="J1",
            destination_junction_id="J2",
            status="pending"
        )
        db.add(emergency)
        db.commit()
        
        db_emergency = db.query(EmergencyRequest).filter(EmergencyRequest.id == "emg_001").first()
        assert db_emergency.request_type == EmergencyRequestType.AMBULANCE


# ============================================================================
# Event & Metrics Model Tests
# ============================================================================

class TestSignalEventModel:
    """Test SignalEvent model."""
    
    def test_signal_event_creation(self, db):
        """Test creating signal phase change event."""
        network = Network(id="net1", name="Network 1", junctions_count=1, edges_count=1)
        intersection = Intersection(id="J1", network_id="net1", latitude=13.0, longitude=77.5)
        
        db.add_all([network, intersection])
        db.commit()
        
        event = SignalEvent(
            id="sig_evt_001",
            intersection_id="J1",
            old_phase=0,
            new_phase=1,
            controller="adaptive",
            duration_seconds=10.0
        )
        db.add(event)
        db.commit()
        
        db_event = db.query(SignalEvent).filter(SignalEvent.id == "sig_evt_001").first()
        assert db_event.new_phase == 1


class TestMetricSnapshotModel:
    """Test MetricSnapshot model."""
    
    def test_metric_snapshot_creation(self, db):
        """Test creating metric snapshot."""
        network = Network(id="net1", name="Network 1", junctions_count=1, edges_count=1)
        intersection = Intersection(id="J1", network_id="net1", latitude=13.0, longitude=77.5)
        
        db.add_all([network, intersection])
        db.commit()
        
        metric = MetricSnapshot(
            id="metric_001",
            intersection_id="J1",
            avg_waiting_time_s=15.5,
            avg_queue_length=5.2,
            throughput_vph=200.0,
            occupancy_rate=0.65
        )
        db.add(metric)
        db.commit()
        
        db_metric = db.query(MetricSnapshot).filter(MetricSnapshot.id == "metric_001").first()
        assert db_metric.throughput_vph == 200.0


# ============================================================================
# Audit Model Tests
# ============================================================================

class TestAuditEventModel:
    """Test AuditEvent model."""
    
    def test_audit_event_creation(self, db):
        """Test creating audit event."""
        user = User(id="user1", email="test@example.com", firebase_uid="fb1", created_at=datetime.utcnow())
        db.add(user)
        db.commit()
        
        audit = AuditEvent(
            id="audit_001",
            user_id="user1",
            action="verify_incident",
            resource_type="incident",
            resource_id="incident_001",
            after_state={"verified": True},
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        
        db_audit = db.query(AuditEvent).filter(AuditEvent.id == "audit_001").first()
        assert db_audit is not None
        assert db_audit.action == "verify_incident"
    
    def test_audit_immutability(self, db):
        """Test audit events are tracked correctly."""
        user = User(id="user1", email="test@example.com", firebase_uid="fb1", created_at=datetime.utcnow())
        db.add(user)
        db.commit()
        
        audit1 = AuditEvent(
            id="audit_001",
            user_id="user1",
            action="approve_corridor",
            resource_type="emergency",
            resource_id="emg_001",
            timestamp=datetime.utcnow()
        )
        audit2 = AuditEvent(
            id="audit_002",
            user_id="user1",
            action="cancel_emergency",
            resource_type="emergency",
            resource_id="emg_001",
            timestamp=datetime.utcnow()
        )
        
        db.add_all([audit1, audit2])
        db.commit()
        
        trail = db.query(AuditEvent).filter(AuditEvent.resource_id == "emg_001").order_by(AuditEvent.timestamp).all()
        assert len(trail) == 2
        assert trail[0].action == "approve_corridor"
        assert trail[1].action == "cancel_emergency"
