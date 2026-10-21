"""
UATMMS Dynamic Cost Model
Calculates time-dependent edge traversal costs considering queue lengths,
incident severity, closures, and vehicle-specific restrictions.
Formula:
  C_e(t) = travel_time + alpha * queue_penalty + beta * incident_penalty + gamma * restriction_penalty
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DynamicEdgeCondition:
    edge_id: str
    current_speed_mps: float
    queue_count: int = 0
    incident_severity: int = 0  # 0 to 5
    is_closed: bool = False


class DynamicCostModel:
    def __init__(
        self,
        alpha_queue: float = 1.5,
        beta_incident: float = 2.0,
        gamma_restriction: float = 1.0
    ):
        self.alpha_queue = alpha_queue
        self.beta_incident = beta_incident
        self.gamma_restriction = gamma_restriction
        self._conditions: Dict[str, DynamicEdgeCondition] = {}

    def update_condition(
        self,
        edge_id: str,
        current_speed_mps: Optional[float] = None,
        queue_count: int = 0,
        incident_severity: int = 0,
        is_closed: bool = False
    ):
        prev = self._conditions.get(edge_id)
        speed = current_speed_mps if current_speed_mps is not None else (prev.current_speed_mps if prev else 13.89)
        self._conditions[edge_id] = DynamicEdgeCondition(
            edge_id=edge_id,
            current_speed_mps=max(speed, 1.0),
            queue_count=max(queue_count, 0),
            incident_severity=max(incident_severity, 0),
            is_closed=is_closed
        )

    def get_condition(self, edge_id: str) -> Optional[DynamicEdgeCondition]:
        return self._conditions.get(edge_id)

    def compute_edge_cost(
        self,
        edge_id: str,
        length_m: float,
        speed_limit_mps: float,
        vehicle_type: str = "passenger_car"
    ) -> float:
        """
        Computes dynamic cost (in equivalent seconds of travel time).
        Returns infinity (1e9) if edge is completely blocked or closed.
        """
        cond = self._conditions.get(edge_id)

        # 1. Total Closure
        if cond and (cond.is_closed or cond.incident_severity >= 5):
            return 1e9

        # 2. Base Travel Time
        speed = cond.current_speed_mps if cond else speed_limit_mps
        effective_speed = min(speed, speed_limit_mps)
        effective_speed = max(effective_speed, 1.0)
        base_time_s = length_m / effective_speed

        # 3. Queue Penalty (alpha * queued vehicles * 2s stop-and-go delay)
        queue_penalty_s = 0.0
        if cond and cond.queue_count > 0:
            queue_penalty_s = self.alpha_queue * (cond.queue_count * 2.0)

        # 4. Incident Penalty (beta * severity * 20s clearance friction)
        incident_penalty_s = 0.0
        if cond and cond.incident_severity > 0:
            incident_penalty_s = self.beta_incident * (cond.incident_severity * 20.0)

        # 5. Vehicle Type Adjustment
        # Emergency vehicles get green priority window discount
        if vehicle_type in ["ambulance", "emergency_ambulance", "emergency_fire"]:
            queue_penalty_s *= 0.3  # Emergency vehicles bypass partial queues

        total_cost = base_time_s + queue_penalty_s + incident_penalty_s
        return round(total_cost, 2)


# Global cost model instance
dynamic_cost_model = DynamicCostModel()
