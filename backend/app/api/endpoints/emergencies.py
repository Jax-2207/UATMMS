import uuid
from fastapi import APIRouter
from backend.app.schemas.emergency import EmergencyRequest, EmergencyRequestResponse
from backend.app.safety.validator import safety_validator
from backend.app.simulation.manager import simulation_manager

router = APIRouter()


@router.post("/dispatch", response_model=EmergencyRequestResponse, summary="Request Emergency Green Corridor")
async def dispatch_emergency(request: EmergencyRequest):
    req_id = f"emg_{str(uuid.uuid4())[:8]}"
    
    # Representative corridor nodes for demonstration in Phase 0
    assigned_route = [request.origin_edge_id, "E_Brigade_Main", "E_Church_Connect", request.destination_edge_id]
    affected_junctions = ["J1_MG_Road", "J2_Brigade_Rd", "J4_Church_St"]
    
    # Validate each junction with safety validator using current simulation time
    safety_approved = True
    rejection_reason = None
    
    for j_id in affected_junctions:
        valid, reason = safety_validator.validate_phase_transition(
            junction_id=j_id,
            target_phase=1,  # Emergency prioritized green phase
            current_sim_time_s=simulation_manager.sim_time_s,
            is_emergency=True
        )
        if not valid:
            safety_approved = False
            rejection_reason = f"Safety hold on {j_id}: {reason}"
            break

    return GreenCorridorResponse(
        request_id=req_id,
        vehicle_id=request.vehicle_id,
        status="active" if safety_approved else "held_for_clearance",
        assigned_route=assigned_route,
        estimated_travel_time_s=145.0,
        affected_junctions=affected_junctions,
        safety_approved=safety_approved,
        rejection_reason=rejection_reason
    )
