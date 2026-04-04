# Index Options Scalping Bot

Production-oriented modular bot scaffold for Zerodha Kite Connect intraday index options scalping in `apps/trading`.

## Quick start

1. `pip install -r requirements.txt`
2. `copy .env.example .env` and fill credentials
3. Edit `config/daily_config.json`, `config/candle_patterns.json`, and `levels/YYYY-MM-DD.json`
4. `python main.py`

## Safety defaults

- `DRY_RUN=true` by default (no live order placement).
- Orders are MARKET + MIS and options BUY-only flow is enforced by strategy signal mapping.
- EOD squareoff time is configurable via `.env`.
