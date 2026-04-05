# Index Options Scalping Bot

Production-oriented modular bot scaffold for Zerodha Kite Connect intraday index options scalping in `apps/trading`.

## Quick start

1. `pip install -r requirements.txt`
2. `copy .env.example .env` and fill credentials
3. Run [apps/Api](../Api) (MongoDB + `LEVELS_API_URL` in `.env`). Edit levels in [apps/Web](../Web) or via API.
4. Set `LEVELS_API_URL` (and optional `LEVELS_API_KEY`) in `.env`. `daily_config.json` `date` must match the day stored in Mongo. For a new Kite day/session, save a `request_token` in the Web **Kite login** tab. On startup the bot calls `GET /api/v1/kite/request-token` **before** using `token_cache.json` / env, so a fresh Web token wins; if exchange fails (already used), it falls back to today’s cached access token.
5. Edit `config/daily_config.json` and `config/candle_patterns.json`. Optional fallback: `levels/YYYY-MM-DD.json` if API is down.
6. `python main.py`

## Safety defaults

- `DRY_RUN=true` by default (no live order placement).
- Orders are MARKET + MIS and options BUY-only flow is enforced by strategy signal mapping.
- EOD squareoff time is configurable via `.env`.
