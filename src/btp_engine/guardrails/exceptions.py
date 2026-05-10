"""BTP Engine exceptions."""


class BTPEngineError(Exception):
    """Base exception for BTP Engine."""
    pass


class SafetyViolationError(BTPEngineError):
    """Raised when a safety check fails."""
    pass


class CostLimitExceededError(BTPEngineError):
    """Raised when cost limit is exceeded."""
    pass


class ExtractionError(BTPEngineError):
    """Raised when document extraction fails."""
    pass


class ClassificationError(BTPEngineError):
    """Raised when document classification fails."""
    pass