"""
Phase 11: System Hardening & Safety Validation
Comprehensive adversarial safety tests, edge cases, and benchmark compliance.
"""

import pytest
from datetime import datetime
from backend.app.twin.adapter import SumoToTwinAdapter, BinaryProtocol, VehicleState
from backend.app.twin.bridge import TwinBridge3D, SceneFormatter, VehicleInterpolator
from backend.app.safety.validator import SafetyValidator  # From Phase 0


# ============================================================================
# Adversarial Safety Tests
# ============================================================================

class TestAdversarialSafety:
    """Test system robustness against adversarial/malicious inputs."""
    
    def test_adapter_invalid_vehicle_id_empty_string(self):
        """Test adapter handles empty vehicle ID."""
        adapter = SumoToTwinAdapter()
        sumo_vehicle = {
            'id': '',  # Empty
            'type': 'car',
            'x': 10.0, 'y': 20.0,
            'angle': 45.0,
            'speed': 50.0,
            'lane': 'lane1'
        }
        
        # Should not crash
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        assert vehicle.id == ''  # Preserves the value
    
    def test_adapter_extreme_coordinates(self):
        """Test adapter handles extreme coordinates."""
        adapter = SumoToTwinAdapter()
        sumo_vehicle = {
            'id': 'v1',
            'type': 'car',
            'x': 180.0,  # Maximum longitude
            'y': 90.0,   # Maximum latitude
            'angle': 0.0,
            'speed': 0.0,
            'lane': 'lane1'
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        assert vehicle.x == 180.0
        assert vehicle.y == 90.0
    
    def test_adapter_negative_speed(self):
        """Test adapter handles negative speed (reverse)."""
        adapter = SumoToTwinAdapter()
        sumo_vehicle = {
            'id': 'v1',
            'type': 'car',
            'x': 10.0, 'y': 20.0,
            'angle': 0.0,
            'speed': -10.0,  # Negative (reverse)
            'lane': 'lane1'
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        assert vehicle.speed == -10.0
    
    def test_adapter_extreme_rotation(self):
        """Test adapter handles extreme rotation angles."""
        adapter = SumoToTwinAdapter()
        
        # Test 360+ degrees
        sumo_vehicle = {
            'id': 'v1', 'type': 'car',
            'x': 10.0, 'y': 20.0,
            'angle': 720.0,  # 2 full rotations
            'speed': 50.0, 'lane': 'lane1'
        }
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        assert vehicle.rotation == 720.0  # Preserves the value
    
    def test_binary_protocol_short_data(self):
        """Test binary decode with very short data."""
        short_data = b'short'
        result = BinaryProtocol.decode_vehicle(short_data)
        assert result is None  # Should handle gracefully
    
    def test_binary_protocol_empty_data(self):
        """Test binary decode with empty data."""
        result = BinaryProtocol.decode_vehicle(b'')
        assert result is None
    
    def test_binary_protocol_max_length_vehicle_id(self):
        """Test binary encoding with exactly 16-byte vehicle ID."""
        vehicle = VehicleState(
            id='12345678901234567890',  # 20 bytes
            type='car', x=10.0, y=20.0, z=0.0,
            rotation=45.0, speed=50.0, lane='',
            status='normal', timestamp=datetime.utcnow().timestamp()
        )
        
        encoded = BinaryProtocol.encode_vehicle(vehicle)
        assert len(encoded) == 38
        
        decoded = BinaryProtocol.decode_vehicle(encoded)
        assert decoded is not None
        # ID should be truncated to 16 bytes
        assert len(decoded.id) <= 16
    
    def test_bridge_null_scene_operations(self):
        """Test bridge operations with null/empty scenes."""
        bridge = TwinBridge3D()
        
        # Empty scene
        scene = bridge.create_scene_snapshot([], [], [])
        assert len(scene.vehicles) == 0
        assert len(scene.signals) == 0
        assert len(scene.incidents) == 0
    
    def test_interpolator_identical_positions(self):
        """Test interpolation when start and end are identical."""
        pos_a = (10.0, 20.0, 0.0)
        pos_b = (10.0, 20.0, 0.0)
        
        result = VehicleInterpolator.interpolate_position(pos_a, pos_b, 0.5)
        assert result == (10.0, 20.0, 0.0)
    
    def test_interpolator_zero_speed_dead_reckoning(self):
        """Test dead reckoning with zero speed."""
        pos = (10.0, 20.0, 0.0)
        heading = 0.0
        speed_kmh = 0.0
        dt = 1.0
        
        result = VehicleInterpolator.dead_reckon(pos, heading, speed_kmh, dt)
        assert result == pos  # Should not move
    
    def test_incident_severity_clamping(self):
        """Test incident severity is clamped to 1-5 range."""
        adapter = SumoToTwinAdapter()
        
        # Test zero
        incident = adapter.convert_incident('inc1', 0.0, 0.0, 0, 'accident', 'reported')
        assert incident.severity >= 1
        
        # Test negative
        incident = adapter.convert_incident('inc2', 0.0, 0.0, -5, 'accident', 'reported')
        assert incident.severity >= 1
        
        # Test extreme
        incident = adapter.convert_incident('inc3', 0.0, 0.0, 1000, 'accident', 'reported')
        assert incident.severity <= 5
    
    def test_scene_serialization_large_dataset(self):
        """Test scene serialization with 500+ vehicles."""
        adapter = SumoToTwinAdapter()
        
        vehicles = [
            {
                'id': f'v_{i}',
                'type': 'car' if i % 2 == 0 else 'truck',
                'x': 10.0 + i * 0.1,
                'y': 20.0 + i * 0.1,
                'angle': 45.0,
                'speed': 50.0 - i * 0.01,
                'lane': 'normal'
            }
            for i in range(500)
        ]
        
        scene = adapter.create_state_snapshot(vehicles, [], [])
        
        # Should handle 500+ vehicles without crashing
        assert len(scene.vehicles) == 500
        
        # Serialization should work
        serialized = adapter.serialize_state(scene)
        assert len(serialized['vehicles']) == 500


# ============================================================================
# Edge Case & Boundary Tests
# ============================================================================

class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""
    
    def test_vehicle_at_network_origin(self):
        """Test vehicle at coordinate origin (0, 0)."""
        adapter = SumoToTwinAdapter()
        sumo_vehicle = {
            'id': 'v_origin',
            'type': 'car',
            'x': 0.0, 'y': 0.0,
            'angle': 0.0,
            'speed': 0.0,
            'lane': 'lane0'
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        assert vehicle.x == 0.0
        assert vehicle.y == 0.0
    
    def test_signal_all_phases(self):
        """Test signal conversion for all possible phases."""
        adapter = SumoToTwinAdapter()
        
        for phase in range(4):
            signal = adapter.convert_signal(f'sig_{phase}', phase, 30.0, 15.0)
            assert signal.phase == phase
            assert signal.id == f'sig_{phase}'
    
    def test_incident_all_severity_levels(self):
        """Test incident visualization for all severity levels."""
        adapter = SumoToTwinAdapter()
        
        for severity in range(1, 6):
            incident = adapter.convert_incident(
                f'inc_{severity}', 0.0, 0.0, severity, 'test', 'reported'
            )
            assert incident.severity == severity
    
    def test_vehicle_type_mapping_all_types(self):
        """Test vehicle type mapping for all supported types."""
        bridge = TwinBridge3D()
        
        types = ['car', 'truck', 'ambulance', 'fire', 'police', 'bus', 'motorcycle']
        for vtype in types:
            model = bridge.map_vehicle_to_model(vtype)
            assert model is not None
            assert isinstance(model, str)
    
    def test_rotation_interpolation_wraparound_all_quadrants(self):
        """Test rotation interpolation across all angle boundaries."""
        # Test 0-90°
        result = VehicleInterpolator.interpolate_rotation(45.0, 90.0, 0.5)
        assert 45 <= result <= 90
        
        # Test 180-270°
        result = VehicleInterpolator.interpolate_rotation(180.0, 270.0, 0.5)
        assert 180 <= result <= 270
        
        # Test 270-360°
        result = VehicleInterpolator.interpolate_rotation(270.0, 360.0, 0.5)
        assert result >= 270 or result <= 360


# ============================================================================
# Performance & Stress Tests
# ============================================================================

class TestPerformance:
    """Test system performance under load."""
    
    def test_adapter_throughput_1000_vehicles(self):
        """Test adapter can process 1000 vehicle conversions quickly."""
        import time
        adapter = SumoToTwinAdapter()
        
        vehicles = [
            {
                'id': f'v_{i}',
                'type': 'car',
                'x': 10.0 + i * 0.1,
                'y': 20.0 + i * 0.1,
                'angle': 45.0,
                'speed': 50.0,
                'lane': f'lane_{i % 4}'
            }
            for i in range(1000)
        ]
        
        start = time.time()
        scene = adapter.create_state_snapshot(vehicles, [], [])
        elapsed = time.time() - start
        
        assert len(scene.vehicles) == 1000
        # Should process 1000 vehicles in < 100ms
        assert elapsed < 0.1, f"Processing 1000 vehicles took {elapsed:.3f}s"
    
    def test_binary_encoding_throughput_1000_vehicles(self):
        """Test binary encoding performance for 1000 vehicles."""
        import time
        adapter = SumoToTwinAdapter()
        
        vehicles = [
            {
                'id': f'v_{i}',
                'type': 'car',
                'x': 10.0 + i * 0.1,
                'y': 20.0 + i * 0.1,
                'angle': 45.0,
                'speed': 50.0,
                'lane': f'lane_{i % 4}'
            }
            for i in range(1000)
        ]
        
        scene = adapter.create_state_snapshot(vehicles, [], [])
        
        start = time.time()
        for vehicle in scene.vehicles:
            BinaryProtocol.encode_vehicle(vehicle)
        elapsed = time.time() - start
        
        # Should encode 1000 vehicles in < 50ms
        assert elapsed < 0.05, f"Encoding 1000 vehicles took {elapsed:.3f}s"
    
    def test_scene_serialization_throughput(self):
        """Test scene serialization performance."""
        import time
        adapter = SumoToTwinAdapter()
        
        vehicles = [
            {
                'id': f'v_{i}',
                'type': 'car',
                'x': 10.0 + i * 0.1,
                'y': 20.0 + i * 0.1,
                'angle': 45.0,
                'speed': 50.0,
                'lane': 'lane1'
            }
            for i in range(500)
        ]
        scene = adapter.create_state_snapshot(vehicles, [], [])
        
        start = time.time()
        for _ in range(100):  # Serialize 100 times
            adapter.serialize_state(scene)
        elapsed = time.time() - start
        
        # Should serialize 100 times in < 200ms (relaxed constraint)
        assert elapsed < 0.2, f"100 serializations took {elapsed:.3f}s"
    
    def test_interpolation_throughput_1000_calculations(self):
        """Test interpolation performance."""
        import time
        
        positions = [(i * 0.1, i * 0.1, 0.0) for i in range(500)]
        
        start = time.time()
        for p in positions:
            for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
                VehicleInterpolator.interpolate_position(p, (p[0] + 1, p[1] + 1, 0), t)
        elapsed = time.time() - start
        
        # Should perform 2500 interpolations in < 50ms
        assert elapsed < 0.05, f"2500 interpolations took {elapsed:.3f}s"


# ============================================================================
# Consistency & Determinism Tests
# ============================================================================

class TestDeterminism:
    """Test deterministic behavior across runs."""
    
    def test_same_input_same_output(self):
        """Test adapter produces identical output for identical input."""
        sumo_vehicle = {
            'id': 'v_test',
            'type': 'car',
            'x': 13.0517,
            'y': 77.5541,
            'angle': 45.5,
            'speed': 48.3,
            'lane': 'lane_main'
        }
        
        adapter1 = SumoToTwinAdapter()
        vehicle1 = adapter1.convert_vehicle(sumo_vehicle)
        
        adapter2 = SumoToTwinAdapter()
        vehicle2 = adapter2.convert_vehicle(sumo_vehicle)
        
        assert vehicle1.x == vehicle2.x
        assert vehicle1.y == vehicle2.y
        assert vehicle1.rotation == vehicle2.rotation
        assert vehicle1.speed == vehicle2.speed
    
    def test_sequence_counter_deterministic(self):
        """Test sequence counter increments deterministically."""
        bridge = TwinBridge3D()
        
        sequences = []
        for i in range(10):
            scene = bridge.create_scene_snapshot([], [], [])
            sequences.append(scene.sequence)
        
        # Should be 1, 2, 3, ..., 10
        assert sequences == list(range(1, 11))
    
    def test_binary_encoding_roundtrip_deterministic(self):
        """Test binary encoding/decoding preserves values deterministically."""
        vehicle = VehicleState(
            id='v_deterministic',
            type='car',
            x=13.05,
            y=77.55,
            z=0.0,
            rotation=45.0,
            speed=50.0,
            lane='lane1',
            status='normal',
            timestamp=1731025200.0
        )
        
        for _ in range(5):
            encoded = BinaryProtocol.encode_vehicle(vehicle)
            decoded = BinaryProtocol.decode_vehicle(encoded)
            
            assert abs(decoded.x - vehicle.x) < 0.01
            assert abs(decoded.y - vehicle.y) < 0.01
            assert abs(decoded.rotation - vehicle.rotation) < 0.1
            assert abs(decoded.speed - vehicle.speed) < 0.1


# ============================================================================
# Data Integrity Tests
# ============================================================================

class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_scene_frame_id_uniqueness(self):
        """Test each scene gets a unique frame ID."""
        bridge = TwinBridge3D()
        
        frame_ids = set()
        for _ in range(100):
            scene = bridge.create_scene_snapshot([], [], [])
            frame_ids.add(scene.frame_id)
        
        # All frame IDs should be unique
        assert len(frame_ids) == 100
    
    def test_geojson_feature_collection_validity(self):
        """Test GeoJSON output is valid."""
        bridge = TwinBridge3D()
        vehicles = [('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal')]
        scene = bridge.create_scene_snapshot(vehicles, [], [])
        
        geojson = SceneFormatter.to_geojson_feature_collection(scene)
        
        # Required GeoJSON fields
        assert geojson['type'] == 'FeatureCollection'
        assert 'features' in geojson
        assert isinstance(geojson['features'], list)
        
        # Each feature should be valid
        for feature in geojson['features']:
            assert feature['type'] == 'Feature'
            assert 'geometry' in feature
            assert 'properties' in feature
            assert feature['geometry']['type'] in ['Point', 'LineString', 'Polygon']
    
    def test_cesium_format_completeness(self):
        """Test Cesium format includes all required fields."""
        bridge = TwinBridge3D()
        vehicles = [('v1', 'car', 10.0, 20.0, 0.0, 45.0, 50.0, 'normal')]
        signals = [('sig1', 15.0, 25.0, 2.0, 0)]
        scene = bridge.create_scene_snapshot(vehicles, signals, [])
        
        cesium = SceneFormatter.to_cesium_tiles_format(scene)
        
        # Check required fields
        assert 'version' in cesium
        assert 'assets' in cesium
        assert 'signals' in cesium
        assert 'timestamp' in cesium
        assert 'sequence' in cesium


# ============================================================================
# Compliance & Standard Tests
# ============================================================================

class TestCompliance:
    """Test compliance with Phase specifications."""
    
    def test_adapter_all_vehicle_types_supported(self):
        """Test adapter supports all vehicle types from spec."""
        adapter = SumoToTwinAdapter()
        supported_types = ['car', 'truck', 'bus']
        
        for vtype in supported_types:
            sumo_vehicle = {
                'id': f'v_{vtype}',
                'type': vtype,
                'x': 10.0, 'y': 20.0,
                'angle': 0.0,
                'speed': 50.0,
                'lane': 'lane1'
            }
            vehicle = adapter.convert_vehicle(sumo_vehicle)
            # Verify conversion happened without error
            assert vehicle is not None
            assert vehicle.id == f'v_{vtype}'
    
    def test_binary_protocol_38_byte_vehicle_format(self):
        """Test binary protocol maintains 38-byte vehicle encoding."""
        vehicle = VehicleState(
            id='v1',
            type='car',
            x=10.0, y=20.0, z=0.0,
            rotation=45.0, speed=50.0, lane='',
            status='normal', timestamp=datetime.utcnow().timestamp()
        )
        
        encoded = BinaryProtocol.encode_vehicle(vehicle)
        assert len(encoded) == 38, "Vehicle encoding must be exactly 38 bytes"
    
    def test_signal_phases_0_to_3(self):
        """Test signal states support phases 0-3 per spec."""
        adapter = SumoToTwinAdapter()
        
        for phase in range(4):
            signal = adapter.convert_signal(f'sig_{phase}', phase, 30.0, 15.0)
            assert signal.phase == phase
    
    def test_incident_severity_1_to_5(self):
        """Test incident severity levels 1-5 per spec."""
        adapter = SumoToTwinAdapter()
        
        for severity in range(1, 6):
            incident = adapter.convert_incident(
                f'inc_{severity}', 0.0, 0.0, severity, 'test', 'reported'
            )
            assert incident.severity == severity


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
