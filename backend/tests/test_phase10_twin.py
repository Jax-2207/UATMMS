"""
Phase 10: 3D Digital Twin Tests
Tests SUMO-to-Twin adapter, binary protocol, and state management.
"""

import pytest
import struct
from datetime import datetime
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

from backend.app.twin.adapter import (
    VehicleState, SignalState, IncidentVisualization, RoadNetworkState,
    SumoToTwinAdapter, BinaryProtocol
)


# ============================================================================
# Data Class Tests
# ============================================================================

class TestVehicleState:
    """Test VehicleState data class."""
    
    def test_vehicle_state_creation(self):
        """Test creating a vehicle state."""
        vehicle = VehicleState(
            id="v1",
            type="car",
            x=10.0,
            y=20.0,
            z=0.0,
            rotation=45.0,
            speed=50.0,
            lane="lane1",
            status="normal",
            timestamp=datetime.utcnow().timestamp()
        )
        
        assert vehicle.id == "v1"
        assert vehicle.type == "car"
        assert vehicle.x == 10.0
        assert vehicle.y == 20.0
        assert vehicle.speed == 50.0
        assert vehicle.status == "normal"
    
    def test_vehicle_state_emergency_type(self):
        """Test emergency vehicle state."""
        vehicle = VehicleState(
            id="amb1",
            type="ambulance",
            x=15.0,
            y=25.0,
            z=0.0,
            rotation=90.0,
            speed=80.0,
            lane="lane2",
            status="emergency",
            timestamp=datetime.utcnow().timestamp()
        )
        
        assert vehicle.type == "ambulance"
        assert vehicle.status == "emergency"
        assert vehicle.speed == 80.0


class TestSignalState:
    """Test SignalState data class."""
    
    def test_signal_state_creation(self):
        """Test creating signal state."""
        signal = SignalState(
            id="sig1",
            phase=0,
            duration=30.0,
            remaining_time=15.0,
            status="active",
            timestamp=datetime.utcnow().timestamp()
        )
        
        assert signal.id == "sig1"
        assert signal.phase == 0
        assert signal.duration == 30.0
        assert signal.remaining_time == 15.0
    
    def test_signal_phase_transitions(self):
        """Test signal phase transitions."""
        for phase in range(4):
            signal = SignalState(
                id=f"sig_{phase}",
                phase=phase,
                duration=30.0,
                remaining_time=30.0 - (phase * 5),
                status="active",
                timestamp=datetime.utcnow().timestamp()
            )
            assert signal.phase == phase


class TestIncidentVisualization:
    """Test IncidentVisualization data class."""
    
    def test_incident_creation(self):
        """Test creating incident visualization."""
        incident = IncidentVisualization(
            id="inc1",
            x=50.0,
            y=60.0,
            z=0.0,
            severity=3,
            type="accident",
            status="reported",
            timestamp=datetime.utcnow().timestamp()
        )
        
        assert incident.id == "inc1"
        assert incident.severity == 3
        assert incident.type == "accident"
        assert incident.status == "reported"
    
    def test_incident_severity_levels(self):
        """Test incident severity levels (1-5)."""
        for severity in range(1, 6):
            incident = IncidentVisualization(
                id=f"inc_{severity}",
                x=50.0,
                y=60.0,
                z=0.0,
                severity=severity,
                type="accident",
                status="reported",
                timestamp=datetime.utcnow().timestamp()
            )
            assert incident.severity == severity


class TestRoadNetworkState:
    """Test RoadNetworkState data class."""
    
    def test_network_state_creation(self):
        """Test creating network state."""
        vehicles = [
            VehicleState("v1", "car", 10.0, 20.0, 0.0, 45.0, 50.0, "lane1", "normal", datetime.utcnow().timestamp()),
            VehicleState("v2", "truck", 15.0, 25.0, 0.0, 90.0, 40.0, "lane2", "normal", datetime.utcnow().timestamp()),
        ]
        signals = [
            SignalState("sig1", 0, 30.0, 15.0, "active", datetime.utcnow().timestamp()),
        ]
        incidents = []
        
        state = RoadNetworkState(
            vehicles=vehicles,
            signals=signals,
            incidents=incidents,
            timestamp=datetime.utcnow().timestamp(),
            sequence_number=1
        )
        
        assert len(state.vehicles) == 2
        assert len(state.signals) == 1
        assert state.sequence_number == 1


# ============================================================================
# SumoToTwinAdapter Tests
# ============================================================================

class TestSumoToTwinAdapter:
    """Test SUMO-to-Twin adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return SumoToTwinAdapter()
    
    def test_adapter_initialization(self, adapter):
        """Test adapter initializes with sequence 0."""
        assert adapter.sequence_number == 0
        assert adapter.last_state is None
    
    def test_convert_vehicle_basic(self, adapter):
        """Test converting SUMO vehicle to VehicleState."""
        sumo_vehicle = {
            'id': 'v1',
            'type': 'car',
            'x': 10.0,
            'y': 20.0,
            'angle': 45.0,
            'speed': 50.0,
            'lane': 'lane1'
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        
        assert vehicle.id == 'v1'
        assert vehicle.type == 'car'
        assert vehicle.x == 10.0
        assert vehicle.y == 20.0
        assert vehicle.rotation == 45.0
        assert vehicle.speed == 50.0
        assert vehicle.status == 'normal'
    
    def test_convert_vehicle_emergency_type(self, adapter):
        """Test converting emergency vehicle."""
        sumo_vehicle = {
            'id': 'amb1',
            'type': 'emergency',
            'x': 15.0,
            'y': 25.0,
            'angle': 90.0,
            'speed': 80.0,
            'lane': 'lane2'
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        
        assert vehicle.type == 'ambulance'
        assert vehicle.status == 'emergency'
    
    def test_convert_vehicle_fire_truck(self, adapter):
        """Test converting fire truck."""
        sumo_vehicle = {
            'id': 'fire1',
            'type': 'fire',
            'x': 30.0,
            'y': 40.0,
            'angle': 180.0,
            'speed': 70.0,
            'lane': 'lane3'
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        
        assert vehicle.type == 'fire'
        assert vehicle.status == 'emergency'
    
    def test_convert_vehicle_police(self, adapter):
        """Test converting police vehicle."""
        sumo_vehicle = {
            'id': 'police1',
            'type': 'police',
            'x': 35.0,
            'y': 45.0,
            'angle': 270.0,
            'speed': 75.0,
            'lane': 'lane4'
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        
        assert vehicle.type == 'police'
        assert vehicle.status == 'emergency'
    
    def test_convert_vehicle_stopped(self, adapter):
        """Test converting stopped vehicle."""
        sumo_vehicle = {
            'id': 'v_stopped',
            'type': 'car',
            'x': 50.0,
            'y': 60.0,
            'angle': 0.0,
            'speed': 0.0,  # Stopped
            'lane': 'lane5'
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        
        assert vehicle.status == 'stopped'
    
    def test_convert_vehicle_missing_fields(self, adapter):
        """Test converting vehicle with missing optional fields."""
        sumo_vehicle = {
            'id': 'v_minimal',
            'x': 10.0,
            'y': 20.0
        }
        
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        
        assert vehicle.id == 'v_minimal'
        assert vehicle.type == 'car'  # Default type
        assert vehicle.speed == 0.0  # Default speed
    
    def test_convert_signal(self, adapter):
        """Test converting traffic signal."""
        signal = adapter.convert_signal('sig1', 0, 30.0, 15.0)
        
        assert signal.id == 'sig1'
        assert signal.phase == 0
        assert signal.duration == 30.0
        assert signal.remaining_time == 15.0
        assert signal.status == 'active'
    
    def test_convert_incident(self, adapter):
        """Test converting incident."""
        incident = adapter.convert_incident(
            'inc1', 50.0, 60.0, 3, 'accident', 'reported'
        )
        
        assert incident.id == 'inc1'
        assert incident.x == 50.0
        assert incident.y == 60.0
        assert incident.severity == 3
        assert incident.type == 'accident'
        assert incident.status == 'reported'
    
    def test_convert_incident_severity_clamping(self, adapter):
        """Test incident severity is clamped to 1-5."""
        # Test below range
        incident = adapter.convert_incident('inc1', 0.0, 0.0, 0, 'accident', 'reported')
        assert incident.severity == 1
        
        # Test above range
        incident = adapter.convert_incident('inc2', 0.0, 0.0, 10, 'accident', 'reported')
        assert incident.severity == 5
    
    def test_create_state_snapshot(self, adapter):
        """Test creating state snapshot."""
        vehicles = [
            {'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 45.0, 'speed': 50.0, 'lane': 'lane1'},
            {'id': 'v2', 'type': 'truck', 'x': 15.0, 'y': 25.0, 'angle': 90.0, 'speed': 40.0, 'lane': 'lane2'},
        ]
        signals = [
            ('sig1', 0, 30.0, 15.0),
            ('sig2', 1, 30.0, 25.0),
        ]
        incidents = [
            {'id': 'inc1', 'x': 50.0, 'y': 60.0, 'severity': 2, 'type': 'accident', 'status': 'reported'},
        ]
        
        state = adapter.create_state_snapshot(vehicles, signals, incidents)
        
        assert len(state.vehicles) == 2
        assert len(state.signals) == 2
        assert len(state.incidents) == 1
        assert state.sequence_number == 1
    
    def test_sequence_number_increments(self, adapter):
        """Test sequence number increments with each snapshot."""
        for i in range(1, 6):
            state = adapter.create_state_snapshot([], [], [])
            assert state.sequence_number == i
    
    def test_create_delta_update_first_update(self, adapter):
        """Test delta update on first call (should return full state)."""
        vehicles = [{'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'}]
        state = adapter.create_state_snapshot(vehicles, [], [])
        
        delta = adapter.create_delta_update(state)
        
        assert delta['type'] == 'full_update'
        assert 'data' in delta
        assert delta['sequence'] == 1
    
    def test_create_delta_update_no_changes(self, adapter):
        """Test delta update when no changes occurred."""
        vehicles = [{'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'}]
        
        # First update
        state1 = adapter.create_state_snapshot(vehicles, [], [])
        adapter.create_delta_update(state1)
        
        # Second update with same data
        state2 = adapter.create_state_snapshot(vehicles, [], [])
        delta = adapter.create_delta_update(state2)
        
        assert delta['type'] == 'delta_update'
        assert delta['added_vehicles'] == []
        assert delta['removed_vehicles'] == []
        assert delta['updated_vehicles'] == []
    
    def test_create_delta_update_vehicle_added(self, adapter):
        """Test delta update detects added vehicles."""
        # First update
        vehicles1 = [{'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'}]
        state1 = adapter.create_state_snapshot(vehicles1, [], [])
        adapter.create_delta_update(state1)
        
        # Second update with additional vehicle
        vehicles2 = vehicles1 + [{'id': 'v2', 'type': 'truck', 'x': 15.0, 'y': 25.0, 'angle': 0.0, 'speed': 40.0, 'lane': 'lane2'}]
        state2 = adapter.create_state_snapshot(vehicles2, [], [])
        delta = adapter.create_delta_update(state2)
        
        assert delta['type'] == 'delta_update'
        assert len(delta['added_vehicles']) == 1
        assert delta['added_vehicles'][0]['id'] == 'v2'
    
    def test_create_delta_update_vehicle_removed(self, adapter):
        """Test delta update detects removed vehicles."""
        # First update with two vehicles
        vehicles1 = [
            {'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'},
            {'id': 'v2', 'type': 'truck', 'x': 15.0, 'y': 25.0, 'angle': 0.0, 'speed': 40.0, 'lane': 'lane2'}
        ]
        state1 = adapter.create_state_snapshot(vehicles1, [], [])
        adapter.create_delta_update(state1)
        
        # Second update with one vehicle removed
        vehicles2 = [vehicles1[0]]
        state2 = adapter.create_state_snapshot(vehicles2, [], [])
        delta = adapter.create_delta_update(state2)
        
        assert delta['type'] == 'delta_update'
        assert len(delta['removed_vehicles']) == 1
        assert delta['removed_vehicles'][0] == 'v2'
    
    def test_create_delta_update_vehicle_moved(self, adapter):
        """Test delta update detects position changes."""
        # First update
        vehicles1 = [{'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'}]
        state1 = adapter.create_state_snapshot(vehicles1, [], [])
        adapter.create_delta_update(state1)
        
        # Second update with vehicle moved
        vehicles2 = [{'id': 'v1', 'type': 'car', 'x': 12.0, 'y': 22.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'}]
        state2 = adapter.create_state_snapshot(vehicles2, [], [])
        delta = adapter.create_delta_update(state2)
        
        assert delta['type'] == 'delta_update'
        assert len(delta['updated_vehicles']) == 1
        assert delta['updated_vehicles'][0]['x'] == 12.0
        assert delta['updated_vehicles'][0]['y'] == 22.0
    
    def test_serialize_state(self, adapter):
        """Test serializing complete state."""
        vehicles = [{'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'}]
        state = adapter.create_state_snapshot(vehicles, [], [])
        
        serialized = adapter.serialize_state(state)
        
        assert 'vehicles' in serialized
        assert 'signals' in serialized
        assert 'incidents' in serialized
        assert 'timestamp' in serialized
        assert 'sequence' in serialized
        assert len(serialized['vehicles']) == 1
    
    def test_serialize_vehicle(self, adapter):
        """Test serializing vehicle."""
        vehicle = VehicleState(
            id='v1', type='car', x=10.0, y=20.0, z=0.0,
            rotation=45.0, speed=50.0, lane='lane1',
            status='normal', timestamp=datetime.utcnow().timestamp()
        )
        
        serialized = adapter.serialize_vehicle(vehicle)
        
        assert serialized['id'] == 'v1'
        assert serialized['type'] == 'car'
        assert serialized['x'] == 10.0


# ============================================================================
# Binary Protocol Tests
# ============================================================================

class TestBinaryProtocol:
    """Test binary protocol encoding/decoding."""
    
    def test_frame_types_defined(self):
        """Test frame type constants are defined."""
        assert BinaryProtocol.FRAME_FULL_STATE == 0x01
        assert BinaryProtocol.FRAME_DELTA == 0x02
        assert BinaryProtocol.FRAME_VEHICLE_ADDED == 0x03
        assert BinaryProtocol.FRAME_VEHICLE_REMOVED == 0x04
        assert BinaryProtocol.FRAME_SIGNAL_UPDATE == 0x05
        assert BinaryProtocol.FRAME_INCIDENT_UPDATE == 0x06
    
    def test_encode_vehicle_car(self):
        """Test encoding a car vehicle."""
        vehicle = VehicleState(
            id='v1', type='car', x=10.0, y=20.0, z=0.0,
            rotation=45.0, speed=50.0, lane='lane1',
            status='normal', timestamp=datetime.utcnow().timestamp()
        )
        
        encoded = BinaryProtocol.encode_vehicle(vehicle)
        
        assert len(encoded) == 38
        assert isinstance(encoded, bytes)
    
    def test_encode_vehicle_truck(self):
        """Test encoding a truck vehicle."""
        vehicle = VehicleState(
            id='v2', type='truck', x=15.0, y=25.0, z=0.0,
            rotation=90.0, speed=40.0, lane='lane2',
            status='normal', timestamp=datetime.utcnow().timestamp()
        )
        
        encoded = BinaryProtocol.encode_vehicle(vehicle)
        assert len(encoded) == 38
    
    def test_encode_vehicle_ambulance(self):
        """Test encoding ambulance (emergency)."""
        vehicle = VehicleState(
            id='amb1', type='ambulance', x=30.0, y=40.0, z=0.0,
            rotation=180.0, speed=80.0, lane='lane3',
            status='emergency', timestamp=datetime.utcnow().timestamp()
        )
        
        encoded = BinaryProtocol.encode_vehicle(vehicle)
        assert len(encoded) == 38
    
    def test_encode_decode_vehicle_roundtrip(self):
        """Test encoding and decoding preserves vehicle data."""
        original = VehicleState(
            id='v1', type='car', x=10.5, y=20.5, z=0.0,
            rotation=45.0, speed=50.0, lane='lane1',
            status='normal', timestamp=datetime.utcnow().timestamp()
        )
        
        encoded = BinaryProtocol.encode_vehicle(original)
        decoded = BinaryProtocol.decode_vehicle(encoded)
        
        assert decoded is not None
        assert decoded.id == 'v1'
        assert decoded.type == 'car'
        assert abs(decoded.x - 10.5) < 0.01
        assert abs(decoded.y - 20.5) < 0.01
        assert abs(decoded.rotation - 45.0) < 0.01
        assert abs(decoded.speed - 50.0) < 0.01
        assert decoded.status == 'normal'
    
    def test_encode_decode_emergency_vehicle(self):
        """Test encoding/decoding emergency vehicle."""
        original = VehicleState(
            id='amb1', type='ambulance', x=35.5, y=45.5, z=0.0,
            rotation=90.0, speed=75.0, lane='lane2',
            status='emergency', timestamp=datetime.utcnow().timestamp()
        )
        
        encoded = BinaryProtocol.encode_vehicle(original)
        decoded = BinaryProtocol.decode_vehicle(encoded)
        
        assert decoded.type == 'ambulance'
        assert decoded.status == 'emergency'
        assert abs(decoded.speed - 75.0) < 0.01
    
    def test_decode_invalid_data(self):
        """Test decoding invalid/short data."""
        invalid_data = b'short'  # Too short
        
        result = BinaryProtocol.decode_vehicle(invalid_data)
        
        assert result is None
    
    def test_encode_vehicle_id_truncation(self):
        """Test encoding vehicle with long ID (should truncate to 16 bytes)."""
        vehicle = VehicleState(
            id='this_is_a_very_long_vehicle_id_that_exceeds_16_bytes',
            type='car', x=10.0, y=20.0, z=0.0,
            rotation=45.0, speed=50.0, lane='lane1',
            status='normal', timestamp=datetime.utcnow().timestamp()
        )
        
        encoded = BinaryProtocol.encode_vehicle(vehicle)
        assert len(encoded) == 38
        
        # Decode and check ID is truncated
        decoded = BinaryProtocol.decode_vehicle(encoded)
        assert len(decoded.id) <= 16
    
    def test_binary_protocol_vehicle_types(self):
        """Test binary encoding of all vehicle types."""
        types_and_codes = [
            ('car', 0),
            ('truck', 1),
            ('ambulance', 2),
            ('fire', 3),
            ('police', 4),
            ('bus', 5)
        ]
        
        for vtype, code in types_and_codes:
            vehicle = VehicleState(
                id='test', type=vtype, x=0.0, y=0.0, z=0.0,
                rotation=0.0, speed=0.0, lane='',
                status='normal', timestamp=datetime.utcnow().timestamp()
            )
            
            encoded = BinaryProtocol.encode_vehicle(vehicle)
            decoded = BinaryProtocol.decode_vehicle(encoded)
            
            assert decoded.type == vtype
    
    def test_binary_protocol_status_encoding(self):
        """Test binary encoding of all status values."""
        statuses_and_codes = [
            ('normal', 0),
            ('emergency', 1),
            ('stopped', 2)
        ]
        
        for status, code in statuses_and_codes:
            vehicle = VehicleState(
                id='test', type='car', x=0.0, y=0.0, z=0.0,
                rotation=0.0, speed=0.0, lane='',
                status=status, timestamp=datetime.utcnow().timestamp()
            )
            
            encoded = BinaryProtocol.encode_vehicle(vehicle)
            decoded = BinaryProtocol.decode_vehicle(encoded)
            
            assert decoded.status == status


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase10Integration:
    """Integration tests for Phase 10 components."""
    
    def test_adapter_to_binary_pipeline(self):
        """Test full pipeline: SUMO data → adapter → binary encoding."""
        adapter = SumoToTwinAdapter()
        
        sumo_vehicle = {
            'id': 'v1',
            'type': 'car',
            'x': 10.0,
            'y': 20.0,
            'angle': 45.0,
            'speed': 50.0,
            'lane': 'lane1'
        }
        
        # Convert SUMO to Twin format
        vehicle = adapter.convert_vehicle(sumo_vehicle)
        
        # Encode to binary
        encoded = BinaryProtocol.encode_vehicle(vehicle)
        
        # Decode back
        decoded = BinaryProtocol.decode_vehicle(encoded)
        
        assert decoded.id == 'v1'
        assert decoded.type == 'car'
        assert decoded.status == 'normal'
    
    def test_full_network_state_serialization(self):
        """Test serializing complete network state."""
        adapter = SumoToTwinAdapter()
        
        vehicles = [
            {'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 45.0, 'speed': 50.0, 'lane': 'lane1'},
            {'id': 'v2', 'type': 'truck', 'x': 15.0, 'y': 25.0, 'angle': 90.0, 'speed': 40.0, 'lane': 'lane2'},
            {'id': 'amb1', 'type': 'emergency', 'x': 30.0, 'y': 40.0, 'angle': 180.0, 'speed': 80.0, 'lane': 'lane3'},
        ]
        signals = [
            ('sig1', 0, 30.0, 15.0),
            ('sig2', 1, 30.0, 25.0),
        ]
        incidents = [
            {'id': 'inc1', 'x': 50.0, 'y': 60.0, 'severity': 2, 'type': 'accident', 'status': 'reported'},
            {'id': 'inc2', 'x': 55.0, 'y': 65.0, 'severity': 4, 'type': 'congestion', 'status': 'verified'},
        ]
        
        state = adapter.create_state_snapshot(vehicles, signals, incidents)
        serialized = adapter.serialize_state(state)
        
        assert len(serialized['vehicles']) == 3
        assert len(serialized['signals']) == 2
        assert len(serialized['incidents']) == 2
        assert serialized['sequence'] == 1
    
    def test_multiple_snapshots_with_deltas(self):
        """Test creating multiple snapshots with delta detection."""
        adapter = SumoToTwinAdapter()
        
        # Snapshot 1: Initial state
        vehicles1 = [
            {'id': 'v1', 'type': 'car', 'x': 10.0, 'y': 20.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'},
        ]
        state1 = adapter.create_state_snapshot(vehicles1, [], [])
        delta1 = adapter.create_delta_update(state1)
        assert delta1['type'] == 'full_update'
        
        # Snapshot 2: Vehicle moved
        vehicles2 = [
            {'id': 'v1', 'type': 'car', 'x': 12.0, 'y': 22.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'},
        ]
        state2 = adapter.create_state_snapshot(vehicles2, [], [])
        delta2 = adapter.create_delta_update(state2)
        assert delta2['type'] == 'delta_update'
        assert len(delta2['updated_vehicles']) == 1
        
        # Snapshot 3: New vehicle added AND existing vehicle moved
        vehicles3 = [
            {'id': 'v1', 'type': 'car', 'x': 14.0, 'y': 24.0, 'angle': 0.0, 'speed': 50.0, 'lane': 'lane1'},  # v1 moved again
            {'id': 'v2', 'type': 'truck', 'x': 25.0, 'y': 30.0, 'angle': 90.0, 'speed': 40.0, 'lane': 'lane2'},  # new
        ]
        state3 = adapter.create_state_snapshot(vehicles3, [], [])
        delta3 = adapter.create_delta_update(state3)
        assert delta3['type'] == 'delta_update'
        assert len(delta3['added_vehicles']) == 1  # v2 added
        assert len(delta3['updated_vehicles']) == 1  # v1 moved


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
