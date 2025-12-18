from __future__ import annotations

from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = Field(default_factory=lambda: f"sqlite:///{Path('data').absolute() / 'trading_agent.db'}")
    environment: str = Field("development", description="Execution environment")
    paper_trading: bool = Field(True, description="Enable paper trading mode")
    max_risk_per_trade: float = Field(0.01, description="Max fraction of equity risked per trade")
    max_daily_loss: float = Field(0.05, description="Max fraction of equity that can be lost in a day")
    max_symbol_exposure: float = Field(0.2, description="Max fraction of equity exposed to a single symbol")
    account_equity: float = Field(10000.0, description="Paper account equity for sizing")

    class Config:
        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()
