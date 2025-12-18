from __future__ import annotations

from dataclasses import dataclass
from typing import List

from trading_agent.schemas.alert import AlertPayload
from trading_agent.schemas.pipeline import ValidationResultSchema


@dataclass
class MarketContext:
    ema_fast: float
    ema_slow: float
    vwap: float | None
    atr_baseline: float


class ValidationEngine:
    def __init__(self, context: MarketContext):
        self.context = context

    def evaluate(self, alert: AlertPayload) -> ValidationResultSchema:
        reasons: List[str] = []
        confidence = 0

        indicators = alert.indicators

        # Trend alignment
        if indicators.EMA20 >= self.context.ema_slow and indicators.EMA20 >= indicators.RSI:
            reasons.append("EMA trend aligned")
            confidence += 20
        else:
            reasons.append("EMA trend misaligned")

        if self.context.vwap is not None:
            if alert.price >= self.context.vwap:
                reasons.append("Price above VWAP")
                confidence += 10
            else:
                reasons.append("Price below VWAP")

        # Indicator confirmation
        if indicators.RSI < 30 and alert.signal == "buy":
            reasons.append("RSI oversold")
            confidence += 25
        elif indicators.RSI > 70 and alert.signal == "sell":
            reasons.append("RSI overbought")
            confidence += 25
        else:
            reasons.append("RSI neutral")

        if indicators.MACD > 0 and alert.signal == "buy":
            reasons.append("MACD bullish")
            confidence += 15
        elif indicators.MACD < 0 and alert.signal == "sell":
            reasons.append("MACD bearish")
            confidence += 15
        else:
            reasons.append("MACD unconfirmed")

        # Volatility regime
        if indicators.ATR <= 1.5 * self.context.atr_baseline:
            reasons.append("ATR normal")
            confidence += 10
        else:
            reasons.append("ATR elevated")
            confidence = max(confidence - 10, 0)

        valid = confidence >= 40
        return ValidationResultSchema(valid=valid, confidence=min(confidence, 100), reasons=reasons)
