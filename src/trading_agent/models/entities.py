from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, Integer, JSON, String

from trading_agent.db.database import Base


class SignalAction(str, Enum):
    ENTER_LONG = "ENTER_LONG"
    ENTER_SHORT = "ENTER_SHORT"
    IGNORE = "IGNORE"


class Alert(Base):
    __tablename__ = "alerts"

    id: int = Column(Integer, primary_key=True, index=True)
    symbol: str = Column(String, nullable=False)
    price: float = Column(Float, nullable=False)
    signal: str = Column(String, nullable=False)
    timeframe: str = Column(String, nullable=False)
    indicators: dict = Column(JSON, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: int = Column(Integer, primary_key=True, index=True)
    alert_id: int = Column(Integer, nullable=False)
    valid: bool = Column(Boolean, default=False)
    confidence: int = Column(Integer, default=0)
    reasons: list[str] = Column(JSON, default=list)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class Decision(Base):
    __tablename__ = "decisions"

    id: int = Column(Integer, primary_key=True, index=True)
    alert_id: int = Column(Integer, nullable=False)
    action: SignalAction = Column(SAEnum(SignalAction), nullable=False)
    symbol: str = Column(String, nullable=False)
    order_type: str = Column(String, nullable=False)
    size: float = Column(Float, nullable=False)
    stop_loss: Optional[float] = Column(Float)
    take_profit: Optional[float] = Column(Float)
    confidence: int = Column(Integer, default=0)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id: int = Column(Integer, primary_key=True, index=True)
    decision_id: int = Column(Integer, nullable=False)
    exchange_order_id: Optional[str] = Column(String)
    status: str = Column(String, default="pending")
    filled_size: float = Column(Float, default=0.0)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


class Position(Base):
    __tablename__ = "positions"

    id: int = Column(Integer, primary_key=True, index=True)
    symbol: str = Column(String, nullable=False)
    size: float = Column(Float, nullable=False)
    entry_price: float = Column(Float, nullable=False)
    stop_loss: Optional[float] = Column(Float)
    take_profit: Optional[float] = Column(Float)
    open: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at: Optional[datetime] = Column(DateTime)
