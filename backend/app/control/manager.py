"""
UATMMS Signal Control Manager
Registers and coordinates all signal controllers, routing simulation step updates
to the active controller policy.
"""
from typing import Dict, Any, Optional
from backend.app.control.base import BaseSignalController
from backend.app.control.fixed_time import FixedTimeController
from backend.app.control.queue_adaptive import QueueAdaptiveController
from backend.app.control.max_pressure import MaxPressureController
from backend.app.core.logging import logger


class SignalControlManager:
    """Manages active signal controllers and runtime switching."""

    def __init__(self):
        self._controllers: Dict[str, BaseSignalController] = {}
        self._active_controller_id: str = "fixed_time"

        # Register baseline controllers
        self.register_controller(FixedTimeController())
        self.register_controller(QueueAdaptiveController())
        self.register_controller(MaxPressureController())

    def register_controller(self, controller: BaseSignalController):
        self._controllers[controller.controller_id] = controller
        logger.info(f"Registered signal controller: '{controller.controller_id}' ({controller.name})")

    def set_active_controller(self, controller_id: str):
        if controller_id not in self._controllers:
            raise ValueError(
                f"Unknown controller '{controller_id}'. Available: {list(self._controllers.keys())}"
            )
        self._active_controller_id = controller_id
        logger.info(f"Active signal controller switched to: '{controller_id}'")

    @property
    def active_controller(self) -> BaseSignalController:
        return self._controllers[self._active_controller_id]

    def get_controller(self, controller_id: str) -> Optional[BaseSignalController]:
        return self._controllers.get(controller_id)

    def list_controllers(self) -> Dict[str, Dict[str, Any]]:
        return {
            cid: ctrl.get_stats()
            for cid, ctrl in self._controllers.items()
        }

    def step(
        self,
        sim_time_s: float,
        junction_states: Dict[str, Any]
    ) -> Dict[str, int]:
        """Dispatches step execution to the currently active controller."""
        return self.active_controller.step(sim_time_s, junction_states)


signal_control_manager = SignalControlManager()
