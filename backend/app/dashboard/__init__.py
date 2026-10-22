"""
UATMMS Phase 9: Dashboard Module
Real-time Command Centre dashboard with WebSocket streaming.
"""

from backend.app.dashboard.websocket import (
    ConnectionManager,
    connection_manager,
    websocket_handler,
    broadcast_network_update,
    broadcast_incident_update,
    broadcast_emergency_update,
    MessageType
)

from backend.app.dashboard.serializers import (
    serialize_network_state,
    serialize_traffic_metrics,
    serialize_incidents,
    serialize_emergencies,
    serialize_dashboard_summary,
    create_delta_update
)

__all__ = [
    "ConnectionManager",
    "connection_manager",
    "websocket_handler",
    "broadcast_network_update",
    "broadcast_incident_update",
    "broadcast_emergency_update",
    "MessageType",
    "serialize_network_state",
    "serialize_traffic_metrics",
    "serialize_incidents",
    "serialize_emergencies",
    "serialize_dashboard_summary",
    "create_delta_update"
]
