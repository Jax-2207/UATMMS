"""
UATMMS Audit Logging (Phase 8)
Immutable audit trail for all mutations and critical operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.core.logging import logger
from backend.app.db.models import AuditEvent, User
import uuid


class AuditLogger:
    """Handles all audit event logging."""
    
    @staticmethod
    def log_action(
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Optional[AuditEvent]:
        """
        Log an audit event (mutation or critical operation).
        
        Args:
            user_id: User performing action
            action: Action name (e.g., 'approve_corridor', 'create_incident')
            resource_type: Resource being modified (e.g., 'emergency_request')
            resource_id: ID of resource
            before_state: Previous state (if applicable)
            after_state: New state (if applicable)
            ip_address: Client IP for tracking
            db: Database session
        
        Returns:
            Created AuditEvent, or None if logging failed
        """
        if not db:
            logger.warning("Audit logging attempted without database session")
            return None
        
        try:
            event_id = f"{action}_{resource_id}_{uuid.uuid4().hex[:8]}"
            
            audit_event = AuditEvent(
                id=event_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                before_state=before_state,
                after_state=after_state,
                ip_address=ip_address,
                timestamp=datetime.utcnow()
            )
            
            db.add(audit_event)
            db.commit()
            
            logger.info(
                f"Audit: user={user_id} action={action} "
                f"resource={resource_type}:{resource_id}"
            )
            
            return audit_event
        except Exception as e:
            logger.error(f"Audit event logging failed: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def log_permission_check(
        user_id: str,
        permission_id: str,
        allowed: bool,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        db: Optional[Session] = None
    ) -> None:
        """Log permission checks (for security auditing)."""
        if not db:
            return
        
        try:
            action = f"permission_check_{permission_id}"
            resource_type = "permission"
            
            audit_event = AuditEvent(
                id=f"{action}_{resource_id}_{int(datetime.utcnow().timestamp())}",
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id or "N/A",
                after_state={"allowed": allowed},
                ip_address=ip_address,
                timestamp=datetime.utcnow()
            )
            
            db.add(audit_event)
            db.commit()
        except Exception as e:
            logger.error(f"Permission check audit logging failed: {e}")


# ============================================================================
# Specific Audit Operations
# ============================================================================

def audit_emergency_request_change(
    user_id: str,
    emergency_id: str,
    old_status: str,
    new_status: str,
    db: Session
) -> None:
    """Log emergency request status change."""
    AuditLogger.log_action(
        user_id=user_id,
        action=f"emergency_status_change_{old_status}_to_{new_status}",
        resource_type="emergency_request",
        resource_id=emergency_id,
        before_state={"status": old_status},
        after_state={"status": new_status},
        db=db
    )


def audit_incident_verification(
    user_id: str,
    incident_id: str,
    verified: bool,
    db: Session
) -> None:
    """Log incident verification action."""
    AuditLogger.log_action(
        user_id=user_id,
        action="verify_incident" if verified else "reject_incident",
        resource_type="incident",
        resource_id=incident_id,
        after_state={"verified": verified},
        db=db
    )


def audit_corridor_approval(
    user_id: str,
    emergency_id: str,
    corridor: list[str],
    approved: bool,
    db: Session
) -> None:
    """Log corridor approval action."""
    AuditLogger.log_action(
        user_id=user_id,
        action="approve_corridor" if approved else "reject_corridor",
        resource_type="emergency_request",
        resource_id=emergency_id,
        after_state={
            "corridor": corridor,
            "approved": approved
        },
        db=db
    )


def audit_model_promotion(
    user_id: str,
    model_id: str,
    promoted: bool,
    metrics: Dict[str, Any],
    db: Session
) -> None:
    """Log model promotion decision."""
    AuditLogger.log_action(
        user_id=user_id,
        action="promote_model" if promoted else "reject_model",
        resource_type="model_version",
        resource_id=model_id,
        after_state={
            "promoted": promoted,
            "metrics": metrics
        },
        db=db
    )


def audit_user_role_change(
    user_id: str,
    target_user_id: str,
    role_id: str,
    added: bool,
    db: Session
) -> None:
    """Log user role assignment/removal."""
    AuditLogger.log_action(
        user_id=user_id,
        action=f"{'add' if added else 'remove'}_role_to_user",
        resource_type="user",
        resource_id=target_user_id,
        after_state={
            "role": role_id,
            "action": "add" if added else "remove"
        },
        db=db
    )


def audit_signal_override(
    user_id: str,
    junction_id: str,
    old_phase: int,
    new_phase: int,
    reason: str,
    db: Session
) -> None:
    """Log manual signal override."""
    AuditLogger.log_action(
        user_id=user_id,
        action="override_signal",
        resource_type="signal",
        resource_id=junction_id,
        before_state={"phase": old_phase},
        after_state={"phase": new_phase, "reason": reason},
        db=db
    )


# ============================================================================
# Audit Queries
# ============================================================================

def get_audit_trail(
    resource_id: str,
    db: Session,
    limit: int = 100
) -> list[AuditEvent]:
    """Get audit trail for a specific resource."""
    return db.query(AuditEvent)\
        .filter(AuditEvent.resource_id == resource_id)\
        .order_by(AuditEvent.timestamp.desc())\
        .limit(limit)\
        .all()


def get_user_audit_history(
    user_id: str,
    db: Session,
    action_filter: Optional[str] = None,
    limit: int = 100
) -> list[AuditEvent]:
    """Get audit history for a specific user."""
    query = db.query(AuditEvent).filter(AuditEvent.user_id == user_id)
    
    if action_filter:
        query = query.filter(AuditEvent.action.like(f"%{action_filter}%"))
    
    return query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()


def get_recent_actions(
    action: str,
    db: Session,
    limit: int = 50
) -> list[AuditEvent]:
    """Get recent occurrences of a specific action."""
    return db.query(AuditEvent)\
        .filter(AuditEvent.action == action)\
        .order_by(AuditEvent.timestamp.desc())\
        .limit(limit)\
        .all()
