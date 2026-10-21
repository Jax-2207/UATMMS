"""
UATMMS Routing Graph
Constructs and maintains a NetworkX DiGraph synchronized with network topology
and dynamic edge travel costs.
"""
from typing import Dict, List, Optional, Tuple, Any
import networkx as nx
from backend.app.network.topology import network_topology
from backend.app.routing.cost_model import dynamic_cost_model


class RoutingGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.edge_lookup: Dict[Tuple[str, str], str] = {}  # (u, v) -> edge_id
        self._build_graph()

    def _build_graph(self):
        """Constructs NetworkX DiGraph from NetworkTopology."""
        self.graph.clear()
        self.edge_lookup.clear()

        # Add Nodes (Junctions and Perimeter entry/exit nodes)
        for j_id, j in network_topology.junctions.items():
            self.graph.add_node(
                j_id,
                x=j.x_m,
                y=j.y_m,
                name=j.name,
                signalized=j.signalized
            )

        # Add Edges
        for edge_id, edge in network_topology.edges.items():
            u = edge.from_junction
            v = edge.to_junction

            # If node not yet in graph (e.g. perimeter node), add with fallback coordinates
            if u not in self.graph:
                self.graph.add_node(u, x=0.0, y=0.0, name=u, signalized=False)
            if v not in self.graph:
                self.graph.add_node(v, x=0.0, y=0.0, name=v, signalized=False)

            cost = dynamic_cost_model.compute_edge_cost(
                edge_id=edge_id,
                length_m=edge.length_m,
                speed_limit_mps=edge.speed_limit_mps
            )

            self.graph.add_edge(
                u, v,
                edge_id=edge_id,
                length_m=edge.length_m,
                speed_limit_mps=edge.speed_limit_mps,
                weight=cost
            )
            self.edge_lookup[(u, v)] = edge_id

    def update_costs(self, vehicle_type: str = "passenger_car"):
        """Refreshes all edge weights using dynamic cost model."""
        for u, v, data in self.graph.edges(data=True):
            edge_id = data["edge_id"]
            cost = dynamic_cost_model.compute_edge_cost(
                edge_id=edge_id,
                length_m=data["length_m"],
                speed_limit_mps=data["speed_limit_mps"],
                vehicle_type=vehicle_type
            )
            self.graph[u][v]["weight"] = cost

    def get_edge_id_between(self, u: str, v: str) -> Optional[str]:
        return self.edge_lookup.get((u, v))

    def get_node_coords(self, node_id: str) -> Tuple[float, float]:
        node = self.graph.nodes.get(node_id, {})
        return node.get("x", 0.0), node.get("y", 0.0)


routing_graph = RoutingGraph()
