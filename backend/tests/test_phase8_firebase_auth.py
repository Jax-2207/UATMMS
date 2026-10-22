"""
Phase 8: Firebase Authentication Tests
Tests token verification, user creation, role assignment, and Firebase integration.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend.app.db.models import Base, User, Role, Permission
from backend.app.auth.firebase_auth import (
    verify_id_token,
    get_or_create_user,
    get_user_by_uid,
    get_user_by_email,
    get_user_roles,
    get_user_permissions,
    set_user_custom_claims,
    add_role_to_user,
    remove_role_from_user,
    FirebaseAuthContext,
    get_auth_context_from_token,
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
def setup_rbac(db):
    """Setup default RBAC roles and permissions."""
    roles_data = [
        ("admin", 100),
        ("operator", 60),
        ("police", 50),
        ("public", 10),
    ]
    
    for role_id, priority in roles_data:
        role = Role(id=role_id, name=role_id.title(), priority=priority)
        db.add(role)
    
    perms_data = [
        ("view_signals", "signal", "view"),
        ("approve_corridor", "corridor", "approve"),
        ("override_signal", "signal", "override"),
        ("manage_users", "user", "manage"),
    ]
    
    for perm_id, resource, action in perms_data:
        perm = Permission(id=perm_id, name=perm_id.title(), resource=resource, action=action)
        db.add(perm)
    
    db.commit()
    
    # Assign permissions to roles
    admin_role = db.query(Role).filter(Role.id == "admin").first()
    operator_role = db.query(Role).filter(Role.id == "operator").first()
    public_role = db.query(Role).filter(Role.id == "public").first()
    
    view_signals = db.query(Permission).filter(Permission.id == "view_signals").first()
    approve_corridor = db.query(Permission).filter(Permission.id == "approve_corridor").first()
    override_signal = db.query(Permission).filter(Permission.id == "override_signal").first()
    manage_users = db.query(Permission).filter(Permission.id == "manage_users").first()
    
    # Admin has all permissions
    admin_role.permissions.extend([view_signals, approve_corridor, override_signal, manage_users])
    
    # Operator has some permissions
    operator_role.permissions.extend([view_signals, approve_corridor])
    
    # Public has only view permissions
    public_role.permissions.append(view_signals)
    
    db.commit()
    
    return db


@pytest.fixture
def mock_firebase_token():
    """Mock Firebase ID token."""
    return {
        "uid": "user_123",
        "email": "test@example.com",
        "email_verified": True,
        "name": "Test User",
        "iss": "https://securetoken.google.com/project-id",
        "aud": "project-id",
        "auth_time": 1234567890,
        "user_id": "user_123",
        "sub": "user_123",
        "iat": 1234567890,
        "exp": 1234567890 + 3600,
        "firebase": {
            "identities": {},
            "sign_in_provider": "anonymous"
        }
    }


# ============================================================================
# Token Verification Tests
# ============================================================================

class TestTokenVerification:
    """Test Firebase token verification."""
    
    @patch('backend.app.auth.firebase_auth.auth')
    def test_verify_valid_token(self, mock_auth, mock_firebase_token):
        """Test verifying a valid Firebase token."""
        mock_auth.verify_id_token.return_value = mock_firebase_token
        
        result = verify_id_token("valid_token_123")
        
        assert result is not None
        assert result["uid"] == "user_123"
        assert result["email"] == "test@example.com"
        mock_auth.verify_id_token.assert_called_once_with("valid_token_123")
    
    @patch('backend.app.auth.firebase_auth.auth')
    def test_verify_invalid_token(self, mock_auth):
        """Test verifying an invalid Firebase token."""
        mock_auth.verify_id_token.side_effect = ValueError("Invalid token")
        
        with pytest.raises(ValueError) as exc_info:
            verify_id_token("invalid_token_123")
        
        assert "Invalid or expired" in str(exc_info.value)
    
    @patch('backend.app.auth.firebase_auth.auth')
    def test_verify_expired_token(self, mock_auth):
        """Test verifying an expired Firebase token."""
        mock_auth.verify_id_token.side_effect = ValueError("Token expired")
        
        with pytest.raises(ValueError) as exc_info:
            verify_id_token("expired_token_123")
        
        assert "Invalid or expired" in str(exc_info.value)
    
    @patch('backend.app.auth.firebase_auth.auth')
    def test_verify_malformed_token(self, mock_auth):
        """Test verifying a malformed token."""
        mock_auth.verify_id_token.side_effect = ValueError("Malformed token")
        
        with pytest.raises(ValueError):
            verify_id_token("malformed")


# ============================================================================
# User Creation & Retrieval Tests
# ============================================================================

class TestUserCreation:
    """Test user creation from Firebase claims."""
    
    def test_create_new_user_from_claims(self, db, mock_firebase_token):
        """Test creating a new user from Firebase claims."""
        user = get_or_create_user(mock_firebase_token, db)
        
        assert user is not None
        assert user.firebase_uid == "user_123"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"
        assert user.is_verified is True
        assert user.is_active is True
    
    def test_get_existing_user(self, db, mock_firebase_token):
        """Test retrieving existing user (doesn't create duplicate)."""
        # Create first
        user1 = get_or_create_user(mock_firebase_token, db)
        user1_id = user1.id
        
        # Retrieve same user
        user2 = get_or_create_user(mock_firebase_token, db)
        
        assert user1_id == user2.id
        
        # Verify only one user in database
        all_users = db.query(User).all()
        assert len(all_users) == 1
    
    def test_user_last_login_updated(self, db, mock_firebase_token):
        """Test that last_login_at is updated on re-login."""
        user1 = get_or_create_user(mock_firebase_token, db)
        first_login = user1.last_login_at
        
        # Simulate time passing
        import time
        time.sleep(0.1)
        
        user2 = get_or_create_user(mock_firebase_token, db)
        second_login = user2.last_login_at
        
        assert second_login >= first_login
    
    def test_create_user_without_display_name(self, db):
        """Test creating user when display name is missing."""
        claims = {
            "uid": "user_no_name",
            "email": "noname@example.com",
            "email_verified": False
        }
        
        user = get_or_create_user(claims, db)
        
        assert user is not None
        assert user.firebase_uid == "user_no_name"
        assert user.display_name is None
    
    def test_create_user_unverified_email(self, db):
        """Test creating user with unverified email."""
        claims = {
            "uid": "user_unverified",
            "email": "unverified@example.com",
            "email_verified": False,
            "name": "Unverified User"
        }
        
        user = get_or_create_user(claims, db)
        
        assert user.is_verified is False


class TestUserRetrieval:
    """Test user lookup operations."""
    
    def test_get_user_by_uid(self, db):
        """Test retrieving user by Firebase UID."""
        user = User(
            id="user1",
            firebase_uid="fb_uid_1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        retrieved = get_user_by_uid("fb_uid_1", db)
        
        assert retrieved is not None
        assert retrieved.id == "user1"
    
    def test_get_user_by_email(self, db):
        """Test retrieving user by email."""
        user = User(
            id="user1",
            firebase_uid="fb_uid_1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        retrieved = get_user_by_email("test@example.com", db)
        
        assert retrieved is not None
        assert retrieved.firebase_uid == "fb_uid_1"
    
    def test_get_nonexistent_user_by_uid(self, db):
        """Test retrieving nonexistent user returns None."""
        result = get_user_by_uid("nonexistent_uid", db)
        
        assert result is None
    
    def test_get_nonexistent_user_by_email(self, db):
        """Test retrieving nonexistent email returns None."""
        result = get_user_by_email("nonexistent@example.com", db)
        
        assert result is None


# ============================================================================
# Role Assignment Tests
# ============================================================================

class TestRoleAssignment:
    """Test role assignment and retrieval."""
    
    def test_get_user_roles_empty(self, db):
        """Test getting roles for user with no roles."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        roles = get_user_roles(user)
        
        assert roles == []
    
    def test_get_user_roles_multiple(self, db, setup_rbac):
        """Test getting multiple roles for user."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        admin_role = db.query(Role).filter(Role.id == "admin").first()
        operator_role = db.query(Role).filter(Role.id == "operator").first()
        
        user.roles.append(admin_role)
        user.roles.append(operator_role)
        db.commit()
        
        roles = get_user_roles(user)
        
        assert len(roles) == 2
        assert "admin" in roles
        assert "operator" in roles
    
    @patch('backend.app.auth.firebase_auth.set_user_custom_claims')
    def test_add_role_to_user(self, mock_set_claims, db, setup_rbac):
        """Test adding a role to a user."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        result = add_role_to_user("user1", "admin", db)
        
        assert result is True
        
        db_user = db.query(User).filter(User.id == "user1").first()
        roles = get_user_roles(db_user)
        assert "admin" in roles
        mock_set_claims.assert_called_once()
    
    @patch('backend.app.auth.firebase_auth.set_user_custom_claims')
    def test_remove_role_from_user(self, mock_set_claims, db, setup_rbac):
        """Test removing a role from a user."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        admin_role = db.query(Role).filter(Role.id == "admin").first()
        user.roles.append(admin_role)
        db.commit()
        
        result = remove_role_from_user("user1", "admin", db)
        
        assert result is True
        
        db_user = db.query(User).filter(User.id == "user1").first()
        roles = get_user_roles(db_user)
        assert "admin" not in roles
    
    def test_add_nonexistent_role(self, db, setup_rbac):
        """Test adding nonexistent role fails gracefully."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        result = add_role_to_user("user1", "nonexistent", db)
        
        assert result is False
    
    def test_add_role_to_nonexistent_user(self, db, setup_rbac):
        """Test adding role to nonexistent user fails gracefully."""
        result = add_role_to_user("nonexistent", "admin", db)
        
        assert result is False


# ============================================================================
# Permission Tests
# ============================================================================

class TestUserPermissions:
    """Test permission retrieval through roles."""
    
    def test_get_permissions_no_roles(self, db):
        """Test getting permissions for user with no roles."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        permissions = get_user_permissions(user)
        
        assert permissions == set()
    
    def test_get_permissions_single_role(self, db, setup_rbac):
        """Test getting permissions from single role."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        public_role = db.query(Role).filter(Role.id == "public").first()
        user.roles.append(public_role)
        db.commit()
        
        permissions = get_user_permissions(user)
        
        assert "view_signals" in permissions
        assert "approve_corridor" not in permissions
    
    def test_get_permissions_multiple_roles(self, db, setup_rbac):
        """Test getting combined permissions from multiple roles."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        operator_role = db.query(Role).filter(Role.id == "operator").first()
        public_role = db.query(Role).filter(Role.id == "public").first()
        
        user.roles.append(operator_role)
        user.roles.append(public_role)
        db.commit()
        
        permissions = get_user_permissions(user)
        
        # Should have union of both roles
        assert "view_signals" in permissions
        assert "approve_corridor" in permissions
        assert "override_signal" not in permissions
    
    def test_get_permissions_admin_role(self, db, setup_rbac):
        """Test admin role has all permissions."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        admin_role = db.query(Role).filter(Role.id == "admin").first()
        user.roles.append(admin_role)
        db.commit()
        
        permissions = get_user_permissions(user)
        
        assert "view_signals" in permissions
        assert "approve_corridor" in permissions
        assert "override_signal" in permissions
        assert "manage_users" in permissions


# ============================================================================
# Custom Claims Tests
# ============================================================================

class TestCustomClaims:
    """Test Firebase custom claims management."""
    
    @patch('backend.app.auth.firebase_auth.auth')
    def test_set_user_custom_claims(self, mock_auth):
        """Test setting custom claims on Firebase user."""
        claims = {"roles": ["admin", "operator"]}
        
        set_user_custom_claims("user_123", claims)
        
        mock_auth.set_custom_user_claims.assert_called_once_with("user_123", claims)
    
    @patch('backend.app.auth.firebase_auth.auth')
    def test_set_custom_claims_failure(self, mock_auth):
        """Test setting custom claims failure handling."""
        mock_auth.set_custom_user_claims.side_effect = Exception("Firebase error")
        
        with pytest.raises(Exception):
            set_user_custom_claims("user_123", {"roles": ["admin"]})


# ============================================================================
# Auth Context Tests
# ============================================================================

class TestFirebaseAuthContext:
    """Test FirebaseAuthContext class."""
    
    def test_auth_context_creation(self, db, setup_rbac):
        """Test creating authentication context."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        admin_role = db.query(Role).filter(Role.id == "admin").first()
        user.roles.append(admin_role)
        db.commit()
        
        roles = get_user_roles(user)
        permissions = get_user_permissions(user)
        
        auth_context = FirebaseAuthContext(user, roles, permissions)
        
        assert auth_context.user.email == "test@example.com"
        assert auth_context.roles == ["admin"]
    
    def test_auth_context_has_permission(self, db, setup_rbac):
        """Test checking permission in auth context."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        public_role = db.query(Role).filter(Role.id == "public").first()
        user.roles.append(public_role)
        db.commit()
        
        roles = get_user_roles(user)
        permissions = get_user_permissions(user)
        
        auth_context = FirebaseAuthContext(user, roles, permissions)
        
        assert auth_context.has_permission("view_signals") is True
        assert auth_context.has_permission("override_signal") is False
    
    def test_auth_context_has_role(self, db, setup_rbac):
        """Test checking role in auth context."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        admin_role = db.query(Role).filter(Role.id == "admin").first()
        user.roles.append(admin_role)
        db.commit()
        
        roles = get_user_roles(user)
        permissions = get_user_permissions(user)
        
        auth_context = FirebaseAuthContext(user, roles, permissions)
        
        assert auth_context.has_role("admin") is True
        assert auth_context.has_role("public") is False
    
    def test_auth_context_repr(self, db, setup_rbac):
        """Test auth context string representation."""
        user = User(
            id="user1",
            firebase_uid="fb1",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        roles = get_user_roles(user)
        permissions = get_user_permissions(user)
        
        auth_context = FirebaseAuthContext(user, roles, permissions)
        repr_str = repr(auth_context)
        
        assert "test@example.com" in repr_str
        assert "FirebaseAuthContext" in repr_str


# ============================================================================
# Full Token-to-Context Flow Tests
# ============================================================================

class TestAuthContextFromToken:
    """Test complete authentication flow from token to context."""
    
    @patch('backend.app.auth.firebase_auth.verify_id_token')
    @patch('backend.app.auth.firebase_auth.get_or_create_user')
    def test_get_auth_context_from_token(self, mock_get_user, mock_verify_token, db, setup_rbac):
        """Test extracting auth context from token."""
        claims = {
            "uid": "user_123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User"
        }
        
        mock_verify_token.return_value = claims
        
        user = User(
            id="user_123",
            firebase_uid="user_123",
            email="test@example.com",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        
        admin_role = db.query(Role).filter(Role.id == "admin").first()
        user.roles.append(admin_role)
        db.commit()
        
        mock_get_user.return_value = user
        
        auth_context = get_auth_context_from_token("token_123", db)
        
        assert auth_context.user.email == "test@example.com"
        assert "admin" in auth_context.roles
        mock_verify_token.assert_called_once_with("token_123")
    
    @patch('backend.app.auth.firebase_auth.verify_id_token')
    def test_get_auth_context_invalid_token(self, mock_verify_token, db):
        """Test extracting auth context from invalid token fails."""
        mock_verify_token.side_effect = ValueError("Invalid token")
        
        with pytest.raises(ValueError):
            get_auth_context_from_token("invalid_token", db)

