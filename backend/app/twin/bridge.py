"""
Phase 10: 3D Digital Twin - Visualization Bridge
Streams 3D scene state (vehicle positions, signal colors, incidents) to rendering clients.
Supports WebSocket and REST polling modes.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

from backend.app.core.logging import logger


# ============================================================================
# Signal Color & Vehicle Model Enums
# ============================================================================

class SignalColor(str, Enum):
    """Traffic signal display color."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class VehicleModel(str, Enum):
    """3D vehicle model type for rendering."""
    CAR = "car"
    TRUCK = "truck"
    BUS = "bus"
    AUTO_RICKSHAW = "auto_rickshaw"
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    POLICE_VEHICLE = "police_vehicle"
    MOTORCYCLE = "motorcycle"


class IncidentSeverityColor(str, Enum):
    """Incident visualization color by severity."""
    LOW = "yellow"        # Severity 1
    MODERATE = "orange"   # Severity 2
    HIGH = "red"          # Severity 3
    CRITICAL = "darkred"  # Severity 4-5


# ============================================================================
# 3D Scene State Classes
# ============================================================================

@dataclass
class Vehicle3D:
    """Vehicle data formatted for 3D renderer."""
    id: str
    model: str  # VehicleModel enum value
    x: float
    y: float
    z: float
    rotation_degrees: float  # Heading 0-360
    speed_kmh: float
    status: str  # 'normal', 'emergency', 'stopped'
    color: str  # CSS color (default, emergency override)
    timestamp: float


@dataclass
class Signal3D:
    """Traffic signal state for 3D renderer."""
    id: str
    x: float
    y: float
    z: float
    color: str  # SignalColor enum value
    phase: int  # 0-3
    timestamp: float


@dataclass
class Incident3D:
    """Incident marker for 3D visualization."""
    id: str
    x: float
    y: float
    z: float
    severity: int  # 1-5
    severity_color: str  # Color mapping
    type: str
    status: str  # 'reported', 'verified', 'cleared'
    timestamp: float


@dataclass
class Scene3D:
    """Complete 3D scene state snapshot."""
    vehicles: List[Vehicle3D]
    signals: List[Signal3D]
    incidents: List[Incident3D]
    timestamp: float
    sequence: int
    frame_id: str  # UUID for frame tracking


# ============================================================================
# 3D Bridge - Formats Twin State for 3D Rendering
# ============================================================================

class TwinBridge3D:
    """
    Converts RoadNetworkState and control system data to 3D scene format.
    Manages frame sequencing, interpolation hints, and animation data.
    """
    
    def __init__(self):
        """Initialize bridge."""
        self.frame_counter = 0
        self.last_scene: Optional[Scene3D] = None
        self.vehicle_trajectories: Dict[str, List[tuple]] = {}  # id -> [(x,y,z,t), ...]
    
    @staticmethod
    def map_vehicle_to_model(vehicle_type: str) -> str:
        """Map Twin vehicle type to 3D model identifier."""
        type_to_model = {
            'car': VehicleModel.CAR,
            'truck': VehicleModel.TRUCK,
            'bus': VehicleModel.BUS,
            'ambulance': VehicleModel.AMBULANCE,
            'fire': VehicleModel.FIRE_TRUCK,
            'police': VehicleModel.POLICE_VEHICLE,
            'motorcycle': VehicleModel.MOTORCYCLE,
        }
        return type_to_model.get(vehicle_type, VehicleModel.CAR).value
    
    @staticmethod
    def map_status_to_color(status: str, model: str) -> str:
        """Map vehicle status to 3D color."""
        if status == 'emergency':
            if model in [VehicleModel.AMBULANCE, VehicleModel.FIRE_TRUCK]:
                return '#FF0000'  # Red
            elif model == VehicleModel.POLICE_VEHICLE:
                return '#0000FF'  # Blue
        elif status == 'stopped':
            return '#FFB6C6'  # Light red (slowed/stopped)
        
        return '#4A90E2'  # Default blue
    
    @staticmethod
    def signal_phase_to_color(phase: int) -> str:
        """Map signal phase to display color (simplified)."""
        # In real system, phase → permissive movements → color
        # Simplified: assume phases 0,2 = NS green, 1,3 = EW green
        if phase in [0, 2]:
            return SignalColor.GREEN.value
        else:
            return SignalColor.RED.value
    
    @staticmethod
    def incident_severity_to_color(severity: int) -> str:
        """Map incident severity to color."""
        if severity == 1:
            return IncidentSeverityColor.LOW.value
        elif severity == 2:
            return IncidentSeverityColor.MODERATE.value
        elif severity == 3:
            return IncidentSeverityColor.HIGH.value
        else:
            return IncidentSeverityColor.CRITICAL.value
    
    def convert_vehicle_to_3d(
        self,
        vehicle_id: str,
        vehicle_type: str,
        x: float, y: float, z: float,
        rotation: float,
        speed: float,
        status: str
    ) -> Vehicle3D:
        """Convert Twin VehicleState to 3D format."""
        model = self.map_vehicle_to_model(vehicle_type)
        color = self.map_status_to_color(status, model)
        
        # Track trajectory for interpolation hints
        if vehicle_id not in self.vehicle_trajectories:
            self.vehicle_trajectories[vehicle_id] = []
        
        self.vehicle_trajectories[vehicle_id].append((x, y, z, datetime.utcnow().timestamp()))
        
        # Keep only last 10 points for smoothing
        if len(self.vehicle_trajectories[vehicle_id]) > 10:
            self.vehicle_trajectories[vehicle_id].pop(0)
        
        return Vehicle3D(
            id=vehicle_id,
            model=model,
            x=x, y=y, z=z,
            rotation_degrees=rotation,
            speed_kmh=speed,
            status=status,
            color=color,
            timestamp=datetime.utcnow().timestamp()
        )
    
    def convert_signal_to_3d(
        self,
        signal_id: str,
        x: float, y: float, z: float,
        phase: int
    ) -> Signal3D:
        """Convert Twin SignalState to 3D format."""
        color = self.signal_phase_to_color(phase)
        
        return Signal3D(
            id=signal_id,
            x=x, y=y, z=z,
            color=color,
            phase=phase,
            timestamp=datetime.utcnow().timestamp()
        )
    
    def convert_incident_to_3d(
        self,
        incident_id: str,
        x: float, y: float, z: float,
        severity: int,
        incident_type: str,
        status: str
    ) -> Incident3D:
        """Convert Twin IncidentVisualization to 3D format."""
        severity_color = self.incident_severity_to_color(severity)
        
        return Incident3D(
            id=incident_id,
            x=x, y=y, z=z,
            severity=severity,
            severity_color=severity_color,
            type=incident_type,
            status=status,
            timestamp=datetime.utcnow().timestamp()
        )
    
    def create_scene_snapshot(
        self,
        vehicles: List[tuple],  # (id, type, x, y, z, rotation, speed, status)
        signals: List[tuple],   # (id, x, y, z, phase)
        incidents: List[tuple]  # (id, x, y, z, severity, type, status)
    ) -> Scene3D:
        """Create complete 3D scene snapshot."""
        import uuid
        
        self.frame_counter += 1
        
        vehicles_3d = [
            self.convert_vehicle_to_3d(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7])
            for v in vehicles
        ]
        
        signals_3d = [
            self.convert_signal_to_3d(s[0], s[1], s[2], s[3], s[4])
            for s in signals
        ]
        
        incidents_3d = [
            self.convert_incident_to_3d(i[0], i[1], i[2], i[3], i[4], i[5], i[6])
            for i in incidents
        ]
        
        scene = Scene3D(
            vehicles=vehicles_3d,
            signals=signals_3d,
            incidents=incidents_3d,
            timestamp=datetime.utcnow().timestamp(),
            sequence=self.frame_counter,
            frame_id=str(uuid.uuid4())
        )
        
        self.last_scene = scene
        return scene
    
    def create_incremental_update(self, new_scene: Scene3D) -> Dict[str, Any]:
        """Create incremental update with interpolation hints."""
        if not self.last_scene:
            # First update - return full scene and update last_scene
            self.last_scene = new_scene
            return {
                'type': 'full_scene',
                'scene': self.serialize_scene(new_scene),
                'interpolation_hints': {
                    'use_dead_reckoning': True,
                    'dt_seconds': 0.1
                }
            }
        
        # Simple delta: new vehicles, gone vehicles, updated positions
        old_vehicle_ids = {v.id for v in self.last_scene.vehicles}
        new_vehicle_ids = {v.id for v in new_scene.vehicles}
        
        added = [v for v in new_scene.vehicles if v.id not in old_vehicle_ids]
        removed = [v.id for v in self.last_scene.vehicles if v.id not in new_vehicle_ids]
        
        updated = []
        for new_v in new_scene.vehicles:
            old_v = next((v for v in self.last_scene.vehicles if v.id == new_v.id), None)
            if old_v and (old_v.x != new_v.x or old_v.y != new_v.y):
                # Include trajectory for interpolation
                traj = self.vehicle_trajectories.get(new_v.id, [])
                updated.append({
                    **asdict(new_v),
                    'trajectory': traj[-3:] if len(traj) > 1 else []  # Last 3 points
                })
            elif old_v and (old_v.status != new_v.status or old_v.color != new_v.color):
                updated.append(asdict(new_v))
        
        # Update last scene for next iteration
        self.last_scene = new_scene
        
        return {
            'type': 'incremental_update',
            'sequence': new_scene.sequence,
            'frame_id': new_scene.frame_id,
            'added_vehicles': [asdict(v) for v in added],
            'removed_vehicles': removed,
            'updated_vehicles': updated,
            'signals': [asdict(s) for s in new_scene.signals],
            'incidents': [asdict(i) for i in new_scene.incidents],
            'interpolation_hints': {
                'use_dead_reckoning': True,
                'dt_seconds': 0.1,
                'extrapolate_distance_m': 5.0
            }
        }
    
    @staticmethod
    def serialize_scene(scene: Scene3D) -> Dict[str, Any]:
        """Serialize scene to JSON-compatible format."""
        return {
            'vehicles': [asdict(v) for v in scene.vehicles],
            'signals': [asdict(s) for s in scene.signals],
            'incidents': [asdict(i) for i in scene.incidents],
            'timestamp': scene.timestamp,
            'sequence': scene.sequence,
            'frame_id': scene.frame_id
        }


# ============================================================================
# Animation Interpolation Helper
# ============================================================================

class VehicleInterpolator:
    """Smooth interpolation between vehicle state updates for 60 FPS rendering."""
    
    @staticmethod
    def interpolate_position(
        pos_a: tuple,  # (x, y, z)
        pos_b: tuple,  # (x, y, z)
        t: float       # 0.0 to 1.0 (interpolation factor)
    ) -> tuple:
        """Linear interpolation between two positions."""
        return (
            pos_a[0] + (pos_b[0] - pos_a[0]) * t,
            pos_a[1] + (pos_b[1] - pos_a[1]) * t,
            pos_a[2] + (pos_b[2] - pos_a[2]) * t
        )
    
    @staticmethod
    def interpolate_rotation(
        rot_a: float,
        rot_b: float,
        t: float
    ) -> float:
        """Smooth rotation interpolation (handles 360° wraparound)."""
        # Shortest path around circle
        delta = rot_b - rot_a
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360
        
        return (rot_a + delta * t) % 360
    
    @staticmethod
    def dead_reckon(
        pos: tuple,
        heading: float,
        speed_kmh: float,
        dt_seconds: float
    ) -> tuple:
        """Extrapolate next position based on heading and speed."""
        # Convert speed from km/h to m/s
        speed_ms = speed_kmh / 3.6
        distance = speed_ms * dt_seconds
        
        # Convert heading to radians
        import math
        heading_rad = math.radians(heading)
        
        # Update position
        dx = distance * math.sin(heading_rad)
        dy = distance * math.cos(heading_rad)
        
        return (pos[0] + dx, pos[1] + dy, pos[2])


# ============================================================================
# REST API Response Formatting
# ============================================================================

class SceneFormatter:
    """Format 3D scenes for REST API responses."""
    
    @staticmethod
    def to_geojson_feature_collection(scene: Scene3D) -> Dict[str, Any]:
        """Convert scene to GeoJSON FeatureCollection for web mapping libraries."""
        features = []
        
        # Vehicle features
        for vehicle in scene.vehicles:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [vehicle.x, vehicle.y]
                },
                'properties': {
                    'id': vehicle.id,
                    'type': 'vehicle',
                    'model': vehicle.model,
                    'speed': vehicle.speed_kmh,
                    'status': vehicle.status,
                    'color': vehicle.color,
                    'rotation': vehicle.rotation_degrees
                }
            })
        
        # Signal features
        for signal in scene.signals:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [signal.x, signal.y]
                },
                'properties': {
                    'id': signal.id,
                    'type': 'signal',
                    'color': signal.color,
                    'phase': signal.phase
                }
            })
        
        # Incident features
        for incident in scene.incidents:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [incident.x, incident.y]
                },
                'properties': {
                    'id': incident.id,
                    'type': 'incident',
                    'severity': incident.severity,
                    'severity_color': incident.severity_color,
                    'incident_type': incident.type,
                    'status': incident.status
                }
            })
        
        return {
            'type': 'FeatureCollection',
            'features': features,
            'properties': {
                'timestamp': scene.timestamp,
                'sequence': scene.sequence,
                'frame_id': scene.frame_id
            }
        }
    
    @staticmethod
    def to_cesium_tiles_format(scene: Scene3D) -> Dict[str, Any]:
        """Convert scene to Cesium GIS format."""
        return {
            'version': '1.0',
            'name': 'UATMMS 3D Scene',
            'description': 'Real-time traffic simulation 3D visualization',
            'assets': [
                {
                    'id': f'vehicle_{v.id}',
                    'position': {'x': v.x, 'y': v.y, 'z': v.z},
                    'model': v.model,
                    'orientation': v.rotation_degrees,
                    'properties': {'status': v.status, 'speed': v.speed_kmh}
                }
                for v in scene.vehicles
            ],
            'signals': [
                {
                    'id': s.id,
                    'position': {'x': s.x, 'y': s.y, 'z': s.z},
                    'color': s.color,
                    'phase': s.phase
                }
                for s in scene.signals
            ],
            'incidents': [
                {
                    'id': i.id,
                    'position': {'x': i.x, 'y': i.y, 'z': i.z},
                    'severity': i.severity,
                    'type': i.type,
                    'color': i.severity_color
                }
                for i in scene.incidents
            ],
            'timestamp': scene.timestamp,
            'sequence': scene.sequence
        }
