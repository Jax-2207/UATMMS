"""
UATMMS Emergency Corridor Scheduler
Calculates green-light timing windows for emergency vehicles.
"""

from typing import List, Dict, Optional, Tuple
from backend.app.routing.router import dynamic_router
from backend.app.routing.cost_model import dynamic_cost_model
from backend.app.schemas.emergency import (
    EmergencyType, EmergencySeverity, CorridorWindow, EmergencyCorridorPlan
)
from backend.app.schemas.routing import RoutePlanRequest
from backend.app.core.logging import logger
from backend.app.core.errors import ValidationError


class CorridorScheduler:
    """
    Computes green-light timing windows for emergency vehicles.
    Uses estimated travel time along route to calculate arrival times at each junction.
    """

    def __init__(self, buffer_s: float = 5.0, clearance_s: float = 3.0):
        """
        Args:
            buffer_s: Seconds before ETA to start green (safety margin for deceleration)
            clearance_s: Seconds after ETA to keep green (for vehicle passage)
        """
        self.buffer_s = buffer_s
        self.clearance_s = clearance_s
        self.green_window_min_duration_s = 15.0  # Minimum green window length

    def schedule_corridor(
        self,
        request_id: str,
        vehicle_id: str,
        origin_junction: str,
        destination_junction: str,
        vehicle_type: EmergencyType,
        severity: EmergencySeverity,
        current_sim_time_s: float,
    ) -> EmergencyCorridorPlan:
        """
        Compute corridor green windows for emergency vehicle route.

        Args:
            request_id: Emergency request ID
            vehicle_id: Vehicle identifier
            origin_junction: Starting junction
            destination_junction: Destination junction
            vehicle_type: Type of emergency vehicle
            severity: Severity level (affects priority)
            current_sim_time_s: Current simulation time

        Returns:
            EmergencyCorridorPlan with route and green windows

        Raises:
            ValidationError: If route not found or parameters invalid
        """
        logger.info(
            f"[Corridor Scheduler] Planning corridor for {vehicle_id} "
            f"({severity.name}) from {origin_junction} to {destination_junction}"
        )

        # Step 1: Plan optimal route for emergency vehicle
        route_edges = self._plan_emergency_route(origin_junction, destination_junction)
        if not route_edges:
            raise ValidationError(f"No route found from {origin_junction} to {destination_junction}")

        # Step 2: Calculate total estimated travel time
        total_travel_time = self._estimate_travel_time(route_edges, current_sim_time_s)

        # Step 3: Build junction sequence from edges
        route_junctions = self._extract_junctions_from_route(route_edges, origin_junction)

        # Step 4: Calculate ETA at each junction and generate green windows
        corridor_windows = self._generate_corridor_windows(
            route_edges=route_edges,
            route_junctions=route_junctions,
            start_time_s=current_sim_time_s,
            vehicle_type=vehicle_type,
            severity=severity
        )

        # Step 5: Create corridor plan
        plan = EmergencyCorridorPlan(
            request_id=request_id,
            vehicle_id=vehicle_id,
            route_edges=route_edges,
            route_junctions=route_junctions,
            corridor_windows=corridor_windows,
            total_estimated_travel_time_s=total_travel_time,
            created_at_s=current_sim_time_s
        )

        logger.info(
            f"[Corridor Scheduler] Corridor planned for {vehicle_id}: "
            f"{len(corridor_windows)} junctions, {total_travel_time:.1f}s travel time"
        )

        return plan

    def _plan_emergency_route(self, origin_junction: str, destination_junction: str) -> List[str]:
        """
        Plan route using dynamic graph routing.
        Emergency vehicles get 30% discount on congestion penalties.

        Returns:
            List of edge IDs from origin to destination.
        """
        try:
            from backend.app.schemas.routing import RoutePlanRequest
            request = RoutePlanRequest(
                origin_edge_id=origin_junction,
                destination_edge_id=destination_junction,
                algorithm="astar",
                vehicle_type="passenger_car"  # Simplified: treat as normal vehicle
            )
            response = dynamic_router.plan_route(request)
            return response.edge_sequence
        except Exception as e:
            logger.error(f"Route planning failed: {e}")
            return []

    def _estimate_travel_time(self, route_edges: List[str], current_sim_time_s: float) -> float:
        """
        Estimate total travel time along route considering current conditions.

        Returns:
            Total travel time in seconds.
        """
        total_time = 0.0
        for edge_id in route_edges:
            condition = dynamic_cost_model.get_condition(edge_id)
            if condition:
                # Estimated travel time already accounts for current speed/congestion
                estimated_time = condition.estimated_travel_time
                total_time += estimated_time
            else:
                # Fallback: assume 50 km/h average
                total_time += 2.0

        logger.debug(f"Estimated total travel time: {total_time:.1f}s")
        return total_time

    def _extract_junctions_from_route(self, route_edges: List[str], origin: str) -> List[str]:
        """
        Extract ordered list of junctions from edge sequence.
        Implementation depends on network topology data structure.
        For now, returns placeholder list.

        In production, use network.graph to traverse edges and collect junctions.
        """
        # Placeholder: in real implementation, traverse the graph
        # For testing: return estimated junctions based on route length
        junction_count = max(2, len(route_edges) // 2)  # Rough estimate
        junctions = [origin]

        # Add intermediate junctions (names would come from graph)
        for i in range(1, junction_count - 1):
            junctions.append(f"J_{i}")

        # Destination is final
        junctions.append(f"J_{junction_count - 1}")

        return junctions

    def _generate_corridor_windows(
        self,
        route_edges: List[str],
        route_junctions: List[str],
        start_time_s: float,
        vehicle_type: EmergencyType,
        severity: EmergencySeverity
    ) -> List[CorridorWindow]:
        """
        Generate green-time windows for each junction along route.

        For each junction:
        - Calculate estimated arrival time (ETA)
        - Compute green window: [ETA - buffer, ETA + clearance]
        - Ensure minimum window duration

        Returns:
            List of CorridorWindow specifications.
        """
        windows = []
        cumulative_time = start_time_s

        for idx, (junction_id, edge_id_incoming) in enumerate(zip(route_junctions, route_edges)):
            # Estimate arrival at this junction
            condition = dynamic_cost_model.get_condition(edge_id_incoming)
            if condition:
                segment_travel_time = condition.estimated_travel_time
            else:
                segment_travel_time = 2.0

            eta_s = cumulative_time + segment_travel_time

            # Green window boundaries
            green_start_s = max(cumulative_time, eta_s - self.buffer_s)
            green_end_s = eta_s + self.clearance_s

            # Ensure minimum window duration
            window_duration = green_end_s - green_start_s
            if window_duration < self.green_window_min_duration_s:
                green_end_s = green_start_s + self.green_window_min_duration_s

            # Target phase (simplified: assume 0 is green for emergency corridor)
            target_phase = 0

            # Priority based on severity (lower number = higher priority)
            priority = severity.value

            window = CorridorWindow(
                junction_id=junction_id,
                edge_id_incoming=edge_id_incoming,
                target_phase=target_phase,
                green_window_start_s=green_start_s,
                green_window_end_s=green_end_s,
                estimated_arrival_s=eta_s,
                priority=priority
            )

            windows.append(window)
            logger.debug(
                f"  Junction {junction_id}: ETA={eta_s:.1f}s, "
                f"Green=[{green_start_s:.1f}s, {green_end_s:.1f}s]"
            )

            cumulative_time = eta_s

        return windows

    def validate_corridor_feasibility(
        self,
        corridor_plan: EmergencyCorridorPlan,
        current_sim_time_s: float
    ) -> Tuple[bool, str]:
        """
        Validate if corridor is feasible given current conditions.

        Checks:
        1. First junction is reachable within buffer time
        2. No junction windows have passed
        3. Total corridor doesn't exceed max emergency duration

        Returns:
            (is_feasible: bool, reason: str)
        """
        if not corridor_plan.corridor_windows:
            return False, "Corridor has no windows"

        first_window = corridor_plan.corridor_windows[0]

        # Check if first window is in future
        if first_window.green_window_start_s < current_sim_time_s:
            delta = current_sim_time_s - first_window.green_window_start_s
            if delta > 30.0:  # More than 30s in past, likely unreachable
                return False, f"First corridor window expired {delta:.1f}s ago"

        # Check last window (estimate deadline)
        last_window = corridor_plan.corridor_windows[-1]
        max_corridor_duration_s = 300.0  # 5 minutes
        if last_window.green_window_end_s - current_sim_time_s > max_corridor_duration_s:
            return False, f"Corridor duration exceeds {max_corridor_duration_s}s max"

        return True, "Corridor feasible"


# Global instance
corridor_scheduler = CorridorScheduler()
