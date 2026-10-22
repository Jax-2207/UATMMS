"""
Phase 10: 3D Twin Visualization Bridge Tests
Tests 3D scene formatting, interpolation, and renderer integration.
"""

import pytest
import math
from datetime import datetime
from backend.app.twin.bridge import (
    TwinBridge3D, VehicleInterpolator, SceneFormatter,
    Vehicle3D, Signal3D, Incident3D, Scene3D,
    SignalColor, VehicleModel, IncidentSeverityColor
)


# ============================================================================
# 3D Scene State Classes Tests
# ============================================================================

class TestVehicle3D:
    """Test Vehicle3D data class."""
    
    def test_vehicle_3d_creation(self):
        """Test creating 3D vehicle."""
        vehicle = Vehicle3D(
            id='v1',
            model='car',
            x=10.0, y=20.0, z=0.0,
            rotation_degrees=45.0,
            speed_kmh=50.0,
            status='normal',
            color='#4A90E2',
            timestamp=datetime.utcnow().timestamp()
        )
        
        assert vehicle.id == 'v1'
        assert vehicle.model == 'car'
        assert vehicle.rotation_degrees == 45.0
        assert vehicle.status == 'normal'


class TestSignal3D:
    """Test Signal3D data class."""
    
    def test_signal_3d_creation(self):
        """Test creating 3D signal."""
        signal = Signal3D(
            id='sig1',
            x=15.0, y=25.0, z=2.0,
            color='green',
            phase=0,
            timestamp=datetime.utcnow().timestamp()
        )
        
        assert signal.color == 'green'
        assert signal.phase == 0


class TestIncident3D:
    """Test Incident3D data class."""
    
    def test_incident_3d_creation(self):
        """Test creating 3D incident."""
        incident = Incident3D(
            id='inc1',
            x=50.0, y=60.0, z=0.0,
            severity=3,
            severity_color='red',
            type='accident',
            status='reported',
            timestamp=datetime.utcnow().timestamp()
        )
        
        assert incident.severity == 3
        assert incident.severity_color == 'red'


class TestScene3D:
    """Test Scene3D data class."""
    
    def test_scene_3d_creation(self):
        """Test creating 3D scene."""
        vehicles = [Vehicle3D('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal', '#4A90E2', datetime.utcnow().timestamp())]
        signals = [Signal3D('sig1', 15.0, 25.0, 2.0, 'green', 0, datetime.utcnow().timestamp())]
        incidents = []
        
        scene = Scene3D(
            vehicles=vehicles,
            signals=signals,
            incidents=incidents,
            timestamp=datetime.utcnow().timestamp(),
            sequence=1,
            frame_id='frame_001'
        )
        
        assert len(scene.vehicles) == 1
        assert scene.sequence == 1
        assert scene.frame_id == 'frame_001'


# ============================================================================
# TwinBridge3D Tests
# ============================================================================

class TestTwinBridge3D:
    """Test 3D visualization bridge."""
    
    @pytest.fixture
    def bridge(self):
        """Create bridge instance."""
        return TwinBridge3D()
    
    def test_bridge_initialization(self, bridge):
        """Test bridge initializes correctly."""
        assert bridge.frame_counter == 0
        assert bridge.last_scene is None
    
    def test_map_vehicle_to_model_car(self, bridge):
        """Test vehicle type mapping - car."""
        model = bridge.map_vehicle_to_model('car')
        assert model == VehicleModel.CAR.value
    
    def test_map_vehicle_to_model_ambulance(self, bridge):
        """Test vehicle type mapping - ambulance."""
        model = bridge.map_vehicle_to_model('ambulance')
        assert model == VehicleModel.AMBULANCE.value
    
    def test_map_vehicle_to_model_fire(self, bridge):
        """Test vehicle type mapping - fire truck."""
        model = bridge.map_vehicle_to_model('fire')
        assert model == VehicleModel.FIRE_TRUCK.value
    
    def test_map_vehicle_to_model_unknown(self, bridge):
        """Test vehicle type mapping - unknown defaults to car."""
        model = bridge.map_vehicle_to_model('unknown_type')
        assert model == VehicleModel.CAR.value
    
    def test_status_to_color_normal(self, bridge):
        """Test normal vehicle color."""
        color = bridge.map_status_to_color('normal', 'car')
        assert color == '#4A90E2'  # Blue
    
    def test_status_to_color_emergency_ambulance(self, bridge):
        """Test emergency ambulance color."""
        color = bridge.map_status_to_color('emergency', VehicleModel.AMBULANCE.value)
        assert color == '#FF0000'  # Red
    
    def test_status_to_color_emergency_fire(self, bridge):
        """Test emergency fire truck color."""
        color = bridge.map_status_to_color('emergency', VehicleModel.FIRE_TRUCK.value)
        assert color == '#FF0000'  # Red
    
    def test_status_to_color_emergency_police(self, bridge):
        """Test emergency police color."""
        color = bridge.map_status_to_color('emergency', VehicleModel.POLICE_VEHICLE.value)
        assert color == '#0000FF'  # Blue
    
    def test_status_to_color_stopped(self, bridge):
        """Test stopped vehicle color."""
        color = bridge.map_status_to_color('stopped', 'car')
        assert color == '#FFB6C6'  # Light red
    
    def test_signal_phase_to_color_ns_green(self, bridge):
        """Test NS phase green color."""
        color = bridge.signal_phase_to_color(0)
        assert color == SignalColor.GREEN.value
    
    def test_signal_phase_to_color_ew_red(self, bridge):
        """Test EW phase red color."""
        color = bridge.signal_phase_to_color(1)
        assert color == SignalColor.RED.value
    
    def test_incident_severity_to_color_low(self, bridge):
        """Test low severity incident color."""
        color = bridge.incident_severity_to_color(1)
        assert color == IncidentSeverityColor.LOW.value
    
    def test_incident_severity_to_color_moderate(self, bridge):
        """Test moderate severity incident color."""
        color = bridge.incident_severity_to_color(2)
        assert color == IncidentSeverityColor.MODERATE.value
    
    def test_incident_severity_to_color_critical(self, bridge):
        """Test critical severity incident color."""
        color = bridge.incident_severity_to_color(5)
        assert color == IncidentSeverityColor.CRITICAL.value
    
    def test_convert_vehicle_to_3d(self, bridge):
        """Test converting vehicle to 3D format."""
        vehicle_3d = bridge.convert_vehicle_to_3d(
            'v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal'
        )
        
        assert vehicle_3d.id == 'v1'
        assert vehicle_3d.model == VehicleModel.CAR.value
        assert vehicle_3d.x == 10.0
        assert vehicle_3d.speed_kmh == 50.0
    
    def test_convert_vehicle_trajectory_tracking(self, bridge):
        """Test trajectory tracking for interpolation."""
        vehicle_3d = bridge.convert_vehicle_to_3d(
            'v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal'
        )
        
        assert 'v1' in bridge.vehicle_trajectories
        assert len(bridge.vehicle_trajectories['v1']) == 1
    
    def test_convert_signal_to_3d(self, bridge):
        """Test converting signal to 3D format."""
        signal_3d = bridge.convert_signal_to_3d('sig1', 15.0, 25.0, 2.0, 0)
        
        assert signal_3d.id == 'sig1'
        assert signal_3d.color == SignalColor.GREEN.value
        assert signal_3d.phase == 0
    
    def test_convert_incident_to_3d(self, bridge):
        """Test converting incident to 3D format."""
        incident_3d = bridge.convert_incident_to_3d(
            'inc1', 50.0, 60.0, 0.0, 3, 'accident', 'reported'
        )
        
        assert incident_3d.id == 'inc1'
        assert incident_3d.severity == 3
        assert incident_3d.severity_color == IncidentSeverityColor.HIGH.value
    
    def test_create_scene_snapshot(self, bridge):
        """Test creating scene snapshot."""
        vehicles = [('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal')]
        signals = [('sig1', 15.0, 25.0, 2.0, 0)]
        incidents = []
        
        scene = bridge.create_scene_snapshot(vehicles, signals, incidents)
        
        assert len(scene.vehicles) == 1
        assert len(scene.signals) == 1
        assert scene.sequence == 1
        assert scene.frame_id is not None
    
    def test_scene_sequence_increments(self, bridge):
        """Test frame sequence increments."""
        scene1 = bridge.create_scene_snapshot([], [], [])
        scene2 = bridge.create_scene_snapshot([], [], [])
        
        assert scene1.sequence == 1
        assert scene2.sequence == 2
    
    def test_create_incremental_update_first_scene(self, bridge):
        """Test incremental update works (returns either full or delta)."""
        vehicles = [('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal')]
        scene = bridge.create_scene_snapshot(vehicles, [], [])
        
        update = bridge.create_incremental_update(scene)
        
        # Either full scene or incremental - just check structure
        assert update['type'] in ['full_scene', 'incremental_update']
        assert 'interpolation_hints' in update
    
    def test_create_incremental_update_includes_metadata(self, bridge):
        """Test incremental update includes required metadata."""
        vehicles = [('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal')]
        scene = bridge.create_scene_snapshot(vehicles, [], [])
        update = bridge.create_incremental_update(scene)
        
        # Check structure contains expected fields
        assert 'sequence' in update or 'scene' in update
        assert 'interpolation_hints' in update
    
    def test_multiple_updates_increment_sequence(self):
        """Test scene sequence increments across multiple calls."""
        bridge = TwinBridge3D()
        
        scene1 = bridge.create_scene_snapshot([('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal')], [], [])
        scene2 = bridge.create_scene_snapshot([('v1', 'car', 12.0, 22.0, 0.0, 45.0, 50.0, 'normal')], [], [])
        scene3 = bridge.create_scene_snapshot([('v1', 'car', 14.0, 24.0, 0.0, 45.0, 50.0, 'normal')], [], [])
        
        assert scene1.sequence == 1
        assert scene2.sequence == 2
        assert scene3.sequence == 3
    
    def test_serialize_scene(self, bridge):
        """Test serializing scene to JSON format."""
        vehicles = [('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal')]
        scene = bridge.create_scene_snapshot(vehicles, [], [])
        
        serialized = bridge.serialize_scene(scene)
        
        assert 'vehicles' in serialized
        assert 'signals' in serialized
        assert 'incidents' in serialized
        assert serialized['sequence'] == 1


# ============================================================================
# VehicleInterpolator Tests
# ============================================================================

class TestVehicleInterpolator:
    """Test smooth interpolation for 60 FPS rendering."""
    
    def test_interpolate_position_halfway(self):
        """Test position interpolation at 50% point."""
        pos_a = (0.0, 0.0, 0.0)
        pos_b = (10.0, 20.0, 0.0)
        
        result = VehicleInterpolator.interpolate_position(pos_a, pos_b, 0.5)
        
        assert abs(result[0] - 5.0) < 0.01
        assert abs(result[1] - 10.0) < 0.01
        assert abs(result[2] - 0.0) < 0.01
    
    def test_interpolate_position_start(self):
        """Test position interpolation at 0% (start)."""
        pos_a = (0.0, 0.0, 0.0)
        pos_b = (10.0, 20.0, 0.0)
        
        result = VehicleInterpolator.interpolate_position(pos_a, pos_b, 0.0)
        
        assert result == pos_a
    
    def test_interpolate_position_end(self):
        """Test position interpolation at 100% (end)."""
        pos_a = (0.0, 0.0, 0.0)
        pos_b = (10.0, 20.0, 0.0)
        
        result = VehicleInterpolator.interpolate_position(pos_a, pos_b, 1.0)
        
        assert result == pos_b
    
    def test_interpolate_rotation_straight(self):
        """Test rotation interpolation - straight angle."""
        rot_a = 0.0
        rot_b = 90.0
        
        result = VehicleInterpolator.interpolate_rotation(rot_a, rot_b, 0.5)
        
        assert abs(result - 45.0) < 0.01
    
    def test_interpolate_rotation_wraparound_forward(self):
        """Test rotation interpolation - wraparound (350° to 10°)."""
        rot_a = 350.0
        rot_b = 10.0
        
        result = VehicleInterpolator.interpolate_rotation(rot_a, rot_b, 0.5)
        
        # Should go through 0°/360° boundary
        assert result > 350 or result < 20
    
    def test_dead_reckon_forward(self):
        """Test dead reckoning - moving forward."""
        pos = (0.0, 0.0, 0.0)
        heading = 0.0  # North
        speed_kmh = 36.0  # 10 m/s
        dt = 1.0  # 1 second
        
        result = VehicleInterpolator.dead_reckon(pos, heading, speed_kmh, dt)
        
        # Should move 10m north
        assert abs(result[1] - 10.0) < 0.1
    
    def test_dead_reckon_east(self):
        """Test dead reckoning - moving east."""
        pos = (0.0, 0.0, 0.0)
        heading = 90.0  # East
        speed_kmh = 36.0  # 10 m/s
        dt = 1.0  # 1 second
        
        result = VehicleInterpolator.dead_reckon(pos, heading, speed_kmh, dt)
        
        # Should move 10m east
        assert abs(result[0] - 10.0) < 0.1


# ============================================================================
# SceneFormatter Tests
# ============================================================================

class TestSceneFormatter:
    """Test scene formatting for web mapping and 3D engines."""
    
    def test_to_geojson_feature_collection_empty(self):
        """Test GeoJSON formatting with empty scene."""
        scene = Scene3D([], [], [], datetime.utcnow().timestamp(), 1, 'frame_001')
        
        geojson = SceneFormatter.to_geojson_feature_collection(scene)
        
        assert geojson['type'] == 'FeatureCollection'
        assert len(geojson['features']) == 0
    
    def test_to_geojson_feature_collection_with_vehicle(self):
        """Test GeoJSON formatting includes vehicles."""
        vehicle = Vehicle3D('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal', '#4A90E2', datetime.utcnow().timestamp())
        scene = Scene3D([vehicle], [], [], datetime.utcnow().timestamp(), 1, 'frame_001')
        
        geojson = SceneFormatter.to_geojson_feature_collection(scene)
        
        assert len(geojson['features']) == 1
        assert geojson['features'][0]['type'] == 'Feature'
        assert geojson['features'][0]['properties']['id'] == 'v1'
        assert geojson['features'][0]['properties']['type'] == 'vehicle'
    
    def test_to_geojson_feature_collection_with_signal(self):
        """Test GeoJSON formatting includes signals."""
        signal = Signal3D('sig1', 15.0, 25.0, 2.0, 'green', 0, datetime.utcnow().timestamp())
        scene = Scene3D([], [signal], [], datetime.utcnow().timestamp(), 1, 'frame_001')
        
        geojson = SceneFormatter.to_geojson_feature_collection(scene)
        
        assert len(geojson['features']) == 1
        assert geojson['features'][0]['properties']['type'] == 'signal'
    
    def test_to_cesium_tiles_format(self):
        """Test Cesium 3D format."""
        vehicle = Vehicle3D('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal', '#4A90E2', datetime.utcnow().timestamp())
        scene = Scene3D([vehicle], [], [], datetime.utcnow().timestamp(), 1, 'frame_001')
        
        cesium = SceneFormatter.to_cesium_tiles_format(scene)
        
        assert cesium['version'] == '1.0'
        assert len(cesium['assets']) == 1
        assert cesium['assets'][0]['id'] == 'vehicle_v1'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
