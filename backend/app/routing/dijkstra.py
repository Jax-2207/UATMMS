"""
UATMMS Dijkstra Shortest Path Router
Computes exact minimum-cost paths on the dynamic weighted road network.
"""
from typing import List, Tuple, Optional
import networkx as nx
from backend.app.routing.graph import routing_graph
from backend.app.network.mapping import get_edge_by_id


def plan_dijkstra_route(
    origin_edge_id: str,
    destination_edge_id: str,
    vehicle_type: str = "passenger_car"
) -> Tuple[List[str], List[str], float, float, int]:
    """
    Computes shortest path from origin edge to destination edge using Dijkstra.
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
        # Trivial single edge or turnaround
        edge_seq = [origin_edge_id]
        if destination_edge_id != origin_edge_id:
            edge_seq.append(destination_edge_id)
        dist = orig_edge.length_m + (dest_edge.length_m if destination_edge_id != origin_edge_id else 0)
        time_s = dist / orig_edge.speed_limit_mps
        return edge_seq, [start_node], dist, round(time_s, 2), 1

    try:
        path_nodes = nx.dijkstra_path(routing_graph.graph, start_node, target_node, weight="weight")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        raise ValueError(f"No routable path found between {origin_edge_id} and {destination_edge_id}: {e}")

    # Reconstruct edge sequence
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
