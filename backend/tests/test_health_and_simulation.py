import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "UATMMS" in data["message"]
    assert "version" in data


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "safety_validator" in data["active_modules"]
    assert "simulation_manager" in data["active_modules"]


def test_simulation_lifecycle():
    # 1. Check initial state
    res = client.get("/api/v1/simulation/state")
    assert res.status_code == 200
    state = res.json()
    assert "run_id" in state
    assert len(state["signals"]) > 0

    # 2. Start simulation
    res_start = client.post("/api/v1/simulation/start", json={"scenario_id": "test_scenario", "seed": 123})
    assert res_start.status_code == 200
    assert res_start.json()["status"] == "running"

    # 3. Step forward
    res_step = client.post("/api/v1/simulation/step")
    assert res_step.status_code == 200
    assert res_step.json()["step"] == 1

    # 4. Pause simulation
    res_pause = client.post("/api/v1/simulation/pause")
    assert res_pause.status_code == 200
    assert res_pause.json()["status"] == "paused"

    # 5. Reset simulation
    res_reset = client.post("/api/v1/simulation/reset")
    assert res_reset.status_code == 200
    assert res_reset.json()["status"] == "stopped"


def test_incident_reporting():
    payload = {
        "incident_type": "blocked_lane",
        "edge_id": "E_Brigade_Main",
        "severity": 4,
        "description": "Fallen tree blocking right lane"
    }
    response = client.post("/api/v1/incidents/report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["incident_type"] == "blocked_lane"
    assert data["rerouting_triggered"] is True

    # Check active incidents
    res_active = client.get("/api/v1/incidents/active")
    assert res_active.status_code == 200
    assert any(i["edge_id"] == "E_Brigade_Main" for i in res_active.json())


def test_emergency_dispatch():
    payload = {
        "vehicle_id": "AMB_108",
        "vehicle_type": "ambulance",
        "origin_edge_id": "E_MG_Road_North",
        "destination_edge_id": "E_Victoria_Hospital",
        "urgency_level": 1
    }
    response = client.post("/api/v1/emergencies/dispatch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_id"] == "AMB_108"
    assert len(data["assigned_route"]) > 0
