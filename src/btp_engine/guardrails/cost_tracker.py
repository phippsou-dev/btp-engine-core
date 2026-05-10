"""Cost tracking for BTP Engine operations."""

from typing import Dict, Optional
from .exceptions import CostLimitExceededError, GuardrailViolation


class CostTracker:
    """Tracks and limits operational costs."""
    
    def __init__(self, max_cost_usd: float = 0.0):
        self.max_cost_usd = max_cost_usd
        self.current_cost_usd = 0.0
        self.operations: Dict[str, float] = {}
    
    def add_cost(self, operation: str, cost_usd: float) -> None:
        """Add cost for an operation.
        
        Args:
            operation: Operation name
            cost_usd: Cost in USD
            
        Raises:
            GuardrailViolation: If any cost is added when max is 0
            CostLimitExceededError: If cost exceeds limit
        """
        if cost_usd < 0:
            raise ValueError("Cost cannot be negative")
        
        # Strict guardrail: any cost > 0 when max is 0 is forbidden
        if self.max_cost_usd == 0.0 and cost_usd > 0.0:
            raise GuardrailViolation(
                f"Cost guardrail violated: cannot add {cost_usd} USD when max_cost_usd is 0.0"
            )
        
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