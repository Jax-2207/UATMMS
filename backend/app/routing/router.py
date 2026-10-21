"""
UATMMS Dynamic Routing Service
Provides high-level planning and rerouting evaluation with hysteresis to prevent route flapping.
"""
import uuid
from typing import List
from backend.app.schemas.routing import (
    RoutePlanRequest,
    RoutePlanResponse,
    RerouteEvaluationRequest,
    RerouteEvaluationResponse
)
from backend.app.routing.dijkstra import plan_dijkstra_route
from backend.app.routing.astar import plan_astar_route
from backend.app.routing.cost_model import dynamic_cost_model
from backend.app.network.mapping import get_edge_by_id


class DynamicRouter:
    """Unified routing service for UATMMS."""

    def plan_route(self, request: RoutePlanRequest) -> RoutePlanResponse:
        algorithm = (request.algorithm or "astar").lower()

        if algorithm == "dijkstra":
            edges, junctions, dist_m, time_s, nodes_expanded = plan_dijkstra_route(
                origin_edge_id=request.origin_edge_id,
                destination_edge_id=request.destination_edge_id,
                vehicle_type=request.vehicle_type or "passenger_car"
            )
        else:
            edges, junctions, dist_m, time_s, nodes_expanded = plan_astar_route(
                origin_edge_id=request.origin_edge_id,
                destination_edge_id=request.destination_edge_id,
                vehicle_type=request.vehicle_type or "passenger_car"
            )
            algorithm = "astar"

        # Check if any edge in route has incidents
        incident_active = False
        for edge_id in edges:
            cond = dynamic_cost_model.get_condition(edge_id)
            if cond and cond.incident_severity > 0:
                incident_active = True
                break

        return RoutePlanResponse(
            route_id=f"rt_{uuid.uuid4().hex[:8]}",
            origin_edge_id=request.origin_edge_id,
            destination_edge_id=request.destination_edge_id,
            algorithm_used=algorithm,
            edge_sequence=edges,
            junction_sequence=junctions,
            total_distance_m=dist_m,
            estimated_travel_time_s=time_s,
            nodes_expanded=nodes_expanded,
            incident_detour_active=incident_active
        )

    def evaluate_reroute(self, request: RerouteEvaluationRequest) -> RerouteEvaluationResponse:
        """
        Evaluates whether a vehicle should switch to an alternative route.
        Applies a hysteresis threshold (default 15% travel time saving) to prevent oscillations.
        """
        # 1. Calculate remaining travel time on the current route from current_edge_id
        current_route = request.current_route
        curr_edge_idx = -1
        for idx, e in enumerate(current_route):
            if e == request.current_edge_id:
                curr_edge_idx = idx
                break

        if curr_edge_idx == -1:
            # Fallback: current edge not found in current route, treat current edge as start
            remaining_edges = [request.current_edge_id]
        else:
            remaining_edges = current_route[curr_edge_idx:]

        current_remaining_time_s = 0.0
        for edge_id in remaining_edges:
            meta = get_edge_by_id(edge_id)
            if meta:
                cost = dynamic_cost_model.compute_edge_cost(
                    edge_id=edge_id,
                    length_m=meta.length_m,
                    speed_limit_mps=meta.speed_limit_mps
                )
                current_remaining_time_s += cost

        # 2. Plan new candidate route from current_edge_id to destination_edge_id
        plan_req = RoutePlanRequest(
            origin_edge_id=request.current_edge_id,
            destination_edge_id=request.destination_edge_id,
            algorithm="astar"
        )
        candidate_plan = self.plan_route(plan_req)
        candidate_remaining_time_s = candidate_plan.estimated_travel_time_s

        # 3. Calculate relative time saved
        if current_remaining_time_s <= 0.0:
            relative_saving = 0.0
        else:
            relative_saving = (current_remaining_time_s - candidate_remaining_time_s) / current_remaining_time_s

        should_reroute = relative_saving >= request.hysteresis_threshold

        reason = (
            f"Candidate route saves {round(relative_saving * 100, 1)}% time "
            f"(threshold: {round(request.hysteresis_threshold * 100, 1)}%). Reroute recommended."
            if should_reroute
            else f"Time saving {round(relative_saving * 100, 1)}% is below hysteresis threshold "
                 f"({round(request.hysteresis_threshold * 100, 1)}%). Retaining current route."
        )

        recommended_route = candidate_plan.edge_sequence if should_reroute else current_route

        return RerouteEvaluationResponse(
            should_reroute=should_reroute,
            current_remaining_time_s=round(current_remaining_time_s, 2),
            candidate_remaining_time_s=round(candidate_remaining_time_s, 2),
            relative_time_saved_ratio=round(relative_saving, 4),
            recommended_route=recommended_route,
            reason=reason
        )


dynamic_router = DynamicRouter()
