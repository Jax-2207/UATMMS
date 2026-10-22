"""
UATMMS Firebase Authentication (Phase 8)
JWT token verification, user creation/lookup, and identity mapping.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth
from sqlalchemy.orm import Session
from backend.app.core.logging import logger
from backend.app.db.models import User

# ============================================================================
# Firebase Initialization
# ============================================================================

# Initialize Firebase (credentials from environment or file)
def init_firebase():
    """
    Initialize Firebase Admin SDK.
    Credentials should be from:
    1. Environment variable: FIREBASE_CREDENTIALS_JSON
    2. Or file path: FIREBASE_CREDENTIALS_FILE
    """
    try:
        if not firebase_admin._apps:
            cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            cred_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
            
            if cred_json:
                import json
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
            elif cred_file and os.path.exists(cred_file):
                cred = credentials.Certificate(cred_file)
            else:
                logger.warning("Firebase credentials not found. Using default credentials.")
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized ✓")
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        raise


# ============================================================================
# Token Verification
# ============================================================================

def verify_id_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Firebase ID token and return claims.
    
    Args:
        id_token: JWT token from Firebase client
    
    Returns:
        Token claims if valid, None if invalid
        Claims include: uid, email, email_verified, custom claims
    
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except ValueError as e:
        logger.warning(f"Invalid Firebase token: {e}")
        raise ValueError("Invalid or expired authentication token")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise


# ============================================================================
# User Management
# ============================================================================

def get_or_create_user(claims: Dict[str, Any], db: Session) -> User:
    """
    Get existing user or create new from Firebase claims.
    
    Args:
        claims: Decoded Firebase token claims
        db: Database session
    
    Returns:
        User instance (new or existing)
    """
    uid = claims.get('uid')
    email = claims.get('email')
    
    # Try to find existing user
    user = db.query(User).filter(User.firebase_uid == uid).first()
    
    if user:
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()
        return user
    
    # Create new user
    user = User(
        id=uid,
        firebase_uid=uid,
        email=email,
        display_name=claims.get('name'),
        is_verified=claims.get('email_verified', False),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"New user created: {email}")
    return user


def get_user_by_uid(uid: str, db: Session) -> Optional[User]:
    """Get user by Firebase UID."""
    return db.query(User).filter(User.firebase_uid == uid).first()


def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_roles(user: User) -> list[str]:
    """Get list of role IDs for user."""
    return [role.id for role in user.roles]


def get_user_permissions(user: User) -> set[str]:
    """Get set of all permissions for user (through roles)."""
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.id)
    return permissions


# ============================================================================
# Custom Claims & Role Assignment
# ============================================================================

def set_user_custom_claims(uid: str, claims: Dict[str, Any]) -> None:
    """
    Set custom claims on Firebase user.
    Used to encode roles in token for quick checks on client.
    
    Args:
        uid: Firebase UID
        claims: Custom claims dictionary (must be JSON-serializable)
    
    Note: Changes take effect on next login/token refresh
    """
    try:
        auth.set_custom_user_claims(uid, claims)
        logger.info(f"Custom claims set for user {uid}: {claims}")
    except Exception as e:
        logger.error(f"Failed to set custom claims: {e}")
        raise


def add_role_to_user(user_id: str, role_id: str, db: Session) -> bool:
    """
    Add a role to a user.
    
    Args:
        user_id: User ID (Firebase UID)
        role_id: Role ID
        db: Database session
    
    Returns:
        True if successful, False otherwise
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found: {user_id}")
            return False
        
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            logger.warning(f"Role not found: {role_id}")
            return False
        
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            logger.info(f"Role {role_id} added to user {user_id}")
            
            # Update Firebase custom claims
            roles = get_user_roles(user)
            set_user_custom_claims(user.firebase_uid, {"roles": roles})
        
        return True
    except Exception as e:
        logger.error(f"Failed to add role to user: {e}")
        db.rollback()
        return False


def remove_role_from_user(user_id: str, role_id: str, db: Session) -> bool:
    """Remove a role from a user."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False
        
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
            logger.info(f"Role {role_id} removed from user {user_id}")
            
            # Update Firebase custom claims
            roles = get_user_roles(user)
            set_user_custom_claims(user.firebase_uid, {"roles": roles})
        
        return True
    except Exception as e:
        logger.error(f"Failed to remove role from user: {e}")
        db.rollback()
        return False


# ============================================================================
# Middleware Integration
# ============================================================================

class FirebaseAuthContext:
    """Context object for authenticated request."""
    
    def __init__(self, user: User, roles: list[str], permissions: set[str]):
        self.user = user
        self.roles = roles
        self.permissions = permissions
    
    def has_permission(self, permission_id: str) -> bool:
        """Check if user has permission."""
        return permission_id in self.permissions
    
    def has_role(self, role_id: str) -> bool:
        """Check if user has role."""
        return role_id in self.roles
    
    def __repr__(self):
        return f"<FirebaseAuthContext user={self.user.email}, roles={self.roles}>"


def get_auth_context_from_token(id_token: str, db: Session) -> FirebaseAuthContext:
    """
    Extract authentication context from Firebase ID token.
    
    Args:
        id_token: JWT token
        db: Database session
    
    Returns:
        FirebaseAuthContext with user, roles, permissions
    
    Raises:
        ValueError: If token invalid or user not found
    """
    try:
        # Verify token
        claims = verify_id_token(id_token)
        
        # Get or create user
        user = get_or_create_user(claims, db)
        
        # Get roles and permissions
        roles = get_user_roles(user)
        permissions = get_user_permissions(user)
        
        return FirebaseAuthContext(user, roles, permissions)
    except Exception as e:
        logger.error(f"Auth context extraction failed: {e}")
        raise


# Import Role for type hints
from backend.app.db.models import Role
