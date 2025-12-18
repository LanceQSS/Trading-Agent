from trading_agent.schemas.alert import AlertPayload, IndicatorPayload
from trading_agent.services.validation_engine import MarketContext, ValidationEngine


def test_validation_engine_confirms_signal():
    alert = AlertPayload(
        symbol="ETH",
        price=1700.0,
        signal="buy",
        timeframe="5m",
        indicators=IndicatorPayload(RSI=25.0, MACD=0.002, EMA20=1695.0, ATR=10.0),
    )
    context = MarketContext(ema_fast=1690.0, ema_slow=1680.0, vwap=1690.0, atr_baseline=12.0)
    engine = ValidationEngine(context)

    result = engine.evaluate(alert)

    assert result.valid is True
    assert result.confidence >= 40
    assert "RSI oversold" in result.reasons
