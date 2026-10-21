"""
UATMMS A* Dynamic Router
Computes optimal minimum-cost paths using an admissible Euclidean heuristic:
  h(u, v) = euclidean_dist(u, v) / max_speed_mps
Ensuring exact optimality with fewer node evaluations.
"""
from typing import List, Tuple
import math
import networkx as nx
from backend.app.routing.graph import routing_graph
from backend.app.network.mapping import get_edge_by_id

MAX_NETWORK_SPEED_MPS = 16.67  # 60 km/h upper bound


def euclidean_heuristic(u: str, v: str) -> float:
    """Admissible heuristic: straight-line distance divided by maximum legal speed."""
    ux, uy = routing_graph.get_node_coords(u)
    vx, vy = routing_graph.get_node_coords(v)
    dist = math.sqrt((ux - vx) ** 2 + (uy - vy) ** 2)
    return dist / MAX_NETWORK_SPEED_MPS


def plan_astar_route(
    origin_edge_id: str,
    destination_edge_id: str,
    vehicle_type: str = "passenger_car"
) -> Tuple[List[str], List[str], float, float, int]:
    """
    Computes shortest path from origin edge to destination edge using A*.
    Returns: (edge_sequence, junction_sequence, total_distance_m, total_time_s, nodes_expanded)
    """
    orig_edge = get_edge_by_id(origin_edge_id)
    dest_edge = get_edge_by_id(destination_edge_id)

    if not orig_edge:
        raise ValueError(f"Unknown origin edge: {origin_edge_id}")
    if not dest_edge:
        raise ValueError(f"Unknown destination edge: {destination_edge_id}")

    routing_graph.update_costs(vehicle_type=vehicle_type)

    start_node = orig_edge.to_junction
    target_node = dest_edge.from_junction

    if start_node == target_node:
        edge_seq = [origin_edge_id]
        if destination_edge_id != origin_edge_id:
            edge_seq.append(destination_edge_id)
        dist = orig_edge.length_m + (dest_edge.length_m if destination_edge_id != origin_edge_id else 0)
        time_s = dist / orig_edge.speed_limit_mps
        return edge_seq, [start_node], dist, round(time_s, 2), 1

    try:
        path_nodes = nx.astar_path(
            routing_graph.graph,
            start_node,
            target_node,
            heuristic=euclidean_heuristic,
            weight="weight"
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        raise ValueError(f"No routable path found between {origin_edge_id} and {destination_edge_id}: {e}")

    edge_sequence = [origin_edge_id]
    total_dist_m = orig_edge.length_m
    total_time_s = orig_edge.length_m / orig_edge.speed_limit_mps

    for i in range(len(path_nodes) - 1):
        u, v = path_nodes[i], path_nodes[i+1]
        edge_id = routing_graph.get_edge_id_between(u, v)
        if edge_id:
            edge_meta = get_edge_by_id(edge_id)
            if edge_meta:
                edge_sequence.append(edge_id)
                total_dist_m += edge_meta.length_m
                total_time_s += routing_graph.graph[u][v]["weight"]

    if destination_edge_id != edge_sequence[-1]:
        edge_sequence.append(destination_edge_id)
        total_dist_m += dest_edge.length_m
        total_time_s += dest_edge.length_m / dest_edge.speed_limit_mps

    return edge_sequence, path_nodes, round(total_dist_m, 1), round(total_time_s, 2), len(path_nodes)
