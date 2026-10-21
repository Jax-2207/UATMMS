"""
UATMMS Network Topology Module
Parses network graph structure, validates connectivity, and provides graph models
for routing, signal coordination, and Command Centre 2D visualization.
"""
from typing import Dict, List, Set, Optional, Any
from backend.app.network.mapping import (
    BENGALURU_JUNCTIONS,
    BENGALURU_EDGES,
    JunctionMetadata,
    EdgeMetadata
)
from backend.app.core.logging import logger


class NetworkTopology:
    """
    Manages static road network topology, junction coordinates, and directed adjacency.
    """

    def __init__(self):
        self.junctions: Dict[str, JunctionMetadata] = BENGALURU_JUNCTIONS
        self.edges: Dict[str, EdgeMetadata] = BENGALURU_EDGES
        self._adjacency: Dict[str, List[str]] = {}
        self._incoming_edges: Dict[str, List[str]] = {}
        self._outgoing_edges: Dict[str, List[str]] = {}
        self._build_topology_index()

    def _build_topology_index(self):
        """Indexes directed adjacency between junctions and edge linkages."""
        for j_id in self.junctions:
            self._adjacency[j_id] = []
            self._incoming_edges[j_id] = []
            self._outgoing_edges[j_id] = []

        for edge_id, edge in self.edges.items():
            u = edge.from_junction
            v = edge.to_junction
            self._adjacency.setdefault(u, [])
            self._adjacency.setdefault(v, [])
            self._incoming_edges.setdefault(v, [])
            self._outgoing_edges.setdefault(u, [])

            if v not in self._adjacency[u]:
                self._adjacency[u].append(v)
            self._incoming_edges[v].append(edge_id)
            self._outgoing_edges[u].append(edge_id)

        logger.info(
            f"NetworkTopology loaded: {len(self.junctions)} junctions, "
            f"{len(self.edges)} directed edges."
        )

    def get_junction(self, junction_id: str) -> Optional[JunctionMetadata]:
        return self.junctions.get(junction_id)

    def get_edge(self, edge_id: str) -> Optional[EdgeMetadata]:
        return self.edges.get(edge_id)

    def get_neighbors(self, junction_id: str) -> List[str]:
        return self._adjacency.get(junction_id, [])

    def get_incoming_edges(self, junction_id: str) -> List[str]:
        return self._incoming_edges.get(junction_id, [])

    def get_outgoing_edges(self, junction_id: str) -> List[str]:
        return self._outgoing_edges.get(junction_id, [])

    def is_connected(self) -> bool:
        """Verifies weak connectivity across all signalized junctions in network."""
        if not self.junctions:
            return True
        start_node = next(iter(self.junctions))
        visited: Set[str] = set()
        queue = [start_node]

        while queue:
            curr = queue.pop(0)
            if curr not in visited:
                visited.add(curr)
                for nbr in self._adjacency.get(curr, []):
                    if nbr not in visited:
                        queue.append(nbr)
                for edge_id in self._incoming_edges.get(curr, []):
                    edge = self.edges.get(edge_id)
                    if edge and edge.from_junction not in visited:
                        queue.append(edge.from_junction)

        return all(j_id in visited for j_id in self.junctions)

    def to_graph_data(self) -> Dict[str, Any]:
        """Formats network topology for Command Centre 2D Canvas and Leaflet."""
        nodes = []
        for j_id, j in self.junctions.items():
            nodes.append({
                "id": j_id,
                "name": j.name,
                "x": j.x_m,
                "y": j.y_m,
                "lat": j.lat,
                "lon": j.lon,
                "signalized": j.signalized,
                "phases": j.phases
            })

        links = []
        for e_id, e in self.edges.items():
            links.append({
                "id": e_id,
                "source": e.from_junction,
                "target": e.to_junction,
                "street_name": e.street_name,
                "length_m": e.length_m,
                "speed_limit_kph": e.speed_limit_kph,
                "lanes": e.lanes,
                "priority": e.priority
            })

        return {
            "network_name": "Bengaluru CBD Core Grid",
            "junction_count": len(nodes),
            "edge_count": len(links),
            "nodes": nodes,
            "links": links
        }


# Singleton topology instance
network_topology = NetworkTopology()
