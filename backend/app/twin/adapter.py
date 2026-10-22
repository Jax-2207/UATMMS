"""
UATMMS Phase 10: 3D Digital Twin Adapter
Converts SUMO simulation data to 3D Twin format for real-time visualization.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from backend.app.core.logging import logger


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class VehicleState:
    """Vehicle state in 3D space."""
    id: str
    type: str  # 'car', 'truck', 'ambulance', 'fire', 'police'
    x: float  # Longitude (simplified as X)
    y: float  # Latitude (simplified as Y)
    z: float  # Height (0 for ground level)
    rotation: float  # Heading (0-360 degrees)
    speed: float  # km/h
    lane: str  # Road lane identifier
    status: str  # 'normal', 'emergency', 'stopped'
    timestamp: float  # Unix timestamp


@dataclass
class SignalState:
    """Traffic signal state."""
    id: str
    phase: int  # 0-3 (phases)
    duration: float  # Duration in seconds
    remaining_time: float  # Time until next phase
    status: str  # 'active', 'inactive'
    timestamp: float  # Unix timestamp


@dataclass
class IncidentVisualization:
    """Incident visualization data."""
    id: str
    x: float
    y: float
    z: float
    severity: int  # 1-5
    type: str  # 'accident', 'congestion', etc.
    status: str  # 'reported', 'verified', 'cleared'
    timestamp: float


@dataclass
class RoadNetworkState:
    """Complete road network state."""
    vehicles: List[VehicleState]
    signals: List[SignalState]
    incidents: List[IncidentVisualization]
    timestamp: float
    sequence_number: int


# ============================================================================
# SUMO-to-Twin Adapter
# ============================================================================

class SumoToTwinAdapter:
    """Converts SUMO simulation data to 3D Twin format."""
    
    def __init__(self):
        """Initialize adapter."""
        self.sequence_number = 0
        self.last_state: Optional[RoadNetworkState] = None
    
    def convert_vehicle(self, sumo_vehicle: Dict[str, Any]) -> VehicleState:
        """
        Convert SUMO vehicle data to VehicleState.
        
        Args:
            sumo_vehicle: SUMO vehicle data dictionary
        
        Returns:
            VehicleState object
        """
        # Map SUMO vehicle type to Twin type
        type_mapping = {
            'car': 'car',
            'truck': 'truck',
            'bus': 'bus',
            'motorcycle': 'motorcycle',
            'emergency': 'ambulance',
            'fire': 'fire',
            'police': 'police'
        }
        
        vehicle_type = type_mapping.get(sumo_vehicle.get('type', 'car'), 'car')
        
        # Determine status based on context
        status = 'normal'
        if vehicle_type in ['ambulance', 'fire', 'police']:
            status = 'emergency'
        elif sumo_vehicle.get('speed', 0) < 0.1:
            status = 'stopped'
        
        return VehicleState(
            id=sumo_vehicle['id'],
            type=vehicle_type,
            x=sumo_vehicle['x'],
            y=sumo_vehicle['y'],
            z=0.0,  # Ground level
            rotation=sumo_vehicle.get('angle', 0.0),
            speed=sumo_vehicle.get('speed', 0.0),
            lane=sumo_vehicle.get('lane', 'unknown'),
            status=status,
            timestamp=datetime.utcnow().timestamp()
        )
    
    def convert_signal(self, signal_id: str, phase: int, duration: float, remaining: float) -> SignalState:
        """
        Convert traffic signal data to SignalState.
        
        Args:
            signal_id: Signal junction ID
            phase: Current phase (0-3)
            duration: Phase duration
            remaining: Remaining time in phase
        
        Returns:
            SignalState object
        """
        return SignalState(
            id=signal_id,
            phase=phase,
            duration=duration,
            remaining_time=remaining,
            status='active',
            timestamp=datetime.utcnow().timestamp()
        )
    
    def convert_incident(
        self,
        incident_id: str,
        x: float,
        y: float,
        severity: int,
        incident_type: str,
        status: str
    ) -> IncidentVisualization:
        """
        Convert incident data to IncidentVisualization.
        
        Args:
            incident_id: Incident ID
            x: X coordinate
            y: Y coordinate
            severity: Severity level (1-5)
            incident_type: Type of incident
            status: Current status
        
        Returns:
            IncidentVisualization object
        """
        return IncidentVisualization(
            id=incident_id,
            x=x,
            y=y,
            z=0.0,
            severity=max(1, min(5, severity)),  # Clamp 1-5
            type=incident_type,
            status=status,
            timestamp=datetime.utcnow().timestamp()
        )
    
    def create_state_snapshot(
        self,
        vehicles: List[Dict[str, Any]],
        signals: List[tuple],
        incidents: List[Dict[str, Any]]
    ) -> RoadNetworkState:
        """
        Create complete road network state snapshot.
        
        Args:
            vehicles: List of SUMO vehicle data
            signals: List of (signal_id, phase, duration, remaining) tuples
            incidents: List of incident data
        
        Returns:
            RoadNetworkState containing all converted data
        """
        self.sequence_number += 1
        
        converted_vehicles = [self.convert_vehicle(v) for v in vehicles]
        converted_signals = [
            self.convert_signal(sig_id, phase, duration, remaining)
            for sig_id, phase, duration, remaining in signals
        ]
        converted_incidents = [
            self.convert_incident(
                inc['id'], inc['x'], inc['y'],
                inc['severity'], inc['type'], inc['status']
            )
            for inc in incidents
        ]
        
        state = RoadNetworkState(
            vehicles=converted_vehicles,
            signals=converted_signals,
            incidents=converted_incidents,
            timestamp=datetime.utcnow().timestamp(),
            sequence_number=self.sequence_number
        )
        
        return state
    
    def create_delta_update(self, new_state: RoadNetworkState) -> Dict[str, Any]:
        """
        Create delta (only changes) from last state.
        
        Args:
            new_state: New road network state
        
        Returns:
            Delta update containing only changed data
        """
        # Check if this is the first update (no last_state yet)
        if not self.last_state:
            # First update - return full state
            self.last_state = new_state
            return {
                'type': 'full_update',
                'data': self.serialize_state(new_state),
                'sequence': new_state.sequence_number
            }
        
        # Calculate differences
        old_vehicle_ids = {v.id for v in self.last_state.vehicles}
        new_vehicle_ids = {v.id for v in new_state.vehicles}
        
        added = [v for v in new_state.vehicles if v.id not in old_vehicle_ids]
        removed = [v.id for v in self.last_state.vehicles if v.id not in new_vehicle_ids]
        
        # Updated vehicles (changed position/speed)
        updated = []
        for new_v in new_state.vehicles:
            old_v = next((v for v in self.last_state.vehicles if v.id == new_v.id), None)
            if old_v and (old_v.x != new_v.x or old_v.y != new_v.y or old_v.speed != new_v.speed):
                updated.append(new_v)
        
        # Update last state for next iteration
        self.last_state = new_state
        
        return {
            'type': 'delta_update',
            'sequence': new_state.sequence_number,
            'added_vehicles': [self.serialize_vehicle(v) for v in added],
            'removed_vehicles': removed,
            'updated_vehicles': [self.serialize_vehicle(v) for v in updated],
            'signals': [self.serialize_signal(s) for s in new_state.signals],
            'incidents': [self.serialize_incident(i) for i in new_state.incidents]
        }
    
    @staticmethod
    def serialize_state(state: RoadNetworkState) -> Dict[str, Any]:
        """Serialize complete state to JSON-compatible format."""
        return {
            'vehicles': [SumoToTwinAdapter.serialize_vehicle(v) for v in state.vehicles],
            'signals': [SumoToTwinAdapter.serialize_signal(s) for s in state.signals],
            'incidents': [SumoToTwinAdapter.serialize_incident(i) for i in state.incidents],
            'timestamp': state.timestamp,
            'sequence': state.sequence_number
        }
    
    @staticmethod
    def serialize_vehicle(vehicle: VehicleState) -> Dict[str, Any]:
        """Serialize vehicle to JSON."""
        return asdict(vehicle)
    
    @staticmethod
    def serialize_signal(signal: SignalState) -> Dict[str, Any]:
        """Serialize signal to JSON."""
        return asdict(signal)
    
    @staticmethod
    def serialize_incident(incident: IncidentVisualization) -> Dict[str, Any]:
        """Serialize incident to JSON."""
        return asdict(incident)


# ============================================================================
# Binary Protocol
# ============================================================================

class BinaryProtocol:
    """Binary protocol for efficient state transmission."""
    
    # Frame types
    FRAME_FULL_STATE = 0x01
    FRAME_DELTA = 0x02
    FRAME_VEHICLE_ADDED = 0x03
    FRAME_VEHICLE_REMOVED = 0x04
    FRAME_SIGNAL_UPDATE = 0x05
    FRAME_INCIDENT_UPDATE = 0x06
    
    @staticmethod
    def encode_vehicle(vehicle: VehicleState) -> bytes:
        """
        Encode vehicle state to binary.
        
        Format:
        - ID (16 bytes): vehicle ID
        - Type (1 byte): vehicle type
        - Position (12 bytes): x, y, z (float32 each)
        - Rotation (4 bytes): heading (float32)
        - Speed (4 bytes): speed (float32)
        - Status (1 byte): status code
        
        Total: 38 bytes per vehicle
        """
        data = bytearray()
        
        # ID (padded to 16 bytes)
        vehicle_id = vehicle.id.encode('utf-8')[:16]
        data.extend(vehicle_id.ljust(16, b'\0'))
        
        # Type (1 byte)
        type_map = {'car': 0, 'truck': 1, 'ambulance': 2, 'fire': 3, 'police': 4, 'bus': 5}
        data.append(type_map.get(vehicle.type, 0))
        
        # Position (12 bytes: 3 x float32)
        import struct
        data.extend(struct.pack('fff', vehicle.x, vehicle.y, vehicle.z))
        
        # Rotation (4 bytes: float32)
        data.extend(struct.pack('f', vehicle.rotation))
        
        # Speed (4 bytes: float32)
        data.extend(struct.pack('f', vehicle.speed))
        
        # Status (1 byte)
        status_map = {'normal': 0, 'emergency': 1, 'stopped': 2}
        data.append(status_map.get(vehicle.status, 0))
        
        return bytes(data)
    
    @staticmethod
    def decode_vehicle(data: bytes) -> Optional[VehicleState]:
        """Decode vehicle state from binary."""
        if len(data) < 38:
            logger.warning(f"Invalid vehicle data length: {len(data)}")
            return None
        
        try:
            import struct
            
            # Decode
            vehicle_id = data[0:16].rstrip(b'\0').decode('utf-8')
            type_map_inv = {0: 'car', 1: 'truck', 2: 'ambulance', 3: 'fire', 4: 'police', 5: 'bus'}
            vehicle_type = type_map_inv.get(data[16], 'car')
            
            x, y, z = struct.unpack('fff', data[17:29])
            rotation = struct.unpack('f', data[29:33])[0]
            speed = struct.unpack('f', data[33:37])[0]
            
            status_map_inv = {0: 'normal', 1: 'emergency', 2: 'stopped'}
            status = status_map_inv.get(data[37], 'normal')
            
            return VehicleState(
                id=vehicle_id,
                type=vehicle_type,
                x=x, y=y, z=z,
                rotation=rotation,
                speed=speed,
                lane='unknown',
                status=status,
                timestamp=datetime.utcnow().timestamp()
            )
        except Exception as e:
            logger.error(f"Error decoding vehicle: {e}")
            return None
