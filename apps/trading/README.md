# Index Options Scalping Bot

Production-oriented modular bot scaffold for Zerodha Kite Connect intraday index options scalping in `apps/trading`.

## Quick start

1. `pip install -r requirements.txt`
2. `copy .env.example .env` and fill credentials
3. Run [apps/Api](../Api) (MongoDB). Edit levels in [apps/Web](../Web) or via API.
4. Set **`TRADEKING_API_URL`** in `apps/trading/.env` to your API base (e.g. `http://localhost:3001`). The bot calls **`GET /api/v1/levels/{date}`** and **`GET /api/v1/kite/request-token`** on that host only (no API key). Legacy alias: `LEVELS_API_URL`. **Levels load only from the API** (no local JSON). `daily_config.json` `date` must match the day in Mongo. For Kite, save `request_token` in Web **Kite login**; on startup the bot tries the API before cache/env.
5. Edit `config/daily_config.json` and `config/candle_patterns.json`.
6. `python main.py`

## Safety defaults

- `DRY_RUN=true` by default (no live order placement).
- Orders are MARKET + MIS and options BUY-only flow is enforced by strategy signal mapping.
- EOD squareoff time is configurable via `.env`.
