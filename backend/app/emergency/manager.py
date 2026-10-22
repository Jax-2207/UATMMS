"""
UATMMS Emergency Request Manager
Handles emergency request lifecycle and corridor activation.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from backend.app.schemas.emergency import (
    EmergencyRequest, EmergencyRequestResponse, EmergencyStatus,
    EmergencyCorridorPlan, EmergencyStatusUpdate, EmergencyCompletionReport
)
from backend.app.emergency.corridor_scheduler import corridor_scheduler
from backend.app.emergency.arbitration import emergency_arbitrator
from backend.app.safety.validator import safety_validator
from backend.app.core.logging import logger
from backend.app.core.errors import ValidationError
import uuid


class EmergencyRequestRecord:
    """Internal tracking for emergency requests."""

    def __init__(self, request_id: str, req: EmergencyRequest, sim_time_s: float):
        self.request_id = request_id
        self.vehicle_id = req.vehicle_id
        self.origin = req.origin_junction
        self.destination = req.destination_junction
        self.vehicle_type = req.vehicle_type
        self.severity = req.severity
        self.requester_id = req.requester_id
        self.status = EmergencyStatus.REQUESTED
        self.corridor_plan: Optional[EmergencyCorridorPlan] = None
        self.created_at_s = sim_time_s
        self.activated_at_s: Optional[float] = None
        self.completed_at_s: Optional[float] = None
        self.red_signals_encountered = 0
        self.actual_travel_time_s: Optional[float] = None
        self.metadata = req.metadata
        self.safety_violations = 0

    def to_response(self) -> EmergencyRequestResponse:
        """Convert to API response."""
        return EmergencyRequestResponse(
            request_id=self.request_id,
            vehicle_id=self.vehicle_id,
            status=self.status,
            corridor_plan=self.corridor_plan,
            created_at=datetime.now(),
            message=f"Emergency {self.status.value}"
        )


class EmergencyRequestManager:
    """
    Manages emergency request lifecycle:
    1. Request submission and validation
    2. Route planning and corridor scheduling
    3. Conflict arbitration
    4. Corridor activation and signal control
    5. Completion and metrics
    """

    def __init__(self):
        self.requests: Dict[str, EmergencyRequestRecord] = {}
        self.pending_requests: List[str] = []  # Awaiting corridor activation
        self.active_corridors: Dict[str, EmergencyCorridorPlan] = {}  # Currently active
        self.completed_requests: Dict[str, EmergencyRequestRecord] = {}
        self.max_concurrent_corridors = 3  # Safety limit

    def create_emergency_request(
        self,
        req: EmergencyRequest,
        current_sim_time_s: float
    ) -> EmergencyRequestResponse:
        """
        Create and process emergency request.

        Args:
            req: Emergency request details
            current_sim_time_s: Current simulation time

        Returns:
            EmergencyRequestResponse with assigned request ID

        Raises:
            ValidationError: If request invalid or system overloaded
        """
        # Validation
        if req.origin_junction == req.destination_junction:
            raise ValidationError("Origin and destination cannot be the same")

        if not req.vehicle_id or not req.requester_id:
            raise ValidationError("vehicle_id and requester_id required")

        # Check if already at max concurrent corridors
        if len(self.active_corridors) >= self.max_concurrent_corridors:
            logger.warning(
                f"[EmergencyManager] Max concurrent corridors ({self.max_concurrent_corridors}) reached. "
                f"Queueing request."
            )

        # Create request record
        request_id = str(uuid.uuid4())[:8]
        record = EmergencyRequestRecord(request_id, req, current_sim_time_s)

        self.requests[request_id] = record
        self.pending_requests.append(request_id)

        logger.info(
            f"[EmergencyManager] Created emergency request {request_id} for {req.vehicle_id} "
            f"({req.severity.name}): {req.origin_junction} → {req.destination_junction}"
        )

        # Process corridor scheduling and arbitration
        self._process_pending_requests(current_sim_time_s)

        # Return updated response
        return record.to_response()

    def _process_pending_requests(self, current_sim_time_s: float):
        """Process queued requests: schedule corridors and arbitrate conflicts."""
        if not self.pending_requests:
            return

        logger.debug(f"[EmergencyManager] Processing {len(self.pending_requests)} pending requests")

        # Get all pending request details
        corridor_candidates: List[Tuple[str, EmergencyCorridorPlan]] = []

        for request_id in self.pending_requests[:]:  # Copy to allow modification during iteration
            record = self.requests[request_id]

            # Plan corridor for this request
            try:
                plan = corridor_scheduler.schedule_corridor(
                    request_id=request_id,
                    vehicle_id=record.vehicle_id,
                    origin_junction=record.origin,
                    destination_junction=record.destination,
                    vehicle_type=record.vehicle_type,
                    severity=record.severity,
                    current_sim_time_s=current_sim_time_s
                )

                # Check feasibility
                is_feasible, reason = corridor_scheduler.validate_corridor_feasibility(plan, current_sim_time_s)
                if is_feasible:
                    corridor_candidates.append((request_id, plan))
                    record.corridor_plan = plan
                    record.status = EmergencyStatus.ROUTE_PLANNED
                    logger.debug(f"[EmergencyManager] Corridor planned for {request_id}")
                else:
                    record.status = EmergencyStatus.FAILED
                    logger.error(f"[EmergencyManager] Corridor infeasible for {request_id}: {reason}")

            except ValidationError as e:
                record.status = EmergencyStatus.FAILED
                logger.error(f"[EmergencyManager] Failed to plan corridor for {request_id}: {e}")

        # If multiple candidates, arbitrate conflicts
        if corridor_candidates:
            arbitrated = emergency_arbitrator.evaluate_conflict(corridor_candidates)

            # Update with arbitrated plans
            for request_id, final_plan in arbitrated.items():
                self.requests[request_id].corridor_plan = final_plan

            # Activate corridors
            self._activate_corridors(arbitrated, current_sim_time_s)

            # Remove processed requests from pending
            self.pending_requests = [
                r for r in self.pending_requests
                if r not in arbitrated
            ]

    def _activate_corridors(
        self,
        arbitrated_plans: Dict[str, EmergencyCorridorPlan],
        current_sim_time_s: float
    ):
        """Activate approved corridors: apply signal control and track progress."""
        for request_id, plan in arbitrated_plans.items():
            record = self.requests[request_id]

            # Validate each green window through safety layer
            all_windows_valid = True
            for window in plan.corridor_windows:
                # Safety check: can we enforce this green window?
                is_valid, reason = safety_validator.validate_phase_transition(
                    junction_id=window.junction_id,
                    target_phase=window.target_phase,
                    current_sim_time_s=current_sim_time_s,
                    is_emergency=True
                )

                if not is_valid:
                    logger.warning(
                        f"[EmergencyManager] Safety rejected window for {request_id} at "
                        f"{window.junction_id}: {reason}"
                    )
                    all_windows_valid = False
                    record.safety_violations += 1
                    break

            if all_windows_valid:
                # Activate the corridor
                self.active_corridors[request_id] = plan
                record.status = EmergencyStatus.CORRIDOR_ACTIVE
                record.activated_at_s = current_sim_time_s

                logger.info(
                    f"[EmergencyManager] ACTIVATED corridor for {request_id}: "
                    f"{len(plan.corridor_windows)} junction windows"
                )
            else:
                record.status = EmergencyStatus.FAILED
                logger.error(f"[EmergencyManager] Corridor activation failed for {request_id}")

    def update_emergency_status(
        self,
        update: EmergencyStatusUpdate,
        current_sim_time_s: float
    ) -> Tuple[bool, str]:
        """
        Update emergency vehicle progress.

        Called as vehicle moves through corridor to track completion.

        Returns:
            (success: bool, message: str)
        """
        request_id = update.request_id

        if request_id not in self.requests:
            return False, f"Request {request_id} not found"

        record = self.requests[request_id]

        # Update counters
        record.red_signals_encountered = max(record.red_signals_encountered, update.red_signals_encountered)

        # Check if reached destination
        if update.status == EmergencyStatus.COMPLETED:
            record.completed_at_s = current_sim_time_s
            record.actual_travel_time_s = current_sim_time_s - record.created_at_s
            record.status = EmergencyStatus.COMPLETED

            # Remove from active corridors
            if request_id in self.active_corridors:
                del self.active_corridors[request_id]

            # Move to completed
            self.completed_requests[request_id] = record

            logger.info(
                f"[EmergencyManager] Emergency {request_id} COMPLETED: "
                f"actual travel time {record.actual_travel_time_s:.1f}s, "
                f"red signals {record.red_signals_encountered}"
            )

        return True, "Status updated"

    def complete_emergency(
        self,
        request_id: str,
        completion_report: EmergencyCompletionReport,
        current_sim_time_s: float
    ) -> EmergencyRequestResponse:
        """
        Mark emergency as completed and record metrics.

        Args:
            request_id: Emergency request ID
            completion_report: Final metrics and status
            current_sim_time_s: Current simulation time

        Returns:
            Updated EmergencyRequestResponse
        """
        if request_id not in self.requests:
            raise ValidationError(f"Request {request_id} not found")

        record = self.requests[request_id]
        record.status = EmergencyStatus.COMPLETED
        record.completed_at_s = current_sim_time_s
        record.actual_travel_time_s = completion_report.actual_travel_time_s
        record.red_signals_encountered = completion_report.red_signals_encountered
        record.safety_violations = completion_report.safety_violations

        # Move to completed
        if request_id in self.active_corridors:
            del self.active_corridors[request_id]
        self.completed_requests[request_id] = record

        logger.info(
            f"[EmergencyManager] Completed {request_id}: "
            f"Travel time {completion_report.actual_travel_time_s:.1f}s, "
            f"Red signals {completion_report.red_signals_encountered}, "
            f"Status {completion_report.completion_status}"
        )

        return record.to_response()

    def get_active_corridors(self) -> List[EmergencyCorridorPlan]:
        """Get all currently active emergency corridors."""
        return list(self.active_corridors.values())

    def get_request_status(self, request_id: str) -> Optional[EmergencyRequestResponse]:
        """Get current status of emergency request."""
        if request_id not in self.requests:
            return None

        return self.requests[request_id].to_response()

    def get_statistics(self) -> Dict:
        """Get emergency system statistics."""
        total_requests = len(self.requests)
        active = len(self.active_corridors)
        completed = len(self.completed_requests)

        total_red_signals = sum(r.red_signals_encountered for r in self.completed_requests.values())
        total_violations = sum(r.safety_violations for r in self.completed_requests.values())
        avg_travel_time = (
            sum(r.actual_travel_time_s or 0 for r in self.completed_requests.values()) / completed
            if completed > 0 else 0
        )

        return {
            "total_requests": total_requests,
            "active_corridors": active,
            "completed": completed,
            "average_travel_time_s": avg_travel_time,
            "total_red_signals_encountered": total_red_signals,
            "total_safety_violations": total_violations,
            "max_concurrent_corridors": self.max_concurrent_corridors
        }


# Global instance
emergency_manager = EmergencyRequestManager()
