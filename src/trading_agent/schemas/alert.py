from __future__ import annotations

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field


class IndicatorPayload(BaseModel):
    RSI: float = Field(..., description="Relative Strength Index")
    MACD: float = Field(..., description="Moving Average Convergence Divergence")
    EMA20: float = Field(..., description="20-period exponential moving average")
    ATR: float = Field(..., description="Average True Range")


class AlertPayload(BaseModel):
    symbol: str = Field(..., pattern="^(ETH|BTC-USD|SOL)$")
    price: float
    signal: str = Field(..., pattern="^(buy|sell)$")
    timeframe: str
    indicators: IndicatorPayload
    timestamp: datetime | None = Field(default=None, description="Optional timestamp from TradingView")


class StoredAlert(BaseModel):
    id: int
    created_at: datetime
    symbol: str
    price: float
    signal: str
    timeframe: str
    indicators: Dict[str, float]

    class Config:
        orm_mode = True
