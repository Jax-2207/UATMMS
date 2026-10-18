from typing import Optional, Any, Dict


class UATMMSError(Exception):
    """Base exception for all UATMMS domain errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SafetyViolationError(UATMMSError):
    """Raised when a control action violates safety constraints."""
    pass


class SimulationError(UATMMSError):
    """Raised when the simulation fails to execute or TraCI disconnects."""
    pass


class RoutingError(UATMMSError):
    """Raised when route planning fails or paths are blocked."""
    pass


class AuthorizationError(UATMMSError):
    """Raised when a user lacks required permissions."""
    pass
