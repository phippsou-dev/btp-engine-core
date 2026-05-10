"""Cost tracking for BTP Engine operations."""

from typing import Dict, Optional
from .exceptions import CostLimitExceededError


class CostTracker:
    """Tracks and limits operational costs."""
    
    def __init__(self, max_cost_usd: float = 10.0):
        self.max_cost_usd = max_cost_usd
        self.current_cost_usd = 0.0
        self.operations: Dict[str, float] = {}
    
    def add_cost(self, operation: str, cost_usd: float) -> None:
        """Add cost for an operation."""
        if cost_usd < 0:
            raise ValueError("Cost cannot be negative")
        
        self.current_cost_usd += cost_usd
        self.operations[operation] = self.operations.get(operation, 0.0) + cost_usd
        
        if self.current_cost_usd > self.max_cost_usd:
            raise CostLimitExceededError(
                f"Cost limit exceeded: ${self.current_cost_usd:.2f} > ${self.max_cost_usd:.2f}"
            )
    
    def get_cost(self) -> float:
        """Get current total cost."""
        return self.current_cost_usd
    
    def get_remaining(self) -> float:
        """Get remaining budget."""
        return max(0.0, self.max_cost_usd - self.current_cost_usd)
    
    def reset(self) -> None:
        """Reset cost tracking."""
        self.current_cost_usd = 0.0
        self.operations.clear()