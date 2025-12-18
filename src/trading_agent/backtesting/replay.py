from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from trading_agent.schemas.alert import AlertPayload
from trading_agent.schemas.pipeline import TradeDecision
from trading_agent.services.decision_engine import DecisionEngine, RiskState
from trading_agent.services.validation_engine import MarketContext, ValidationEngine


@dataclass
class BacktestResult:
    net_pl: float
    trades: List[TradeDecision]
    win_rate: float
    expectancy: float


class Backtester:
    def __init__(self, context: MarketContext):
        self.context = context
        self.validation_engine = ValidationEngine(context)
        self.decision_engine = DecisionEngine()

    def run(self, alerts: Iterable[AlertPayload]) -> BacktestResult:
        trades: List[TradeDecision] = []
        wins = 0
        total_return = 0.0
        risk_state = RiskState(open_positions={}, daily_loss_fraction=0.0)

        for alert in alerts:
            validation = self.validation_engine.evaluate(alert)
            decision = self.decision_engine.decide(alert, validation, risk_state)
            trades.append(decision)
            if decision.action != decision.action.IGNORE:
                # simple deterministic P&L: assume target hit when confidence high
                profit = decision.size * (decision.take_profit - decision.stop_loss) if decision.action == decision.action.ENTER_LONG else decision.size * (decision.stop_loss - decision.take_profit)
                realized = profit * (validation.confidence / 100)
                total_return += realized
                if realized > 0:
                    wins += 1

        win_rate = wins / len(trades) if trades else 0.0
        expectancy = total_return / len(trades) if trades else 0.0
        return BacktestResult(net_pl=total_return, trades=trades, win_rate=win_rate, expectancy=expectancy)
