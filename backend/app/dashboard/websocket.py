"""
UATMMS Phase 9: WebSocket Backend
Real-time dashboard data streaming via WebSocket connections.
"""

import json
import asyncio
from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.auth.firebase_auth import get_auth_context_from_token, FirebaseAuthContext
from backend.app.dashboard.serializers import (
    serialize_network_state,
    serialize_traffic_metrics,
    serialize_incidents,
    serialize_emergencies,
)


# ============================================================================
# Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_contexts: Dict[str, FirebaseAuthContext] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, auth_context: FirebaseAuthContext):
        """Register a new WebSocket connection."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.user_contexts[user_id] = auth_context
        
        logger.info(f"WebSocket connected: {user_id} (total: {len(self.active_connections[user_id])})")
    
    def disconnect(self, user_id: str, websocket: WebSocket):
        """Unregister a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.user_contexts:
                    del self.user_contexts[user_id]
        
        logger.info(f"WebSocket disconnected: {user_id}")
    
    async def broadcast_to_user(
        self,
        user_id: str,
        message: Dict,
        exclude_websocket: WebSocket = None
    ):
        """Send message to all WebSocket connections for a user."""
        if user_id not in self.active_connections:
            return
        
        disconnected = []
        
        for websocket in self.active_connections[user_id]:
            if websocket == exclude_websocket:
                continue
            
            try:
                await websocket.send_json(message)
            except RuntimeError:
                disconnected.append(websocket)
        
        # Clean up disconnected
        for ws in disconnected:
            self.disconnect(user_id, ws)
    
    async def broadcast_to_all(self, message: Dict, exclude_websocket: WebSocket = None):
        """Broadcast message to all connected users."""
        for user_id in list(self.active_connections.keys()):
            await self.broadcast_to_user(user_id, message, exclude_websocket)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_connected_users(self) -> List[str]:
        """Get list of connected user IDs."""
        return list(self.active_connections.keys())


# Global instance
connection_manager = ConnectionManager()


# ============================================================================
# WebSocket Message Types
# ============================================================================

class MessageType:
    """Message type constants."""
    
    # Client to Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"
    
    # Server to Client
    PONG = "pong"
    NETWORK_STATE = "network_state"
    TRAFFIC_METRICS = "traffic_metrics"
    INCIDENTS = "incidents"
    EMERGENCIES = "emergencies"
    SIGNAL_UPDATE = "signal_update"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


# ============================================================================
# WebSocket Handler
# ============================================================================

async def websocket_handler(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Main WebSocket handler for dashboard connections.
    
    Args:
        websocket: WebSocket connection
        token: Firebase ID token
        db: Database session
    """
    
    # Authenticate user
    try:
        auth_context = get_auth_context_from_token(token, db)
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    user_id = auth_context.user.id
    
    # Connect
    await connection_manager.connect(websocket, user_id, auth_context)
    
    # Send initial connection message
    await websocket.send_json({
        "type": MessageType.HEARTBEAT,
        "message": "Connected to UATMMS Dashboard",
        "timestamp": datetime.utcnow().isoformat(),
        "user": auth_context.user.email,
        "roles": auth_context.roles,
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            logger.debug(f"WebSocket message from {user_id}: {message_type}")
            
            if message_type == MessageType.PING:
                await websocket.send_json({
                    "type": MessageType.PONG,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == MessageType.SUBSCRIBE:
                # Subscribe to specific data streams
                channels = data.get("channels", [])
                await handle_subscribe(websocket, user_id, channels, auth_context, db)
            
            elif message_type == MessageType.UNSUBSCRIBE:
                # Unsubscribe from channels
                channels = data.get("channels", [])
                logger.info(f"User {user_id} unsubscribed from {channels}")
    
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id, websocket)
        logger.info(f"WebSocket disconnected: {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        connection_manager.disconnect(user_id, websocket)


async def handle_subscribe(
    websocket: WebSocket,
    user_id: str,
    channels: List[str],
    auth_context: FirebaseAuthContext,
    db: Session
):
    """Handle channel subscription."""
    
    for channel in channels:
        try:
            if channel == "network_state":
                await send_network_state(websocket, auth_context, db)
            
            elif channel == "traffic_metrics":
                await send_traffic_metrics(websocket, auth_context, db)
            
            elif channel == "incidents":
                await send_incidents(websocket, auth_context, db)
            
            elif channel == "emergencies":
                await send_emergencies(websocket, auth_context, db)
            
            else:
                await websocket.send_json({
                    "type": MessageType.ERROR,
                    "message": f"Unknown channel: {channel}"
                })
        
        except Exception as e:
            logger.error(f"Error sending {channel}: {e}")
            await websocket.send_json({
                "type": MessageType.ERROR,
                "message": f"Error fetching {channel}: {str(e)}"
            })


async def send_network_state(
    websocket: WebSocket,
    auth_context: FirebaseAuthContext,
    db: Session
):
    """Send network state to client."""
    try:
        state = serialize_network_state(db, auth_context)
        await websocket.send_json({
            "type": MessageType.NETWORK_STATE,
            "data": state,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error sending network state: {e}")
        raise


async def send_traffic_metrics(
    websocket: WebSocket,
    auth_context: FirebaseAuthContext,
    db: Session
):
    """Send traffic metrics to client."""
    try:
        metrics = serialize_traffic_metrics(db, auth_context)
        await websocket.send_json({
            "type": MessageType.TRAFFIC_METRICS,
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error sending traffic metrics: {e}")
        raise


async def send_incidents(
    websocket: WebSocket,
    auth_context: FirebaseAuthContext,
    db: Session
):
    """Send incidents to client."""
    try:
        incidents = serialize_incidents(db, auth_context)
        await websocket.send_json({
            "type": MessageType.INCIDENTS,
            "data": incidents,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error sending incidents: {e}")
        raise


async def send_emergencies(
    websocket: WebSocket,
    auth_context: FirebaseAuthContext,
    db: Session
):
    """Send emergencies to client."""
    try:
        emergencies = serialize_emergencies(db, auth_context)
        await websocket.send_json({
            "type": MessageType.EMERGENCIES,
            "data": emergencies,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error sending emergencies: {e}")
        raise


# ============================================================================
# Broadcast Helpers
# ============================================================================

async def broadcast_network_update(db: Session):
    """Broadcast network state update to all connected clients."""
    try:
        state = serialize_network_state(db)
        message = {
            "type": MessageType.NETWORK_STATE,
            "data": state,
            "timestamp": datetime.utcnow().isoformat()
        }
        await connection_manager.broadcast_to_all(message)
    except Exception as e:
        logger.error(f"Error broadcasting network update: {e}")


async def broadcast_incident_update(db: Session, incident_id: str):
    """Broadcast incident update to all connected clients."""
    try:
        from backend.app.db.models import Incident
        
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if incident:
            message = {
                "type": MessageType.INCIDENTS,
                "data": {
                    "incident": {
                        "id": incident.id,
                        "status": incident.status,
                        "severity": incident.severity,
                        "type": incident.incident_type.value,
                        "timestamp": incident.created_at.isoformat()
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            await connection_manager.broadcast_to_all(message)
    except Exception as e:
        logger.error(f"Error broadcasting incident update: {e}")


async def broadcast_emergency_update(db: Session, emergency_id: str):
    """Broadcast emergency update to all connected clients."""
    try:
        from backend.app.db.models import EmergencyRequest
        
        emergency = db.query(EmergencyRequest).filter(EmergencyRequest.id == emergency_id).first()
        if emergency:
            message = {
                "type": MessageType.EMERGENCIES,
                "data": {
                    "emergency": {
                        "id": emergency.id,
                        "status": emergency.status,
                        "type": emergency.request_type.value,
                        "timestamp": emergency.created_at.isoformat()
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            await connection_manager.broadcast_to_all(message)
    except Exception as e:
        logger.error(f"Error broadcasting emergency update: {e}")
