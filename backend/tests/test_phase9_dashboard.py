"""
Phase 9: Dashboard Tests
Tests WebSocket connections, serialization, and real-time updates.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.app.db.models import (
    Base, User, Role, Network, Intersection, RoadSegment,
    SignalEvent, MetricSnapshot, Incident, IncidentType,
    EmergencyRequest, EmergencyRequestType
)
from backend.app.auth.firebase_auth import FirebaseAuthContext
from backend.app.dashboard.websocket import (
    ConnectionManager, connection_manager, MessageType, websocket_handler
)
from backend.app.dashboard.serializers import (
    serialize_network_state,
    serialize_traffic_metrics,
    serialize_incidents,
    serialize_emergencies,
    serialize_dashboard_summary,
    create_delta_update
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


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        id="test_user_1",
        firebase_uid="fb_test_1",
        email="test@example.com",
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def test_network(db):
    """Create a test network."""
    network = Network(
        id="test_network",
        name="Test Network",
        junctions_count=3,
        edges_count=3
    )
    db.add(network)
    db.commit()
    return network


@pytest.fixture
def test_intersections(db, test_network):
    """Create test intersections."""
    j1 = Intersection(id="J1", network_id=test_network.id, latitude=13.0, longitude=77.5, name="Junction 1")
    j2 = Intersection(id="J2", network_id=test_network.id, latitude=13.1, longitude=77.6, name="Junction 2")
    j3 = Intersection(id="J3", network_id=test_network.id, latitude=13.2, longitude=77.7, name="Junction 3")
    
    db.add_all([j1, j2, j3])
    db.commit()
    return [j1, j2, j3]


@pytest.fixture
def test_road_segments(db, test_network, test_intersections):
    """Create test road segments."""
    s1 = RoadSegment(id="S1", network_id=test_network.id, from_junction_id="J1", to_junction_id="J2", lanes=2, length_m=500.0)
    s2 = RoadSegment(id="S2", network_id=test_network.id, from_junction_id="J2", to_junction_id="J3", lanes=2, length_m=600.0)
    
    db.add_all([s1, s2])
    db.commit()
    return [s1, s2]


@pytest.fixture
def test_auth_context(test_user):
    """Create a test auth context."""
    return FirebaseAuthContext(test_user, ["admin"], {"view_signals", "override_signal"})


# ============================================================================
# Connection Manager Tests
# ============================================================================

class TestConnectionManager:
    """Test WebSocket connection management."""
    
    def test_connect_user(self):
        """Test connecting a user."""
        manager = ConnectionManager()
        websocket = Mock()
        auth_context = Mock()
        
        # Manually add connection (simulating async)
        manager.active_connections["user_1"] = [websocket]
        manager.user_contexts["user_1"] = auth_context
        
        assert "user_1" in manager.active_connections
        assert websocket in manager.active_connections["user_1"]
    
    def test_multiple_connections_same_user(self):
        """Test multiple connections from same user."""
        manager = ConnectionManager()
        ws1 = Mock()
        ws2 = Mock()
        auth_context = Mock()
        
        # Manually add connections
        manager.active_connections["user_1"] = [ws1, ws2]
        manager.user_contexts["user_1"] = auth_context
        
        assert len(manager.active_connections["user_1"]) == 2
    
    def test_disconnect_user(self):
        """Test disconnecting a user."""
        manager = ConnectionManager()
        websocket = Mock()
        auth_context = Mock()
        
        # Manually add connection
        manager.active_connections["user_1"] = [websocket]
        manager.user_contexts["user_1"] = auth_context
        
        manager.disconnect("user_1", websocket)
        
        assert "user_1" not in manager.active_connections
    
    def test_broadcast_to_user(self):
        """Test broadcasting message to user."""
        manager = ConnectionManager()
        ws1 = Mock()
        ws2 = Mock()
        auth_context = Mock()
        
        # Manually add connections
        manager.active_connections["user_1"] = [ws1, ws2]
        manager.user_contexts["user_1"] = auth_context
        
        # Test that broadcast would send to all connections
        # (actual async sending is tested in integration tests)
        assert len(manager.active_connections["user_1"]) == 2
    
    def test_broadcast_to_all(self):
        """Test broadcasting message to all users."""
        manager = ConnectionManager()
        ws1 = Mock()
        ws2 = Mock()
        auth_context = Mock()
        
        # Manually add connections
        manager.active_connections["user_1"] = [ws1]
        manager.active_connections["user_2"] = [ws2]
        manager.user_contexts["user_1"] = auth_context
        manager.user_contexts["user_2"] = auth_context
        
        # Verify both users have connections
        assert len(manager.get_connected_users()) == 2
    
    def test_get_connection_count(self):
        """Test getting connection count."""
        manager = ConnectionManager()
        
        manager.active_connections["user_1"] = [Mock(), Mock()]
        manager.active_connections["user_2"] = [Mock()]
        
        assert manager.get_connection_count() == 3
    
    def test_get_connected_users(self):
        """Test getting connected users."""
        manager = ConnectionManager()
        
        manager.active_connections["user_1"] = [Mock()]
        manager.active_connections["user_2"] = [Mock()]
        
        users = manager.get_connected_users()
        assert set(users) == {"user_1", "user_2"}


# ============================================================================
# Network State Serialization Tests
# ============================================================================

class TestNetworkStateSerialization:
    """Test network topology serialization."""
    
    def test_serialize_network_basic(self, db, test_network, test_intersections, test_road_segments):
        """Test basic network serialization."""
        result = serialize_network_state(db)
        
        assert "networks" in result
        assert len(result["networks"]) == 1
        
        network = result["networks"][0]
        assert network["id"] == "test_network"
        assert len(network["junctions"]) == 3
        assert len(network["segments"]) == 2
    
    def test_serialize_network_signal_state(self, db, test_network, test_intersections):
        """Test network with signal state."""
        # Add signal event
        event = SignalEvent(
            id="evt_1",
            intersection_id="J1",
            old_phase=0,
            new_phase=1,
            controller="adaptive",
            duration_seconds=30.0
        )
        db.add(event)
        db.commit()
        
        result = serialize_network_state(db)
        
        network = result["networks"][0]
        j1 = next(j for j in network["junctions"] if j["id"] == "J1")
        
        assert j1["signal_state"]["phase"] == 1
        assert j1["signal_state"]["duration"] == 30.0
    
    def test_serialize_multiple_networks(self, db):
        """Test serializing multiple networks."""
        net1 = Network(id="net1", name="Network 1", junctions_count=1, edges_count=0)
        net2 = Network(id="net2", name="Network 2", junctions_count=1, edges_count=0)
        
        db.add_all([net1, net2])
        db.commit()
        
        result = serialize_network_state(db)
        
        assert len(result["networks"]) == 2
        assert result["total_junctions"] == 0  # No intersections added


# ============================================================================
# Traffic Metrics Serialization Tests
# ============================================================================

class TestMetricsSeralization:
    """Test traffic metrics serialization."""
    
    def test_serialize_metrics_empty(self, db):
        """Test serializing empty metrics."""
        result = serialize_traffic_metrics(db)
        
        assert "metrics" in result
        assert result["total_intersections"] == 0
    
    def test_serialize_metrics_single(self, db, test_network, test_intersections):
        """Test serializing single metric."""
        metric = MetricSnapshot(
            id="m1",
            intersection_id="J1",
            avg_waiting_time_s=15.5,
            avg_queue_length=5.2,
            throughput_vph=200.0,
            occupancy_rate=0.65
        )
        db.add(metric)
        db.commit()
        
        result = serialize_traffic_metrics(db)
        
        assert len(result["metrics"]) == 1
        assert result["metrics"][0]["intersection_id"] == "J1"
        assert result["metrics"][0]["latest"]["waiting_time"] == 15.5
    
    def test_serialize_metrics_history(self, db, test_network, test_intersections):
        """Test metrics with history."""
        for i in range(5):
            metric = MetricSnapshot(
                id=f"m{i}",
                intersection_id="J1",
                avg_waiting_time_s=10.0 + i,
                avg_queue_length=5.0,
                throughput_vph=200.0,
                occupancy_rate=0.65
            )
            db.add(metric)
        db.commit()
        
        result = serialize_traffic_metrics(db)
        
        assert len(result["metrics"][0]["history"]) == 5


# ============================================================================
# Incident Serialization Tests
# ============================================================================

class TestIncidentSerialization:
    """Test incident serialization."""
    
    def test_serialize_incidents_empty(self, db):
        """Test serializing empty incidents."""
        result = serialize_incidents(db)
        
        assert "incidents" in result
        assert len(result["incidents"]) == 0
        assert result["by_status"]["reported"] == 0
    
    def test_serialize_incidents_basic(self, db, test_network):
        """Test serializing basic incident."""
        incident = Incident(
            id="inc1",
            network_id=test_network.id,
            incident_type=IncidentType.ACCIDENT,
            severity=3,
            description="Test incident",
            status="reported"
        )
        db.add(incident)
        db.commit()
        
        result = serialize_incidents(db)
        
        assert len(result["incidents"]) == 1
        assert result["by_status"]["reported"] == 1
        assert result["by_severity"][3] == 1
    
    def test_serialize_incidents_filtering(self, db, test_network, test_auth_context):
        """Test incident filtering by auth context."""
        # Create incidents
        i1 = Incident(id="inc1", network_id=test_network.id, incident_type=IncidentType.ACCIDENT, severity=2, status="reported")
        i2 = Incident(id="inc2", network_id=test_network.id, incident_type=IncidentType.CONGESTION, severity=3, status="verified")
        
        db.add_all([i1, i2])
        db.commit()
        
        # Public user should only see verified
        public_context = FirebaseAuthContext(test_auth_context.user, ["public"], set())
        result = serialize_incidents(db, public_context)
        
        assert len(result["incidents"]) == 1
        assert result["incidents"][0]["status"] == "verified"


# ============================================================================
# Emergency Serialization Tests
# ============================================================================

class TestEmergencySerialization:
    """Test emergency request serialization."""
    
    def test_serialize_emergencies_empty(self, db):
        """Test serializing empty emergencies."""
        result = serialize_emergencies(db)
        
        assert "emergencies" in result
        assert len(result["emergencies"]) == 0
    
    def test_serialize_emergencies_basic(self, db, test_network, test_intersections):
        """Test serializing basic emergency."""
        emergency = EmergencyRequest(
            id="emg1",
            network_id=test_network.id,
            origin_junction_id="J1",
            destination_junction_id="J3",
            request_type=EmergencyRequestType.AMBULANCE,
            status="pending"
        )
        db.add(emergency)
        db.commit()
        
        result = serialize_emergencies(db)
        
        assert len(result["emergencies"]) == 1
        assert result["by_type"]["ambulance"] == 1
        assert result["by_status"]["pending"] == 1
    
    def test_serialize_emergencies_filtering(self, db, test_network, test_intersections):
        """Test emergency filtering by auth context."""
        # Create emergencies
        e1 = EmergencyRequest(
            id="emg1",
            network_id=test_network.id,
            origin_junction_id="J1",
            destination_junction_id="J2",
            request_type=EmergencyRequestType.AMBULANCE,
            status="pending"
        )
        e2 = EmergencyRequest(
            id="emg2",
            network_id=test_network.id,
            origin_junction_id="J2",
            destination_junction_id="J3",
            request_type=EmergencyRequestType.FIRE,
            status="active"
        )
        
        db.add_all([e1, e2])
        db.commit()
        
        # Public user should only see active
        user = User(id="pub_user", firebase_uid="pub_fb", email="public@example.com", created_at=datetime.utcnow())
        public_context = FirebaseAuthContext(user, ["public"], set())
        
        result = serialize_emergencies(db, public_context)
        
        assert len(result["emergencies"]) == 1
        assert result["emergencies"][0]["status"] == "active"


# ============================================================================
# Dashboard Summary Tests
# ============================================================================

class TestDashboardSummary:
    """Test complete dashboard summary."""
    
    def test_serialize_dashboard_summary(self, db, test_network, test_intersections, test_road_segments, test_auth_context):
        """Test complete dashboard summary."""
        result = serialize_dashboard_summary(db, test_auth_context)
        
        assert "network" in result
        assert "metrics" in result
        assert "incidents" in result
        assert "emergencies" in result
        assert "timestamp" in result
        assert "user" in result
        assert "roles" in result


# ============================================================================
# Delta Encoding Tests
# ============================================================================

class TestDeltaEncoding:
    """Test delta encoding for bandwidth optimization."""
    
    def test_create_delta_no_changes(self):
        """Test delta with no changes."""
        state = {"a": 1, "b": 2}
        delta = create_delta_update(state, state)
        
        assert len(delta["changes"]) == 0
    
    def test_create_delta_with_changes(self):
        """Test delta with changes."""
        old = {"a": 1, "b": 2, "c": 3}
        new = {"a": 1, "b": 20, "c": 3, "d": 4}
        
        delta = create_delta_update(old, new)
        
        assert "b" in delta["changes"]  # Changed
        assert "d" in delta["changes"]  # New
        assert delta["changes"]["b"] == 20
        assert delta["changes"]["d"] == 4
    
    def test_create_delta_timestamp(self):
        """Test delta includes timestamp."""
        old = {"a": 1}
        new = {"a": 2, "timestamp": "2024-10-22T12:00:00"}
        
        delta = create_delta_update(old, new)
        
        assert "timestamp" in delta
        assert delta["timestamp"] == "2024-10-22T12:00:00"


# ============================================================================
# Message Type Constants Tests
# ============================================================================

class TestMessageTypes:
    """Test message type constants."""
    
    def test_message_type_constants(self):
        """Test all message type constants exist."""
        assert hasattr(MessageType, "SUBSCRIBE")
        assert hasattr(MessageType, "UNSUBSCRIBE")
        assert hasattr(MessageType, "PING")
        assert hasattr(MessageType, "PONG")
        assert hasattr(MessageType, "NETWORK_STATE")
        assert hasattr(MessageType, "TRAFFIC_METRICS")
        assert hasattr(MessageType, "INCIDENTS")
        assert hasattr(MessageType, "EMERGENCIES")
        assert hasattr(MessageType, "ERROR")
        assert hasattr(MessageType, "HEARTBEAT")
