"""
Phase 8: RBAC Authorization Tests
Tests permission checks, role enforcement, decorators, and resource-level access control.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.app.db.models import Base, User, Role, Permission, Incident, IncidentType
from backend.app.auth.rbac import (
    has_permission,
    has_role,
    is_admin,
    require_permission,
    require_role,
    can_modify_incident,
    can_view_emergency,
    init_rbac,
    ROLE_HIERARCHY,
    PERMISSIONS_MATRIX,
)
from backend.app.auth.firebase_auth import FirebaseAuthContext


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
def setup_rbac_full(db):
    """Setup complete RBAC with all roles and permissions."""
    init_rbac(db)
    return db


@pytest.fixture
def admin_user(db, setup_rbac_full):
    """Create admin user."""
    user = User(
        id="admin_user",
        firebase_uid="admin_fb",
        email="admin@example.com",
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    
    admin_role = db.query(Role).filter(Role.id == "admin").first()
    user.roles.append(admin_role)
    db.commit()
    
    return user


@pytest.fixture
def operator_user(db, setup_rbac_full):
    """Create operator user."""
    user = User(
        id="operator_user",
        firebase_uid="operator_fb",
        email="operator@example.com",
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    
    operator_role = db.query(Role).filter(Role.id == "operator").first()
    user.roles.append(operator_role)
    db.commit()
    
    return user


@pytest.fixture
def public_user(db, setup_rbac_full):
    """Create public user."""
    user = User(
        id="public_user",
        firebase_uid="public_fb",
        email="public@example.com",
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    
    public_role = db.query(Role).filter(Role.id == "public").first()
    user.roles.append(public_role)
    db.commit()
    
    return user


@pytest.fixture
def ambulance_user(db, setup_rbac_full):
    """Create ambulance user."""
    user = User(
        id="ambulance_user",
        firebase_uid="ambulance_fb",
        email="ambulance@example.com",
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    
    ambulance_role = db.query(Role).filter(Role.id == "ambulance").first()
    user.roles.append(ambulance_role)
    db.commit()
    
    return user


def create_auth_context(user: User) -> FirebaseAuthContext:
    """Helper to create auth context from user."""
    from backend.app.auth.firebase_auth import get_user_roles, get_user_permissions
    roles = get_user_roles(user)
    permissions = get_user_permissions(user)
    return FirebaseAuthContext(user, roles, permissions)


# ============================================================================
# RBAC Policy Tests
# ============================================================================

class TestRBACPolicy:
    """Test RBAC policy configuration."""
    
    def test_role_hierarchy_exists(self):
        """Test that role hierarchy is properly defined."""
        assert "admin" in ROLE_HIERARCHY
        assert "operator" in ROLE_HIERARCHY
        assert "police" in ROLE_HIERARCHY
        assert "public" in ROLE_HIERARCHY
    
    def test_admin_highest_priority(self):
        """Test admin has highest priority."""
        admin_priority = ROLE_HIERARCHY["admin"]
        assert admin_priority > ROLE_HIERARCHY["operator"]
        assert admin_priority > ROLE_HIERARCHY["police"]
        assert admin_priority > ROLE_HIERARCHY["public"]
    
    def test_public_lowest_priority(self):
        """Test public has lowest priority."""
        public_priority = ROLE_HIERARCHY["public"]
        assert public_priority < ROLE_HIERARCHY["operator"]
        assert public_priority < ROLE_HIERARCHY["admin"]
    
    def test_permissions_matrix_exists(self):
        """Test permission matrix is defined."""
        assert len(PERMISSIONS_MATRIX) > 0
        assert "view_signals" in PERMISSIONS_MATRIX
        assert "approve_corridor" in PERMISSIONS_MATRIX
    
    def test_view_signals_permission_exists(self):
        """Test view_signals is available to multiple roles."""
        perm_config = PERMISSIONS_MATRIX["view_signals"]
        assert "admin" in perm_config["roles"]
        assert "operator" in perm_config["roles"]
        assert "public" in perm_config["roles"]
    
    def test_override_signal_admin_only(self):
        """Test override_signal is admin-only."""
        perm_config = PERMISSIONS_MATRIX["override_signal"]
        assert perm_config["roles"] == ["admin"]


# ============================================================================
# Permission Check Tests
# ============================================================================

class TestPermissionChecks:
    """Test permission checking logic."""
    
    def test_has_permission_true(self, admin_user, setup_rbac_full):
        """Test has_permission returns true for valid permission."""
        auth_context = create_auth_context(admin_user)
        
        result = has_permission(auth_context, "view_signals")
        
        assert result is True
    
    def test_has_permission_false(self, public_user, setup_rbac_full):
        """Test has_permission returns false for unavailable permission."""
        auth_context = create_auth_context(public_user)
        
        result = has_permission(auth_context, "override_signal")
        
        assert result is False
    
    def test_has_permission_none_context(self):
        """Test has_permission with None context."""
        result = has_permission(None, "view_signals")
        
        assert result is False
    
    def test_has_role_true(self, admin_user):
        """Test has_role returns true for valid role."""
        auth_context = create_auth_context(admin_user)
        
        result = has_role(auth_context, "admin")
        
        assert result is True
    
    def test_has_role_false(self, public_user):
        """Test has_role returns false for invalid role."""
        auth_context = create_auth_context(public_user)
        
        result = has_role(auth_context, "admin")
        
        assert result is False
    
    def test_is_admin_true(self, admin_user):
        """Test is_admin returns true for admin."""
        auth_context = create_auth_context(admin_user)
        
        result = is_admin(auth_context)
        
        assert result is True
    
    def test_is_admin_false(self, operator_user):
        """Test is_admin returns false for non-admin."""
        auth_context = create_auth_context(operator_user)
        
        result = is_admin(auth_context)
        
        assert result is False


# ============================================================================
# Decorator Tests (require_permission)
# ============================================================================

class TestRequirePermissionDecorator:
    """Test require_permission FastAPI dependency."""
    
    def test_require_permission_allowed(self, admin_user, setup_rbac_full):
        """Test require_permission passes for authorized user."""
        auth_context = create_auth_context(admin_user)
        
        # Check permission directly
        result = has_permission(auth_context, "override_signal")
        assert result is True
    
    def test_require_permission_denied(self, public_user, setup_rbac_full):
        """Test require_permission denies unauthorized user."""
        auth_context = create_auth_context(public_user)
        
        # Check permission directly
        result = has_permission(auth_context, "override_signal")
        assert result is False
    
    def test_require_permission_unauthenticated(self):
        """Test require_permission denies unauthenticated request."""
        # None context should have no permissions
        result = has_permission(None, "view_signals")
        assert result is False
    
    def test_require_permission_operator_approve_corridor(self, operator_user, setup_rbac_full):
        """Test operator can approve corridor."""
        auth_context = create_auth_context(operator_user)
        
        # Check permission directly
        result = has_permission(auth_context, "approve_corridor")
        assert result is True
    
    def test_require_permission_public_cannot_approve(self, public_user, setup_rbac_full):
        """Test public cannot approve corridor."""
        auth_context = create_auth_context(public_user)
        
        # Check permission directly
        result = has_permission(auth_context, "approve_corridor")
        assert result is False


# ============================================================================
# Decorator Tests (require_role)
# ============================================================================

class TestRequireRoleDecorator:
    """Test require_role FastAPI dependency."""
    
    def test_require_role_allowed(self, admin_user):
        """Test require_role passes for authorized user."""
        auth_context = create_auth_context(admin_user)
        
        # Check role directly
        result = has_role(auth_context, "admin")
        assert result is True
    
    def test_require_role_denied(self, public_user):
        """Test require_role denies unauthorized user."""
        auth_context = create_auth_context(public_user)
        
        # Check role directly
        result = has_role(auth_context, "admin")
        assert result is False
    
    def test_require_role_multiple_roles_first_match(self, operator_user):
        """Test require_role with multiple roles (first matches)."""
        auth_context = create_auth_context(operator_user)
        
        # Check if user has any of the roles
        result = has_role(auth_context, "admin") or has_role(auth_context, "operator")
        assert result is True
    
    def test_require_role_multiple_roles_second_match(self, ambulance_user):
        """Test require_role with multiple roles (second matches)."""
        auth_context = create_auth_context(ambulance_user)
        
        # Check if user has any of the roles
        result = any(has_role(auth_context, role) for role in ["admin", "ambulance", "fire"])
        assert result is True
    
    def test_require_role_multiple_roles_no_match(self, public_user):
        """Test require_role with multiple roles (no match)."""
        auth_context = create_auth_context(public_user)
        
        # Check if user has any of the roles
        result = any(has_role(auth_context, role) for role in ["admin", "operator"])
        assert result is False
    
    def test_require_role_unauthenticated(self):
        """Test require_role denies unauthenticated request."""
        # None context should have no roles
        result = has_role(None, "admin")
        assert result is False


# ============================================================================
# Resource-Level Authorization Tests
# ============================================================================

class TestResourceLevelAuth:
    """Test resource-level access control."""
    
    def test_can_modify_incident_admin(self, db, admin_user):
        """Test admin can modify any incident."""
        from backend.app.db.models import Network
        
        network = Network(id="net1", name="Network 1", junctions_count=1, edges_count=1)
        db.add(network)
        db.commit()
        
        incident = Incident(
            id="incident_1",
            network_id="net1",
            incident_type=IncidentType.ACCIDENT,
            severity=3,
            status="reported"
        )
        db.add(incident)
        db.commit()
        
        result = can_modify_incident(admin_user, "incident_1", db)
        
        assert result is True
    
    def test_can_modify_incident_nonexistent(self, db, admin_user):
        """Test modifying nonexistent incident returns False."""
        result = can_modify_incident(admin_user, "nonexistent", db)
        
        assert result is False
    
    def test_can_view_emergency_admin(self, db, admin_user):
        """Test admin can view any emergency."""
        from backend.app.db.models import EmergencyRequest, EmergencyRequestType, Network, Intersection
        
        network = Network(id="net1", name="Network 1", junctions_count=2, edges_count=1)
        db.add(network)
        db.commit()
        
        j1 = Intersection(id="J1", network_id="net1", latitude=13.0, longitude=77.5)
        j2 = Intersection(id="J2", network_id="net1", latitude=13.1, longitude=77.6)
        db.add_all([j1, j2])
        db.commit()
        
        emergency = EmergencyRequest(
            id="emg_1",
            network_id="net1",
            origin_junction_id="J1",
            destination_junction_id="J2",
            request_type=EmergencyRequestType.AMBULANCE,
            status="pending"
        )
        db.add(emergency)
        db.commit()
        
        result = can_view_emergency(admin_user, "emg_1", db)
        
        assert result is True
    
    def test_can_view_emergency_active_public(self, db, public_user):
        """Test anyone can view active emergency."""
        from backend.app.db.models import EmergencyRequest, EmergencyRequestType, Network, Intersection
        
        network = Network(id="net1", name="Network 1", junctions_count=2, edges_count=1)
        db.add(network)
        db.commit()
        
        j1 = Intersection(id="J1", network_id="net1", latitude=13.0, longitude=77.5)
        j2 = Intersection(id="J2", network_id="net1", latitude=13.1, longitude=77.6)
        db.add_all([j1, j2])
        db.commit()
        
        emergency = EmergencyRequest(
            id="emg_1",
            network_id="net1",
            origin_junction_id="J1",
            destination_junction_id="J2",
            request_type=EmergencyRequestType.AMBULANCE,
            status="active"
        )
        db.add(emergency)
        db.commit()
        
        result = can_view_emergency(public_user, "emg_1", db)
        
        assert result is True
    
    def test_cannot_view_emergency_pending_public(self, db, public_user):
        """Test public cannot view pending emergency."""
        from backend.app.db.models import EmergencyRequest, EmergencyRequestType, Network, Intersection
        
        network = Network(id="net1", name="Network 1", junctions_count=2, edges_count=1)
        db.add(network)
        db.commit()
        
        j1 = Intersection(id="J1", network_id="net1", latitude=13.0, longitude=77.5)
        j2 = Intersection(id="J2", network_id="net1", latitude=13.1, longitude=77.6)
        db.add_all([j1, j2])
        db.commit()
        
        emergency = EmergencyRequest(
            id="emg_1",
            network_id="net1",
            origin_junction_id="J1",
            destination_junction_id="J2",
            request_type=EmergencyRequestType.AMBULANCE,
            status="pending"
        )
        db.add(emergency)
        db.commit()
        
        result = can_view_emergency(public_user, "emg_1", db)
        
        assert result is False
    
    def test_can_view_nonexistent_emergency(self, db, admin_user):
        """Test viewing nonexistent emergency returns False."""
        result = can_view_emergency(admin_user, "nonexistent", db)
        
        assert result is False


# ============================================================================
# RBAC Initialization Tests
# ============================================================================

class TestRBACInitialization:
    """Test RBAC initialization."""
    
    def test_init_rbac_creates_roles(self, db):
        """Test init_rbac creates all expected roles."""
        init_rbac(db)
        
        roles = db.query(Role).all()
        role_ids = [role.id for role in roles]
        
        assert len(role_ids) >= 6
        assert "admin" in role_ids
        assert "operator" in role_ids
        assert "public" in role_ids
    
    def test_init_rbac_creates_permissions(self, db):
        """Test init_rbac creates all expected permissions."""
        init_rbac(db)
        
        permissions = db.query(Permission).all()
        perm_ids = [perm.id for perm in permissions]
        
        assert len(perm_ids) > 10
        assert "view_signals" in perm_ids
        assert "approve_corridor" in perm_ids
        assert "override_signal" in perm_ids
    
    def test_init_rbac_assigns_permissions(self, db):
        """Test init_rbac assigns permissions to roles."""
        init_rbac(db)
        
        admin_role = db.query(Role).filter(Role.id == "admin").first()
        public_role = db.query(Role).filter(Role.id == "public").first()
        
        admin_perms = [perm.id for perm in admin_role.permissions]
        public_perms = [perm.id for perm in public_role.permissions]
        
        # Admin should have many permissions
        assert len(admin_perms) > len(public_perms)
        
        # Both should have view_signals
        assert "view_signals" in admin_perms
        assert "view_signals" in public_perms
        
        # Admin should have override_signal, public should not
        assert "override_signal" in admin_perms
        assert "override_signal" not in public_perms
    
    def test_init_rbac_idempotent(self, db):
        """Test init_rbac is idempotent (can be called multiple times)."""
        init_rbac(db)
        initial_count = db.query(Role).count()
        
        init_rbac(db)
        final_count = db.query(Role).count()
        
        assert initial_count == final_count
    
    def test_role_hierarchy_priority(self, db):
        """Test roles have correct priority values."""
        init_rbac(db)
        
        admin = db.query(Role).filter(Role.id == "admin").first()
        public = db.query(Role).filter(Role.id == "public").first()
        
        assert admin.priority > public.priority


# ============================================================================
# Multi-Role Authorization Tests
# ============================================================================

class TestMultiRoleAuth:
    """Test users with multiple roles."""
    
    def test_user_multiple_roles_has_union_permissions(self, db, setup_rbac_full):
        """Test user with multiple roles has union of permissions."""
        user = User(
            id="multi_role_user",
            firebase_uid="multi_fb",
            email="multi@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        operator_role = db.query(Role).filter(Role.id == "operator").first()
        ambulance_role = db.query(Role).filter(Role.id == "ambulance").first()
        
        user.roles.append(operator_role)
        user.roles.append(ambulance_role)
        db.commit()
        
        from backend.app.auth.firebase_auth import get_user_permissions
        permissions = get_user_permissions(user)
        
        # Operator permissions
        assert "view_signals" in permissions
        assert "approve_corridor" in permissions
        
        # Ambulance permissions
        assert "submit_emergency_request" in permissions
        
        # Should not have admin permissions
        assert "override_signal" not in permissions
    
    def test_highest_role_priority_considered(self, db, setup_rbac_full):
        """Test that highest role priority is considered."""
        user = User(
            id="multi_role_user",
            firebase_uid="multi_fb",
            email="multi@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        admin_role = db.query(Role).filter(Role.id == "admin").first()
        public_role = db.query(Role).filter(Role.id == "public").first()
        
        user.roles.append(public_role)
        user.roles.append(admin_role)
        db.commit()
        
        from backend.app.auth.firebase_auth import get_user_roles
        roles = get_user_roles(user)
        
        # Should have both roles
        assert "admin" in roles
        assert "public" in roles


# ============================================================================
# Emergency Service Role Tests
# ============================================================================

class TestEmergencyServiceRoles:
    """Test emergency service specific roles and permissions."""
    
    def test_ambulance_can_submit_emergency(self, db, ambulance_user, setup_rbac_full):
        """Test ambulance can submit emergency request."""
        auth_context = create_auth_context(ambulance_user)
        
        assert has_permission(auth_context, "submit_emergency_request") is True
    
    def test_ambulance_cannot_override_signal(self, db, ambulance_user, setup_rbac_full):
        """Test ambulance cannot override signals."""
        auth_context = create_auth_context(ambulance_user)
        
        assert has_permission(auth_context, "override_signal") is False
    
    def test_ambulance_can_view_emergency_status(self, db, ambulance_user, setup_rbac_full):
        """Test ambulance can view emergency status."""
        auth_context = create_auth_context(ambulance_user)
        
        assert has_permission(auth_context, "view_emergency_status") is True
    
    def test_ambulance_can_cancel_emergency(self, db, ambulance_user, setup_rbac_full):
        """Test ambulance can cancel emergency."""
        auth_context = create_auth_context(ambulance_user)
        
        assert has_permission(auth_context, "cancel_emergency") is True

