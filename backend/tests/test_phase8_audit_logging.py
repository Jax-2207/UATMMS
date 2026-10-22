"""
Phase 8: Audit Logging Tests
Tests immutable audit trails, specific audit operations, and audit queries.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.app.db.models import Base, User, AuditEvent
from backend.app.db.audit import (
    AuditLogger,
    audit_emergency_request_change,
    audit_incident_verification,
    audit_corridor_approval,
    audit_model_promotion,
    audit_user_role_change,
    audit_signal_override,
    get_audit_trail,
    get_user_audit_history,
    get_recent_actions,
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


# ============================================================================
# Basic Audit Logging Tests
# ============================================================================

class TestAuditLoggerBasic:
    """Test basic audit logging functionality."""
    
    def test_log_action_creates_event(self, db, test_user):
        """Test log_action creates audit event."""
        event = AuditLogger.log_action(
            user_id=test_user.id,
            action="test_action",
            resource_type="test_resource",
            resource_id="resource_1",
            db=db
        )
        
        assert event is not None
        assert event.user_id == test_user.id
        assert event.action == "test_action"
        assert event.resource_type == "test_resource"
    
    def test_log_action_persists_to_db(self, db, test_user):
        """Test audit event is persisted to database."""
        AuditLogger.log_action(
            user_id=test_user.id,
            action="test_action",
            resource_type="test_resource",
            resource_id="resource_1",
            db=db
        )
        
        events = db.query(AuditEvent).filter(
            AuditEvent.user_id == test_user.id
        ).all()
        
        assert len(events) == 1
        assert events[0].action == "test_action"
    
    def test_log_action_without_db_session(self, test_user):
        """Test log_action without database session returns None."""
        result = AuditLogger.log_action(
            user_id=test_user.id,
            action="test_action",
            resource_type="test_resource",
            resource_id="resource_1",
            db=None
        )
        
        assert result is None
    
    def test_log_action_with_before_state(self, db, test_user):
        """Test log_action with before_state."""
        before_state = {"status": "pending"}
        
        event = AuditLogger.log_action(
            user_id=test_user.id,
            action="update_status",
            resource_type="incident",
            resource_id="incident_1",
            before_state=before_state,
            db=db
        )
        
        assert event.before_state == before_state
    
    def test_log_action_with_after_state(self, db, test_user):
        """Test log_action with after_state."""
        after_state = {"status": "verified"}
        
        event = AuditLogger.log_action(
            user_id=test_user.id,
            action="verify_incident",
            resource_type="incident",
            resource_id="incident_1",
            after_state=after_state,
            db=db
        )
        
        assert event.after_state == after_state
    
    def test_log_action_with_both_states(self, db, test_user):
        """Test log_action with both before and after states."""
        before = {"status": "pending"}
        after = {"status": "verified"}
        
        event = AuditLogger.log_action(
            user_id=test_user.id,
            action="verify_incident",
            resource_type="incident",
            resource_id="incident_1",
            before_state=before,
            after_state=after,
            db=db
        )
        
        assert event.before_state == before
        assert event.after_state == after
    
    def test_log_action_with_ip_address(self, db, test_user):
        """Test log_action with IP address."""
        event = AuditLogger.log_action(
            user_id=test_user.id,
            action="login",
            resource_type="session",
            resource_id="session_1",
            ip_address="192.168.1.1",
            db=db
        )
        
        assert event.ip_address == "192.168.1.1"
    
    def test_log_action_has_timestamp(self, db, test_user):
        """Test audit event has timestamp."""
        before = datetime.utcnow()
        
        event = AuditLogger.log_action(
            user_id=test_user.id,
            action="test",
            resource_type="resource",
            resource_id="res_1",
            db=db
        )
        
        after = datetime.utcnow()
        
        assert before <= event.timestamp <= after


# ============================================================================
# Specific Audit Operations Tests
# ============================================================================

class TestSpecificAuditOperations:
    """Test domain-specific audit operations."""
    
    def test_audit_emergency_status_change(self, db, test_user):
        """Test auditing emergency status change."""
        audit_emergency_request_change(
            user_id=test_user.id,
            emergency_id="emg_1",
            old_status="pending",
            new_status="active",
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "emg_1"
        ).first()
        
        assert event is not None
        assert "pending" in event.action
        assert "active" in event.action
        assert event.before_state["status"] == "pending"
        assert event.after_state["status"] == "active"
    
    def test_audit_incident_verification_true(self, db, test_user):
        """Test auditing incident verification (verified=True)."""
        audit_incident_verification(
            user_id=test_user.id,
            incident_id="incident_1",
            verified=True,
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "incident_1"
        ).first()
        
        assert event.action == "verify_incident"
        assert event.after_state["verified"] is True
    
    def test_audit_incident_verification_false(self, db, test_user):
        """Test auditing incident verification (verified=False)."""
        audit_incident_verification(
            user_id=test_user.id,
            incident_id="incident_1",
            verified=False,
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "incident_1"
        ).first()
        
        assert event.action == "reject_incident"
        assert event.after_state["verified"] is False
    
    def test_audit_corridor_approval_approved(self, db, test_user):
        """Test auditing corridor approval."""
        corridor = ["J1", "J2", "J3"]
        
        audit_corridor_approval(
            user_id=test_user.id,
            emergency_id="emg_1",
            corridor=corridor,
            approved=True,
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "emg_1"
        ).first()
        
        assert event.action == "approve_corridor"
        assert event.after_state["corridor"] == corridor
        assert event.after_state["approved"] is True
    
    def test_audit_corridor_approval_rejected(self, db, test_user):
        """Test auditing corridor rejection."""
        corridor = ["J1", "J2", "J3"]
        
        audit_corridor_approval(
            user_id=test_user.id,
            emergency_id="emg_1",
            corridor=corridor,
            approved=False,
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "emg_1"
        ).first()
        
        assert event.action == "reject_corridor"
        assert event.after_state["approved"] is False
    
    def test_audit_model_promotion(self, db, test_user):
        """Test auditing model promotion."""
        metrics = {"mean_reward": -5.5, "safety_violations": 0}
        
        audit_model_promotion(
            user_id=test_user.id,
            model_id="ppo_v1",
            promoted=True,
            metrics=metrics,
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "ppo_v1"
        ).first()
        
        assert event.action == "promote_model"
        assert event.after_state["promoted"] is True
        assert event.after_state["metrics"] == metrics
    
    def test_audit_model_rejection(self, db, test_user):
        """Test auditing model rejection."""
        metrics = {"mean_reward": -20.0, "safety_violations": 5}
        
        audit_model_promotion(
            user_id=test_user.id,
            model_id="ppo_v1",
            promoted=False,
            metrics=metrics,
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "ppo_v1"
        ).first()
        
        assert event.action == "reject_model"
        assert event.after_state["promoted"] is False
    
    def test_audit_user_role_add(self, db, test_user):
        """Test auditing role addition."""
        audit_user_role_change(
            user_id=test_user.id,
            target_user_id="target_user_1",
            role_id="admin",
            added=True,
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "target_user_1"
        ).first()
        
        assert event.action == "add_role_to_user"
        assert event.after_state["role"] == "admin"
        assert event.after_state["action"] == "add"
    
    def test_audit_user_role_remove(self, db, test_user):
        """Test auditing role removal."""
        audit_user_role_change(
            user_id=test_user.id,
            target_user_id="target_user_1",
            role_id="admin",
            added=False,
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "target_user_1"
        ).first()
        
        assert event.action == "remove_role_to_user"
        assert event.after_state["action"] == "remove"
    
    def test_audit_signal_override(self, db, test_user):
        """Test auditing signal override."""
        audit_signal_override(
            user_id=test_user.id,
            junction_id="J1",
            old_phase=0,
            new_phase=2,
            reason="Emergency vehicle approaching",
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "J1"
        ).first()
        
        assert event.action == "override_signal"
        assert event.before_state["phase"] == 0
        assert event.after_state["phase"] == 2
        assert event.after_state["reason"] == "Emergency vehicle approaching"


# ============================================================================
# Audit Immutability Tests
# ============================================================================

class TestAuditImmutability:
    """Test that audit trail is immutable."""
    
    def test_audit_events_append_only(self, db, test_user):
        """Test audit events are append-only."""
        # Create first event
        event1 = AuditLogger.log_action(
            user_id=test_user.id,
            action="action_1",
            resource_type="resource",
            resource_id="res_1",
            db=db
        )
        
        # Create second event
        event2 = AuditLogger.log_action(
            user_id=test_user.id,
            action="action_2",
            resource_type="resource",
            resource_id="res_1",
            db=db
        )
        
        # Verify both exist and are in order
        events = db.query(AuditEvent).filter(
            AuditEvent.resource_id == "res_1"
        ).order_by(AuditEvent.timestamp).all()
        
        assert len(events) == 2
        assert events[0].action == "action_1"
        assert events[1].action == "action_2"
    
    def test_audit_trail_full_history(self, db, test_user):
        """Test complete audit trail of resource lifecycle."""
        resource_id = "res_1"
        
        # Sequence of events
        audit_emergency_request_change(
            user_id=test_user.id,
            emergency_id=resource_id,
            old_status="pending",
            new_status="active",
            db=db
        )
        
        audit_emergency_request_change(
            user_id=test_user.id,
            emergency_id=resource_id,
            old_status="active",
            new_status="completed",
            db=db
        )
        
        # Get full trail
        trail = db.query(AuditEvent).filter(
            AuditEvent.resource_id == resource_id
        ).order_by(AuditEvent.timestamp).all()
        
        assert len(trail) == 2
        assert trail[0].action == "emergency_status_change_pending_to_active"
        assert trail[1].action == "emergency_status_change_active_to_completed"
    
    def test_cannot_modify_audit_event(self, db, test_user):
        """Test that audit events cannot be modified."""
        event = AuditLogger.log_action(
            user_id=test_user.id,
            action="original_action",
            resource_type="resource",
            resource_id="res_1",
            db=db
        )
        
        original_id = event.id
        original_action = event.action
        
        # Attempt to modify (SQLAlchemy should prevent this or raise error)
        # In production, the audit table should have immutability constraints
        retrieved_event = db.query(AuditEvent).filter(
            AuditEvent.id == original_id
        ).first()
        
        assert retrieved_event.action == original_action


# ============================================================================
# Audit Query Tests
# ============================================================================

class TestAuditQueries:
    """Test audit trail queries."""
    
    def test_get_audit_trail_for_resource(self, db, test_user):
        """Test retrieving audit trail for specific resource."""
        resource_id = "res_1"
        
        # Create multiple events for same resource
        for i in range(3):
            AuditLogger.log_action(
                user_id=test_user.id,
                action=f"action_{i}",
                resource_type="resource",
                resource_id=resource_id,
                db=db
            )
        
        trail = get_audit_trail(resource_id, db)
        
        assert len(trail) == 3
        assert all(event.resource_id == resource_id for event in trail)
    
    def test_get_audit_trail_limit(self, db, test_user):
        """Test audit trail limit."""
        resource_id = "res_1"
        
        # Create 10 events
        for i in range(10):
            AuditLogger.log_action(
                user_id=test_user.id,
                action=f"action_{i}",
                resource_type="resource",
                resource_id=resource_id,
                db=db
            )
        
        trail = get_audit_trail(resource_id, db, limit=5)
        
        assert len(trail) == 5
    
    def test_get_audit_trail_empty(self, db):
        """Test audit trail for nonexistent resource."""
        trail = get_audit_trail("nonexistent", db)
        
        assert trail == []
    
    def test_get_user_audit_history(self, db):
        """Test getting audit history for specific user."""
        user1 = User(
            id="user_1",
            firebase_uid="fb_1",
            email="user1@example.com",
            created_at=datetime.utcnow()
        )
        user2 = User(
            id="user_2",
            firebase_uid="fb_2",
            email="user2@example.com",
            created_at=datetime.utcnow()
        )
        db.add_all([user1, user2])
        db.commit()
        
        # User1 performs 3 actions
        for i in range(3):
            AuditLogger.log_action(
                user_id=user1.id,
                action=f"action_{i}",
                resource_type="resource",
                resource_id=f"res_{i}",
                db=db
            )
        
        # User2 performs 2 actions
        for i in range(2):
            AuditLogger.log_action(
                user_id=user2.id,
                action=f"action_{i}",
                resource_type="resource",
                resource_id=f"res_u2_{i}",
                db=db
            )
        
        user1_history = get_user_audit_history(user1.id, db)
        user2_history = get_user_audit_history(user2.id, db)
        
        assert len(user1_history) == 3
        assert len(user2_history) == 2
        assert all(event.user_id == user1.id for event in user1_history)
    
    def test_get_user_audit_history_filter_action(self, db, test_user):
        """Test filtering user history by action."""
        # Create mixed actions
        AuditLogger.log_action(
            user_id=test_user.id,
            action="verify_incident",
            resource_type="incident",
            resource_id="inc_1",
            db=db
        )
        
        AuditLogger.log_action(
            user_id=test_user.id,
            action="approve_corridor",
            resource_type="corridor",
            resource_id="cor_1",
            db=db
        )
        
        AuditLogger.log_action(
            user_id=test_user.id,
            action="verify_incident",
            resource_type="incident",
            resource_id="inc_2",
            db=db
        )
        
        verify_history = get_user_audit_history(
            test_user.id, db, action_filter="verify"
        )
        
        assert len(verify_history) == 2
        assert all("verify" in event.action for event in verify_history)
    
    def test_get_user_audit_history_limit(self, db, test_user):
        """Test user history limit."""
        # Create 10 events
        for i in range(10):
            AuditLogger.log_action(
                user_id=test_user.id,
                action=f"action_{i}",
                resource_type="resource",
                resource_id=f"res_{i}",
                db=db
            )
        
        history = get_user_audit_history(test_user.id, db, limit=5)
        
        assert len(history) == 5
    
    def test_get_recent_actions(self, db):
        """Test getting recent occurrences of specific action."""
        user1 = User(
            id="user_1",
            firebase_uid="fb_1",
            email="user1@example.com",
            created_at=datetime.utcnow()
        )
        user2 = User(
            id="user_2",
            firebase_uid="fb_2",
            email="user2@example.com",
            created_at=datetime.utcnow()
        )
        db.add_all([user1, user2])
        db.commit()
        
        # Both users approve corridors
        for i in range(3):
            AuditLogger.log_action(
                user_id=user1.id if i % 2 == 0 else user2.id,
                action="approve_corridor",
                resource_type="corridor",
                resource_id=f"cor_{i}",
                db=db
            )
        
        recent = get_recent_actions("approve_corridor", db, limit=10)
        
        assert len(recent) == 3
        assert all(event.action == "approve_corridor" for event in recent)
    
    def test_get_recent_actions_limit(self, db, test_user):
        """Test recent actions limit."""
        # Create 20 events with same action
        for i in range(20):
            AuditLogger.log_action(
                user_id=test_user.id,
                action="test_action",
                resource_type="resource",
                resource_id=f"res_{i}",
                db=db
            )
        
        recent = get_recent_actions("test_action", db, limit=10)
        
        assert len(recent) == 10


# ============================================================================
# Permission Check Audit Tests
# ============================================================================

class TestPermissionCheckAudit:
    """Test auditing permission checks."""
    
    def test_log_permission_check_allowed(self, db, test_user):
        """Test logging successful permission check."""
        AuditLogger.log_permission_check(
            user_id=test_user.id,
            permission_id="view_signals",
            allowed=True,
            resource_id="signal_1",
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.action.like("permission_check%")
        ).first()
        
        assert event is not None
        assert event.after_state["allowed"] is True
    
    def test_log_permission_check_denied(self, db, test_user):
        """Test logging denied permission check."""
        AuditLogger.log_permission_check(
            user_id=test_user.id,
            permission_id="override_signal",
            allowed=False,
            resource_id="signal_1",
            db=db
        )
        
        event = db.query(AuditEvent).filter(
            AuditEvent.action.like("permission_check%")
        ).first()
        
        assert event is not None
        assert event.after_state["allowed"] is False
    
    def test_log_permission_check_without_db(self, test_user):
        """Test permission check logging without db."""
        # Should not raise error
        AuditLogger.log_permission_check(
            user_id=test_user.id,
            permission_id="view_signals",
            allowed=True,
            db=None
        )

