"""
UATMMS Role-Based Access Control (RBAC) (Phase 8)
Permission checks, decorators, and authorization logic.
"""

from typing import Optional, Callable, Any
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.core.logging import logger
from backend.app.db.models import User, Role, Permission
from backend.app.auth.firebase_auth import FirebaseAuthContext

# ============================================================================
# RBAC Policy
# ============================================================================

# Role hierarchy
ROLE_HIERARCHY = {
    'admin': 100,        # Highest privilege
    'operator': 60,
    'police': 50,
    'ambulance': 40,
    'fire': 40,
    'public': 10,        # Lowest privilege
}

# Permission definitions
PERMISSIONS_MATRIX = {
    # Network/Signal Viewing
    'view_signals': {'roles': ['admin', 'operator', 'police', 'public']},
    'view_network': {'roles': ['admin', 'operator', 'police', 'public']},
    'view_metrics': {'roles': ['admin', 'operator', 'police']},
    
    # Signal Control
    'approve_phase_change': {'roles': ['admin', 'operator']},
    'override_signal': {'roles': ['admin']},
    
    # Emergency Management
    'submit_emergency_request': {'roles': ['ambulance', 'fire', 'police']},
    'view_emergency_status': {'roles': ['ambulance', 'fire', 'police', 'hospital']},
    'approve_corridor': {'roles': ['admin', 'operator']},
    'cancel_emergency': {'roles': ['admin', 'operator', 'ambulance', 'fire', 'police']},
    
    # Incident Management
    'report_incident': {'roles': ['admin', 'operator', 'police', 'public']},
    'verify_incident': {'roles': ['admin', 'police']},
    'resolve_incident': {'roles': ['admin', 'operator', 'police']},
    
    # User Management
    'manage_users': {'roles': ['admin']},
    'manage_roles': {'roles': ['admin']},
    'view_audit_log': {'roles': ['admin']},
    
    # Analytics & RL
    'view_analytics': {'roles': ['admin', 'operator']},
    'deploy_model': {'roles': ['admin']},
    'promote_model': {'roles': ['admin']},
}


# ============================================================================
# Authorization Checks
# ============================================================================

def has_permission(auth_context: FirebaseAuthContext, permission_id: str) -> bool:
    """
    Check if user has specific permission.
    
    Args:
        auth_context: Authentication context with user roles/permissions
        permission_id: Permission ID
    
    Returns:
        True if user has permission
    """
    if not auth_context:
        return False
    
    return auth_context.has_permission(permission_id)


def has_role(auth_context: FirebaseAuthContext, role_id: str) -> bool:
    """Check if user has specific role."""
    if not auth_context:
        return False
    
    return auth_context.has_role(role_id)


def is_admin(auth_context: FirebaseAuthContext) -> bool:
    """Check if user is admin."""
    return has_role(auth_context, 'admin')


def require_permission(permission_id: str) -> Callable:
    """
    FastAPI dependency for permission-based access control.
    
    Usage:
        @app.post("/corridors/approve")
        def approve_corridor(
            auth_context: FirebaseAuthContext = Depends(require_permission("approve_corridor")),
            db: Session = Depends(get_db)
        ):
            ...
    
    Raises:
        HTTPException 403: If user doesn't have permission
    """
    async def permission_check(
        auth_context: Optional[FirebaseAuthContext] = None
    ) -> FirebaseAuthContext:
        if not auth_context:
            logger.warning(f"Unauthenticated request to protected resource")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if not has_permission(auth_context, permission_id):
            logger.warning(
                f"User {auth_context.user.email} lacks permission {permission_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_id}"
            )
        
        return auth_context
    
    return permission_check


def require_role(*role_ids: str) -> Callable:
    """
    FastAPI dependency for role-based access control.
    
    Usage:
        @app.post("/admin/users")
        def manage_users(
            auth_context: FirebaseAuthContext = Depends(require_role("admin")),
        ):
            ...
    
    Raises:
        HTTPException 403: If user doesn't have any of the specified roles
    """
    async def role_check(
        auth_context: Optional[FirebaseAuthContext] = None
    ) -> FirebaseAuthContext:
        if not auth_context:
            logger.warning("Unauthenticated request to role-protected resource")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if not any(has_role(auth_context, role_id) for role_id in role_ids):
            logger.warning(
                f"User {auth_context.user.email} lacks required roles: {role_ids}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role: requires one of {role_ids}"
            )
        
        return auth_context
    
    return role_check


# ============================================================================
# Resource-Level Authorization
# ============================================================================

def can_modify_incident(user: User, incident_id: str, db: Session) -> bool:
    """
    Check if user can modify an incident.
    - Admin: can modify any
    - Police: can verify/modify
    - Operator: can acknowledge
    """
    from backend.app.db.models import Incident
    
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return False
    
    # Admin can always modify
    if has_role(FirebaseAuthContext(user, [r.id for r in user.roles], set()), 'admin'):
        return True
    
    # Police can verify/modify
    if has_role(FirebaseAuthContext(user, [r.id for r in user.roles], set()), 'police'):
        return incident.status in ['reported', 'verified']
    
    return False


def can_view_emergency(user: User, emergency_id: str, db: Session) -> bool:
    """
    Check if user can view emergency request details.
    - Submitter of request can view
    - Operator/admin can view
    - Other emergency types can view active requests
    """
    from backend.app.db.models import EmergencyRequest
    
    emergency = db.query(EmergencyRequest).filter(
        EmergencyRequest.id == emergency_id
    ).first()
    
    if not emergency:
        return False
    
    roles = [r.id for r in user.roles]
    
    # Admin/operator can view all
    if 'admin' in roles or 'operator' in roles:
        return True
    
    # Active emergencies can be viewed by all (situational awareness)
    if emergency.status == 'active':
        return True
    
    return False


# ============================================================================
# Permission Initialization
# ============================================================================

def init_rbac(db: Session) -> None:
    """
    Initialize RBAC schema with default roles and permissions.
    Called once during application startup.
    """
    try:
        # Create roles
        role_ids = list(ROLE_HIERARCHY.keys())
        for role_id in role_ids:
            if not db.query(Role).filter(Role.id == role_id).first():
                role = Role(
                    id=role_id,
                    name=role_id.replace('_', ' ').title(),
                    priority=ROLE_HIERARCHY[role_id]
                )
                db.add(role)
        
        db.commit()
        
        # Create permissions
        for perm_id, perm_config in PERMISSIONS_MATRIX.items():
            if not db.query(Permission).filter(Permission.id == perm_id).first():
                resource, action = perm_id.rsplit('_', 1) if '_' in perm_id else (perm_id, 'view')
                permission = Permission(
                    id=perm_id,
                    name=perm_id.replace('_', ' ').title(),
                    resource=resource,
                    action=action
                )
                db.add(permission)
        
        db.commit()
        
        # Assign permissions to roles
        for perm_id, perm_config in PERMISSIONS_MATRIX.items():
            permission = db.query(Permission).filter(Permission.id == perm_id).first()
            for role_id in perm_config['roles']:
                role = db.query(Role).filter(Role.id == role_id).first()
                if permission and role and permission not in role.permissions:
                    role.permissions.append(permission)
        
        db.commit()
        logger.info(f"RBAC initialized: {len(role_ids)} roles, {len(PERMISSIONS_MATRIX)} permissions")
    except Exception as e:
        logger.error(f"RBAC initialization failed: {e}")
        db.rollback()
        raise


# ============================================================================
# Audit Decorator
# ============================================================================

def audit_action(action_name: str, resource_type: str):
    """
    Decorator to audit mutations.
    
    Usage:
        @audit_action("approve_corridor", "emergency_request")
        def approve_corridor(auth_context, request_id, db):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(auth_context: FirebaseAuthContext, *args, db: Session = None, **kwargs):
            # Execute function
            result = func(auth_context, *args, db=db, **kwargs)
            
            # Log audit event
            try:
                from backend.app.db.models import AuditEvent
                
                resource_id = kwargs.get('resource_id') or (args[0] if args else 'unknown')
                
                audit_event = AuditEvent(
                    id=f"{action_name}_{resource_id}_{int(datetime.utcnow().timestamp())}",
                    user_id=auth_context.user.id,
                    action=action_name,
                    resource_type=resource_type,
                    resource_id=str(resource_id),
                    after_state={"result": str(result)},
                    timestamp=datetime.utcnow()
                )
                db.add(audit_event)
                db.commit()
            except Exception as e:
                logger.error(f"Audit logging failed: {e}")
            
            return result
        
        return wrapper
    return decorator


from datetime import datetime
