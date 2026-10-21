import pytest
from unittest.mock import MagicMock, patch
from backend.app.simulation.traci_adapter import TraciAdapter
from backend.app.core.errors import SimulationError


def test_traci_adapter_initial_state():
    adapter = TraciAdapter()
    assert not adapter.is_connected
    assert adapter.step_count == 0
    assert adapter.simulation_time_s == 0.0
    assert adapter.get_active_vehicles() == []
    assert adapter.get_junction_signals() == []


def test_traci_adapter_start_invalid_path():
    adapter = TraciAdapter()
    # Mock find_sumo_binary so it finds a dummy binary
    with patch.object(adapter, "find_sumo_binary", return_value="dummy_sumo"):
        with pytest.raises(SimulationError, match="SUMO configuration file not found"):
            adapter.start(config_path="non_existent_config.sumocfg")


def test_traci_adapter_safety_gated_signal_control():
    adapter = TraciAdapter()
    junction_id = "J_Test_Adapter"

    # Step forward in synthetic mode
    adapter.step()
    assert adapter.step_count == 1
    assert adapter.simulation_time_s == 1.0

    # 1. Attempt invalid phase flip before minimum green (10s)
    approved, reason = adapter.set_junction_phase(junction_id, target_phase=1)
    # The first registration starts now, elapsed < 10.0s -> REJECTED
    assert not approved
    assert "Minimum green violation" in reason

    # 2. Advance time past minimum green
    adapter.simulation_time_s = 20.0
    approved_after, reason_after = adapter.set_junction_phase(junction_id, target_phase=1)
    assert approved_after


def test_traci_adapter_mocked_traci_connection():
    adapter = TraciAdapter()
    mock_traci = MagicMock()
    mock_traci.simulation.getTime.return_value = 1.0
    mock_traci.vehicle.getIDList.return_value = ["veh_01"]
    mock_traci.vehicle.getRoadID.return_value = "E_Main"
    mock_traci.vehicle.getLaneIndex.return_value = 0
    mock_traci.vehicle.getLanePosition.return_value = 45.0
    mock_traci.vehicle.getSpeed.return_value = 12.5
    mock_traci.vehicle.getTypeID.return_value = "auto_rickshaw"
    mock_traci.trafficlight.getIDList.return_value = ["TL_1"]
    mock_traci.trafficlight.getPhase.return_value = 0
    mock_traci.trafficlight.getPhaseName.return_value = "Green Phase"
    mock_traci.trafficlight.getPhaseDuration.return_value = 15.0

    with patch("backend.app.simulation.traci_adapter.traci", mock_traci):
        with patch("backend.app.simulation.traci_adapter.TRACI_AVAILABLE", True):
            adapter.is_connected = True
            adapter.active_tl_ids = ["TL_1"]

            # Step
            t = adapter.step()
            assert t == 1.0
            mock_traci.simulationStep.assert_called_once()

            # Vehicles
            vehs = adapter.get_active_vehicles()
            assert len(vehs) == 1
            assert vehs[0].vehicle_id == "veh_01"
            assert vehs[0].vehicle_type == "auto_rickshaw"
            assert vehs[0].speed_mps == 12.5

            # Signals
            sigs = adapter.get_junction_signals()
            assert len(sigs) == 1
            assert sigs[0].junction_id == "TL_1"
            assert sigs[0].current_phase_index == 0

            # Close
            adapter.close()
            mock_traci.close.assert_called_once()
            assert not adapter.is_connected
