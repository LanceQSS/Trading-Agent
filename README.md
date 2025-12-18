# Trading Agent

Deterministic, modular crypto trading system that ingests TradingView alerts, validates them against market context, produces explicit trade decisions, and (optionally) executes orders via Coinbase Advanced (paper mode by default).

## Features
- FastAPI webhook for TradingView alerts with strict Pydantic validation
- Validation engine for trend/indicator/volatility checks with confidence scoring
- Deterministic decision engine enforcing risk constraints and producing ready-to-execute instructions
- Execution engine with paper trading simulator and hook for Coinbase Advanced API
- SQLAlchemy persistence for alerts, validation, decisions, orders, and positions
- Backtesting replay to ensure live and simulated logic stay aligned
- Typed, modular code designed for unit testing

## Project Structure
```
src/trading_agent/
  api/                # FastAPI application
  backtesting/        # Backtest runner
  config/             # Settings management
  db/                 # Database configuration
  models/             # SQLAlchemy ORM entities
  schemas/            # Pydantic models for IO contracts
  services/           # Validation, decision, execution, persistence services
```

## Getting Started
1. Install Poetry and project dependencies:
   ```bash
   poetry install
   ```
2. Run the API (paper trading by default):
   ```bash
   poetry run uvicorn trading_agent.api.main:app --reload
   ```
3. Send a webhook payload to `POST /webhook`:
   ```bash
   curl -X POST http://localhost:8000/webhook \
     -H "Content-Type: application/json" \
     -d @examples/webhook_buy.json
   ```

## Example Payloads
Example TradingView webhook payloads are available in `examples/`.

## Testing
Run the unit suite:
```bash
poetry run pytest
```

## Configuration
Environment variables (or `.env`) can override defaults:
- `DATABASE_URL` (sqlite path by default)
- `PAPER_TRADING` (true/false)
- `MAX_RISK_PER_TRADE`, `MAX_DAILY_LOSS`, `MAX_SYMBOL_EXPOSURE`, `ACCOUNT_EQUITY`

## Backtesting
Use the `Backtester` to replay stored or synthetic alerts through the same validation and decision pipeline to estimate metrics like P&L, win rate, and expectancy.
