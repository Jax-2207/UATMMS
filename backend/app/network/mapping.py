"""
UATMMS Network Mapping Module
Provides authoritative, bidirectional mappings between human-readable domain IDs,
SUMO network object identifiers, geographic coordinates, and signal phase configurations.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class JunctionMetadata(BaseModel):
    junction_id: str
    name: str
    sumo_id: str
    x_m: float
    y_m: float
    lat: float
    lon: float
    signalized: bool = True
    min_green_s: float = 10.0
    max_green_s: float = 90.0
    phases: List[str] = [
        "North-South Green",
        "North-South Yellow",
        "All Red Clearance",
        "East-West Green",
        "East-West Yellow",
        "All Red Clearance"
    ]


class EdgeMetadata(BaseModel):
    edge_id: str
    street_name: str
    sumo_edge_id: str
    from_junction: str
    to_junction: str
    length_m: float
    speed_limit_mps: float
    speed_limit_kph: float
    lanes: int
    priority: int


# Authoritative Bangalore CBD Core Topology
BENGALURU_JUNCTIONS: Dict[str, JunctionMetadata] = {
    "J1_MG_Road": JunctionMetadata(
        junction_id="J1_MG_Road",
        name="MG Road - Anil Kumble Circle",
        sumo_id="J1_MG_Road",
        x_m=250.0,
        y_m=550.0,
        lat=12.9756,
        lon=77.6066
    ),
    "J2_Brigade_Rd": JunctionMetadata(
        junction_id="J2_Brigade_Rd",
        name="MG Road - Brigade Road Junction",
        sumo_id="J2_Brigade_Rd",
        x_m=550.0,
        y_m=550.0,
        lat=12.9748,
        lon=77.6092
    ),
    "J3_Residency_Rd": JunctionMetadata(
        junction_id="J3_Residency_Rd",
        name="Residency Road - Mayo Hall Junction",
        sumo_id="J3_Residency_Rd",
        x_m=850.0,
        y_m=550.0,
        lat=12.9739,
        lon=77.6120
    ),
    "J4_Church_St": JunctionMetadata(
        junction_id="J4_Church_St",
        name="Church Street - Museum Road Junction",
        sumo_id="J4_Church_St",
        x_m=250.0,
        y_m=250.0,
        lat=12.9732,
        lon=77.6055
    ),
    "J5_Commercial_St": JunctionMetadata(
        junction_id="J5_Commercial_St",
        name="Commercial Street - Kamaraj Road Crossing",
        sumo_id="J5_Commercial_St",
        x_m=550.0,
        y_m=250.0,
        lat=12.9723,
        lon=77.6080
    ),
    "J6_Lavelle_Rd": JunctionMetadata(
        junction_id="J6_Lavelle_Rd",
        name="Lavelle Road - Richmond Circle Connector",
        sumo_id="J6_Lavelle_Rd",
        x_m=850.0,
        y_m=250.0,
        lat=12.9715,
        lon=77.6105
    ),
}

BENGALURU_EDGES: Dict[str, EdgeMetadata] = {
    # Top Arterial Corridor: MG Road Eastbound & Westbound
    "E_MG_J1_J2": EdgeMetadata(
        edge_id="E_MG_J1_J2",
        street_name="Mahatma Gandhi Road (Eastbound)",
        sumo_edge_id="E_MG_J1_J2",
        from_junction="J1_MG_Road",
        to_junction="J2_Brigade_Rd",
        length_m=260.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=3
    ),
    "E_MG_J2_J1": EdgeMetadata(
        edge_id="E_MG_J2_J1",
        street_name="Mahatma Gandhi Road (Westbound)",
        sumo_edge_id="E_MG_J2_J1",
        from_junction="J2_Brigade_Rd",
        to_junction="J1_MG_Road",
        length_m=260.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=3
    ),
    "E_MG_J2_J3": EdgeMetadata(
        edge_id="E_MG_J2_J3",
        street_name="MG Road Ext - Mayo Hall (Eastbound)",
        sumo_edge_id="E_MG_J2_J3",
        from_junction="J2_Brigade_Rd",
        to_junction="J3_Residency_Rd",
        length_m=260.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=3
    ),
    "E_MG_J3_J2": EdgeMetadata(
        edge_id="E_MG_J3_J2",
        street_name="MG Road Ext - Mayo Hall (Westbound)",
        sumo_edge_id="E_MG_J3_J2",
        from_junction="J3_Residency_Rd",
        to_junction="J2_Brigade_Rd",
        length_m=260.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=3
    ),

    # Central Cross-Corridor: Brigade Road (North-South)
    "E_BRIGADE_J2_J5": EdgeMetadata(
        edge_id="E_BRIGADE_J2_J5",
        street_name="Brigade Road Commercial Strip (Southbound)",
        sumo_edge_id="E_BRIGADE_J2_J5",
        from_junction="J2_Brigade_Rd",
        to_junction="J5_Commercial_St",
        length_m=260.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=3
    ),
    "E_BRIGADE_J5_J2": EdgeMetadata(
        edge_id="E_BRIGADE_J5_J2",
        street_name="Brigade Road Commercial Strip (Northbound)",
        sumo_edge_id="E_BRIGADE_J5_J2",
        from_junction="J5_Commercial_St",
        to_junction="J2_Brigade_Rd",
        length_m=260.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=3
    ),

    # Lower Horizontal Corridor: Church Street & Commercial Street
    "E_CH_J4_J5": EdgeMetadata(
        edge_id="E_CH_J4_J5",
        street_name="Church Street Corridor (Eastbound)",
        sumo_edge_id="E_CH_J4_J5",
        from_junction="J4_Church_St",
        to_junction="J5_Commercial_St",
        length_m=260.0,
        speed_limit_mps=11.11,
        speed_limit_kph=40.0,
        lanes=2,
        priority=2
    ),
    "E_CH_J5_J4": EdgeMetadata(
        edge_id="E_CH_J5_J4",
        street_name="Church Street Corridor (Westbound)",
        sumo_edge_id="E_CH_J5_J4",
        from_junction="J5_Commercial_St",
        to_junction="J4_Church_St",
        length_m=260.0,
        speed_limit_mps=11.11,
        speed_limit_kph=40.0,
        lanes=2,
        priority=2
    ),
    "E_CO_J5_J6": EdgeMetadata(
        edge_id="E_CO_J5_J6",
        street_name="Commercial Street Link (Eastbound)",
        sumo_edge_id="E_CO_J5_J6",
        from_junction="J5_Commercial_St",
        to_junction="J6_Lavelle_Rd",
        length_m=260.0,
        speed_limit_mps=11.11,
        speed_limit_kph=40.0,
        lanes=2,
        priority=2
    ),
    "E_CO_J6_J5": EdgeMetadata(
        edge_id="E_CO_J6_J5",
        street_name="Commercial Street Link (Westbound)",
        sumo_edge_id="E_CO_J6_J5",
        from_junction="J6_Lavelle_Rd",
        to_junction="J5_Commercial_St",
        length_m=260.0,
        speed_limit_mps=11.11,
        speed_limit_kph=40.0,
        lanes=2,
        priority=2
    ),

    # Vertical Links
    "E_VERT_J1_J4": EdgeMetadata(
        edge_id="E_VERT_J1_J4",
        street_name="Museum Road Connector (Southbound)",
        sumo_edge_id="E_VERT_J1_J4",
        from_junction="J1_MG_Road",
        to_junction="J4_Church_St",
        length_m=260.0,
        speed_limit_mps=11.11,
        speed_limit_kph=40.0,
        lanes=2,
        priority=2
    ),
    "E_VERT_J4_J1": EdgeMetadata(
        edge_id="E_VERT_J4_J1",
        street_name="Museum Road Connector (Northbound)",
        sumo_edge_id="E_VERT_J4_J1",
        from_junction="J4_Church_St",
        to_junction="J1_MG_Road",
        length_m=260.0,
        speed_limit_mps=11.11,
        speed_limit_kph=40.0,
        lanes=2,
        priority=2
    ),
    "E_VERT_J3_J6": EdgeMetadata(
        edge_id="E_VERT_J3_J6",
        street_name="Lavelle Road South Connector (Southbound)",
        sumo_edge_id="E_VERT_J3_J6",
        from_junction="J3_Residency_Rd",
        to_junction="J6_Lavelle_Rd",
        length_m=260.0,
        speed_limit_mps=11.11,
        speed_limit_kph=40.0,
        lanes=2,
        priority=2
    ),
    "E_VERT_J6_J3": EdgeMetadata(
        edge_id="E_VERT_J6_J3",
        street_name="Lavelle Road South Connector (Northbound)",
        sumo_edge_id="E_VERT_J6_J3",
        from_junction="J6_Lavelle_Rd",
        to_junction="J3_Residency_Rd",
        length_m=260.0,
        speed_limit_mps=11.11,
        speed_limit_kph=40.0,
        lanes=2,
        priority=2
    ),

    # Perimeter Ingress / Egress Links
    "E_W1_in": EdgeMetadata(
        edge_id="E_W1_in",
        street_name="MG Road West Entry (Kumble Circle Ingress)",
        sumo_edge_id="E_W1_in",
        from_junction="ENTRY_W1",
        to_junction="J1_MG_Road",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_W1_out": EdgeMetadata(
        edge_id="E_W1_out",
        street_name="MG Road West Exit (Kumble Circle Egress)",
        sumo_edge_id="E_W1_out",
        from_junction="J1_MG_Road",
        to_junction="ENTRY_W1",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_E3_in": EdgeMetadata(
        edge_id="E_E3_in",
        street_name="Old Airport Road / Trinity Ingress",
        sumo_edge_id="E_E3_in",
        from_junction="ENTRY_E3",
        to_junction="J3_Residency_Rd",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_E3_out": EdgeMetadata(
        edge_id="E_E3_out",
        street_name="Old Airport Road / Trinity Egress",
        sumo_edge_id="E_E3_out",
        from_junction="J3_Residency_Rd",
        to_junction="ENTRY_E3",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_N1_in": EdgeMetadata(
        edge_id="E_N1_in",
        street_name="Cubbon Park North Ingress",
        sumo_edge_id="E_N1_in",
        from_junction="ENTRY_N1",
        to_junction="J1_MG_Road",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_N1_out": EdgeMetadata(
        edge_id="E_N1_out",
        street_name="Cubbon Park North Egress",
        sumo_edge_id="E_N1_out",
        from_junction="J1_MG_Road",
        to_junction="ENTRY_N1",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_N2_in": EdgeMetadata(
        edge_id="E_N2_in",
        street_name="MG Road North Ingress (Cubbon Rd)",
        sumo_edge_id="E_N2_in",
        from_junction="ENTRY_N2",
        to_junction="J2_Brigade_Rd",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_N2_out": EdgeMetadata(
        edge_id="E_N2_out",
        street_name="MG Road North Egress (Cubbon Rd)",
        sumo_edge_id="E_N2_out",
        from_junction="J2_Brigade_Rd",
        to_junction="ENTRY_N2",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_N3_in": EdgeMetadata(
        edge_id="E_N3_in",
        street_name="Halasuru North Ingress",
        sumo_edge_id="E_N3_in",
        from_junction="ENTRY_N3",
        to_junction="J3_Residency_Rd",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
    "E_N3_out": EdgeMetadata(
        edge_id="E_N3_out",
        street_name="Halasuru North Egress",
        sumo_edge_id="E_N3_out",
        from_junction="J3_Residency_Rd",
        to_junction="ENTRY_N3",
        length_m=230.0,
        speed_limit_mps=13.89,
        speed_limit_kph=50.0,
        lanes=2,
        priority=2
    ),
}


def get_junction_by_id(junction_id: str) -> Optional[JunctionMetadata]:
    return BENGALURU_JUNCTIONS.get(junction_id)


def get_edge_by_id(edge_id: str) -> Optional[EdgeMetadata]:
    return BENGALURU_EDGES.get(edge_id)


def get_all_junctions() -> List[JunctionMetadata]:
    return list(BENGALURU_JUNCTIONS.values())


def get_all_edges() -> List[EdgeMetadata]:
    return list(BENGALURU_EDGES.values())
