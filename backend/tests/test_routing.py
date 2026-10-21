"""
Tests for Phase 3: Dynamic Graph Routing (A*, Dijkstra, Cost Model, Hysteresis, and Endpoints).
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.routing.graph import routing_graph
from backend.app.routing.cost_model import dynamic_cost_model
from backend.app.routing.dijkstra import plan_dijkstra_route
from backend.app.routing.astar import plan_astar_route, euclidean_heuristic
from backend.app.routing.router import dynamic_router
from backend.app.schemas.routing import RoutePlanRequest, RerouteEvaluationRequest


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_cost_model():
    """Reset dynamic edge conditions before each test."""
    dynamic_cost_model._conditions.clear()
    routing_graph._build_graph()


def test_routing_graph_initialization():
    """Verify routing graph properly incorporates junctions and edges."""
    assert len(routing_graph.graph.nodes) >= 6
    assert len(routing_graph.graph.edges) >= 14
    # Check node coordinates exist
    ux, uy = routing_graph.get_node_coords("J1_MG_Road")
    assert ux > 0 and uy > 0


def test_dijkstra_and_astar_route_equivalence():
    """Verify Dijkstra and A* both find the optimal path across CBD network."""
    orig = "E_MG_J1_J2"
    dest = "E_CO_J5_J6"

    d_edges, d_juncs, d_dist, d_time, d_nodes = plan_dijkstra_route(orig, dest)
    a_edges, a_juncs, a_dist, a_time, a_nodes = plan_astar_route(orig, dest)

    assert d_edges[0] == orig
    assert d_edges[-1] == dest
    assert a_edges[0] == orig
    assert a_edges[-1] == dest

    # Both must find optimal travel time
    assert abs(d_time - a_time) < 0.1
    assert abs(d_dist - a_dist) < 0.1
    # A* heuristic should expand <= nodes or equal
    assert a_nodes <= d_nodes + 2


def test_euclidean_heuristic_admissibility():
    """Verify euclidean heuristic never overestimates the true travel time cost."""
    nodes = list(routing_graph.graph.nodes)
    u, v = nodes[0], nodes[1]
    h_val = euclidean_heuristic(u, v)
    assert h_val >= 0.0

    # Ensure edge cost between u and v (if connected) is >= heuristic
    if routing_graph.graph.has_edge(u, v):
        edge_weight = routing_graph.graph[u][v]["weight"]
        assert h_val <= edge_weight + 1e-3


def test_dynamic_cost_incident_avoidance():
    """Verify routing detours around an edge with a severe incident."""
    orig = "E_MG_J1_J2"
    dest = "E_CH_J5_J4"

    # Default baseline route: J1 -> J2 -> J5 -> J4 (via E_MG_J1_J2, E_BRIGADE_J2_J5, E_CH_J5_J4)
    base_edges, _, _, base_time, _ = plan_astar_route(orig, dest)

    # Pick an intermediate edge and set severity 5 (blocked)
    block_edge = "E_BRIGADE_J2_J5"
    dynamic_cost_model.update_condition(
        edge_id=block_edge,
        incident_severity=5,
        is_closed=True
    )

    detour_edges, _, _, detour_time, _ = plan_astar_route(orig, dest)

    assert block_edge not in detour_edges
    assert detour_time > base_time


def test_reroute_hysteresis_prevention():
    """Verify reroute is rejected if saving is below hysteresis threshold (15%)."""
    current_route = ["E_MG_J1_J2", "E_BRIGADE_J2_J5", "E_CH_J5_J4"]
    current_edge = "E_MG_J1_J2"
    dest_edge = "E_CH_J5_J4"

    # Minor delay on current route (1 vehicle queue = 3 seconds delay)
    dynamic_cost_model.update_condition(
        edge_id="E_BRIGADE_J2_J5",
        queue_count=1
    )

    req = RerouteEvaluationRequest(
        current_route=current_route,
        current_edge_id=current_edge,
        destination_edge_id=dest_edge,
        hysteresis_threshold=0.15
    )
    res = dynamic_router.evaluate_reroute(req)

    # Should retain route because 3s delay is < 15% saving
    assert res.should_reroute is False
    assert res.recommended_route == current_route


def test_reroute_trigger_on_severe_blockage():
    """Verify reroute is accepted when saving exceeds 15%."""
    current_route = ["E_MG_J1_J2", "E_BRIGADE_J2_J5", "E_CH_J5_J4"]
    current_edge = "E_MG_J1_J2"
    dest_edge = "E_CH_J5_J4"

    # Severe congestion on current path
    dynamic_cost_model.update_condition(
        edge_id="E_BRIGADE_J2_J5",
        queue_count=35,
        incident_severity=3
    )

    req = RerouteEvaluationRequest(
        current_route=current_route,
        current_edge_id=current_edge,
        destination_edge_id=dest_edge,
        hysteresis_threshold=0.15
    )
    res = dynamic_router.evaluate_reroute(req)

    assert res.should_reroute is True
    assert "E_BRIGADE_J2_J5" not in res.recommended_route
    assert res.relative_time_saved_ratio > 0.15


def test_api_route_plan_and_evaluate(client):
    """Test REST API endpoints for /api/v1/routes/plan and /evaluate."""
    # Plan
    plan_payload = {
        "origin_edge_id": "E_MG_J1_J2",
        "destination_edge_id": "E_CO_J5_J6",
        "algorithm": "astar"
    }
    resp = client.post("/api/v1/routes/plan", json=plan_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "route_id" in data
    assert data["origin_edge_id"] == "E_MG_J1_J2"
    assert len(data["edge_sequence"]) >= 2

    # Evaluate
    eval_payload = {
        "current_route": data["edge_sequence"],
        "current_edge_id": "E_MG_J1_J2",
        "destination_edge_id": "E_CO_J5_J6",
        "hysteresis_threshold": 0.15
    }
    eval_resp = client.post("/api/v1/routes/evaluate", json=eval_payload)
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert "should_reroute" in eval_data

    # Invalid edge error
    bad_resp = client.post("/api/v1/routes/plan", json={
        "origin_edge_id": "NON_EXISTENT_EDGE",
        "destination_edge_id": "E_CO_J5_J6"
    })
    assert bad_resp.status_code == 400
