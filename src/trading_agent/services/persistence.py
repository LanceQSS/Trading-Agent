from __future__ import annotations

from typing import Any

from trading_agent.db.database import session_scope
from trading_agent.models.entities import Alert, Decision, Order, ValidationResult
from trading_agent.schemas.alert import AlertPayload
from trading_agent.schemas.pipeline import TradeDecision, ValidationResultSchema


def persist_alert(alert: AlertPayload) -> int:
    with session_scope() as session:
        db_alert = Alert(
            symbol=alert.symbol,
            price=alert.price,
            signal=alert.signal,
            timeframe=alert.timeframe,
            indicators=alert.indicators.model_dump(),
        )
        session.add(db_alert)
        session.flush()
        return db_alert.id


def persist_validation(alert_id: int, validation: ValidationResultSchema) -> int:
    with session_scope() as session:
        record = ValidationResult(
            alert_id=alert_id,
            valid=validation.valid,
            confidence=validation.confidence,
            reasons=validation.reasons,
        )
        session.add(record)
        session.flush()
        return record.id


def persist_decision(alert_id: int, decision: TradeDecision) -> int:
    with session_scope() as session:
        record = Decision(
            alert_id=alert_id,
            action=decision.action,
            symbol=decision.symbol,
            order_type=decision.order_type,
            size=decision.size,
            stop_loss=decision.stop_loss,
            take_profit=decision.take_profit,
            confidence=decision.confidence,
        )
        session.add(record)
        session.flush()
        return record.id


def persist_order(decision_id: int, execution: Any) -> int:
    with session_scope() as session:
        record = Order(
            decision_id=decision_id,
            exchange_order_id=execution.order_id,
            status=execution.status,
            filled_size=execution.executed_size,
        )
        session.add(record)
        session.flush()
        return record.id
