from trading_agent.schemas.alert import AlertPayload, IndicatorPayload
from trading_agent.schemas.pipeline import Action
from trading_agent.services.decision_engine import DecisionEngine, RiskState
from trading_agent.schemas.pipeline import ValidationResultSchema


def test_decision_engine_enters_with_valid_signal():
    alert = AlertPayload(
        symbol="ETH",
        price=1700.0,
        signal="buy",
        timeframe="5m",
        indicators=IndicatorPayload(RSI=25.0, MACD=0.01, EMA20=1695.0, ATR=10.0),
    )
    validation = ValidationResultSchema(valid=True, confidence=75, reasons=["RSI oversold"])
    risk_state = RiskState(open_positions={}, daily_loss_fraction=0.0)
    engine = DecisionEngine()

    decision = engine.decide(alert, validation, risk_state)

    assert decision.action == Action.ENTER_LONG
    assert decision.size > 0
    assert decision.stop_loss < alert.price
    assert decision.take_profit > alert.price


def test_decision_engine_ignores_when_confidence_low():
    alert = AlertPayload(
        symbol="ETH",
        price=1700.0,
        signal="buy",
        timeframe="5m",
        indicators=IndicatorPayload(RSI=50.0, MACD=0.0, EMA20=1695.0, ATR=10.0),
    )
    validation = ValidationResultSchema(valid=True, confidence=40, reasons=[])
    risk_state = RiskState(open_positions={}, daily_loss_fraction=0.0)
    engine = DecisionEngine()

    decision = engine.decide(alert, validation, risk_state)

    assert decision.action == Action.IGNORE
    assert decision.size == 0
