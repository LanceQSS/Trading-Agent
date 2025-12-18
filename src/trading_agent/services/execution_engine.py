from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from trading_agent.config.settings import get_settings
from trading_agent.schemas.pipeline import ExecutionResult, TradeDecision

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    paper_trading: bool = True


class ExecutionEngine:
    def __init__(self, context: Optional[ExecutionContext] = None):
        settings = get_settings()
        self.context = context or ExecutionContext(paper_trading=settings.paper_trading)

    def execute(self, decision: TradeDecision) -> ExecutionResult:
        if decision.action == decision.action.IGNORE:
            return ExecutionResult(success=True, order_id=None, status="ignored", executed_size=0.0)

        try:
            if self.context.paper_trading:
                order_id = self._simulate_order(decision)
                status = "filled"
                executed_size = decision.size
            else:
                # Placeholder for live Coinbase Advanced API integration
                order_id = "live-order"
                status = "submitted"
                executed_size = 0.0

            return ExecutionResult(success=True, order_id=order_id, status=status, executed_size=executed_size)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Execution failed: %s", exc)
            return ExecutionResult(success=False, order_id=None, status="failed", executed_size=0.0, error=str(exc))

    def _simulate_order(self, decision: TradeDecision) -> str:
        pseudo_id = f"paper-{decision.symbol}-{abs(hash((decision.action, decision.size)))}"
        return pseudo_id
