import os
import xml.etree.ElementTree as ET
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.network.topology import network_topology
from backend.app.network.mapping import (
    get_junction_by_id,
    get_edge_by_id,
    get_all_junctions,
    get_all_edges
)

client = TestClient(app)


def test_bengaluru_network_mapping():
    junctions = get_all_junctions()
    assert len(junctions) == 6
    j1 = get_junction_by_id("J1_MG_Road")
    assert j1 is not None
    assert "MG Road" in j1.name
    assert j1.lat > 12.0
    assert j1.lon > 77.0

    edges = get_all_edges()
    assert len(edges) >= 14
    e_mg = get_edge_by_id("E_MG_J1_J2")
    assert e_mg is not None
    assert e_mg.from_junction == "J1_MG_Road"
    assert e_mg.to_junction == "J2_Brigade_Rd"
    assert e_mg.speed_limit_kph == 50.0


def test_network_topology_connectivity():
    assert network_topology.is_connected() is True
    neighbors_j2 = network_topology.get_neighbors("J2_Brigade_Rd")
    assert "J1_MG_Road" in neighbors_j2
    assert "J3_Residency_Rd" in neighbors_j2
    assert "J5_Commercial_St" in neighbors_j2

    inc_j5 = network_topology.get_incoming_edges("J5_Commercial_St")
    assert "E_BRIGADE_J2_J5" in inc_j5


def test_network_api_endpoints():
    # 1. Graph endpoint
    res_graph = client.get("/api/v1/network/graph")
    assert res_graph.status_code == 200
    graph_data = res_graph.json()
    assert graph_data["junction_count"] == 6
    assert graph_data["edge_count"] >= 14
    assert len(graph_data["nodes"]) == 6
    assert len(graph_data["links"]) >= 14

    # 2. Junctions endpoint
    res_junc = client.get("/api/v1/network/junctions")
    assert res_junc.status_code == 200
    assert len(res_junc.json()) == 6

    # 3. Edges endpoint
    res_edges = client.get("/api/v1/network/edges")
    assert res_edges.status_code == 200
    assert len(res_edges.json()) >= 14


def test_sumo_scenario_files_valid_xml():
    files_to_check = [
        "simulation/networks/poc_single_junction/single_junction.net.xml",
        "simulation/networks/poc_single_junction/single_junction.rou.xml",
        "simulation/networks/poc_single_junction/single_junction.sumocfg",
        "simulation/networks/bengaluru_core/bengaluru_core.nod.xml",
        "simulation/networks/bengaluru_core/bengaluru_core.edg.xml",
        "simulation/networks/bengaluru_core/bengaluru_core.tll.xml",
        "simulation/networks/bengaluru_core/bengaluru_core.net.xml",
        "simulation/networks/bengaluru_core/bengaluru_core.sumocfg",
        "simulation/scenarios/indian_vehicle_types.xml",
        "simulation/scenarios/off_peak.rou.xml",
        "simulation/scenarios/standard_demand.rou.xml",
        "simulation/scenarios/peak_rush.rou.xml"
    ]

    for rel_path in files_to_check:
        assert os.path.exists(rel_path), f"Missing expected simulation file: {rel_path}"
        try:
            tree = ET.parse(rel_path)
            root = tree.getroot()
            assert root is not None, f"Empty XML root in {rel_path}"
        except ET.ParseError as e:
            pytest.fail(f"Invalid XML syntax in {rel_path}: {e}")
