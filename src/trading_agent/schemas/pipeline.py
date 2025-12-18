from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ValidationResultSchema(BaseModel):
    valid: bool
    confidence: int = Field(ge=0, le=100)
    reasons: List[str] = Field(default_factory=list)


class Action(str, Enum):
    ENTER_LONG = "ENTER_LONG"
    ENTER_SHORT = "ENTER_SHORT"
    IGNORE = "IGNORE"


class TradeDecision(BaseModel):
    action: Action
    symbol: str
    order_type: str
    size: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    confidence: int


class ExecutionResult(BaseModel):
    success: bool
    order_id: Optional[str]
    status: str
    executed_size: float
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
