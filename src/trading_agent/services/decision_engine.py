from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from trading_agent.config.settings import get_settings
from trading_agent.schemas.alert import AlertPayload
from trading_agent.schemas.pipeline import Action, TradeDecision, ValidationResultSchema


@dataclass
class RiskState:
    open_positions: dict[str, float]
    daily_loss_fraction: float


class DecisionEngine:
    def __init__(self, settings=None):
        self.settings = settings or get_settings()

    def decide(self, alert: AlertPayload, validation: ValidationResultSchema, risk_state: RiskState) -> TradeDecision:
        if not validation.valid:
            return TradeDecision(
                action=Action.IGNORE,
                symbol=alert.symbol,
                order_type="market",
                size=0.0,
                stop_loss=None,
                take_profit=None,
                confidence=validation.confidence,
            )

        if risk_state.daily_loss_fraction >= self.settings.max_daily_loss:
            return self._ignored_decision(alert, validation, "Daily loss limit reached")

        current_exposure = risk_state.open_positions.get(alert.symbol, 0.0)
        if current_exposure >= self.settings.max_symbol_exposure:
            return self._ignored_decision(alert, validation, "Symbol exposure limit reached")

        if validation.confidence < 50:
            return self._ignored_decision(alert, validation, "Confidence too low")

        stop_loss = self._calculate_stop_loss(alert)
        take_profit = self._calculate_take_profit(alert)
        position_size = self._calculate_position_size(alert, stop_loss)

        action = Action.ENTER_LONG if alert.signal == "buy" else Action.ENTER_SHORT
        return TradeDecision(
            action=action,
            symbol=alert.symbol,
            order_type="market",
            size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=validation.confidence,
        )

    def _ignored_decision(self, alert: AlertPayload, validation: ValidationResultSchema, _reason: str) -> TradeDecision:
        return TradeDecision(
            action=Action.IGNORE,
            symbol=alert.symbol,
            order_type="market",
            size=0.0,
            stop_loss=None,
            take_profit=None,
            confidence=validation.confidence,
        )

    def _calculate_stop_loss(self, alert: AlertPayload) -> float:
        atr = alert.indicators.ATR
        if alert.signal == "buy":
            return alert.price - 2 * atr
        return alert.price + 2 * atr

    def _calculate_take_profit(self, alert: AlertPayload) -> float:
        atr = alert.indicators.ATR
        risk_multiple = 2.0
        if alert.signal == "buy":
            return alert.price + risk_multiple * 2 * atr
        return alert.price - risk_multiple * 2 * atr

    def _calculate_position_size(self, alert: AlertPayload, stop_loss: float) -> float:
        risk_per_trade = self.settings.account_equity * self.settings.max_risk_per_trade
        price_distance = abs(alert.price - stop_loss)
        if price_distance == 0:
            return 0.0
        raw_size = risk_per_trade / price_distance
        max_size = self.settings.account_equity * self.settings.max_symbol_exposure / alert.price
        capped_size = min(raw_size, max_size)
        return round(capped_size, 4)
