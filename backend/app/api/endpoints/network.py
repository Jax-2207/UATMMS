from fastapi import APIRouter
from backend.app.network.topology import network_topology

router = APIRouter()


@router.get("/graph", summary="Get Network Graph Visualization Data")
async def get_network_graph():
    return network_topology.to_graph_data()


@router.get("/junctions", summary="Get All Signalized Junctions")
async def get_junctions():
    return list(network_topology.junctions.values())


@router.get("/edges", summary="Get All Network Road Edges")
async def get_edges():
    return list(network_topology.edges.values())
