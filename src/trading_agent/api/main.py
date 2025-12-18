from __future__ import annotations

import logging
from fastapi import FastAPI, HTTPException

from trading_agent.db.database import Base, get_engine
from trading_agent.schemas.alert import AlertPayload
from trading_agent.schemas.pipeline import ExecutionResult
from trading_agent.services.decision_engine import DecisionEngine, RiskState
from trading_agent.services.execution_engine import ExecutionEngine
from trading_agent.services.persistence import (
    persist_alert,
    persist_decision,
    persist_order,
    persist_validation,
)
from trading_agent.services.validation_engine import MarketContext, ValidationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Deterministic Trading Agent")

# Create tables at startup
Base.metadata.create_all(bind=get_engine())


@app.post("/webhook", response_model=ExecutionResult)
async def handle_webhook(alert: AlertPayload) -> ExecutionResult:
    try:
        alert_id = persist_alert(alert)
    except Exception as exc:
        logger.exception("Failed to persist alert")
        raise HTTPException(status_code=500, detail="Could not persist alert") from exc

    # For demo purposes, context values are placeholders; in production they'd come from market data feeds
    context = MarketContext(ema_fast=alert.indicators.EMA20, ema_slow=alert.indicators.EMA20 * 0.99, vwap=alert.price * 0.995, atr_baseline=alert.indicators.ATR)
    validator = ValidationEngine(context)
    validation = validator.evaluate(alert)
    persist_validation(alert_id, validation)

    risk_state = RiskState(open_positions={}, daily_loss_fraction=0.0)
    decision_engine = DecisionEngine()
    decision = decision_engine.decide(alert, validation, risk_state)
    decision_id = persist_decision(alert_id, decision)

    execution_engine = ExecutionEngine()
    execution = execution_engine.execute(decision)
    persist_order(decision_id, execution)

    return execution


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
