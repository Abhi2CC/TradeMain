# Project Planning

## Architecture Goal

Build a modular intraday index options scalping bot under `apps/trading` using Zerodha Kite Connect.

Levels are stored in MongoDB and served by `apps/Api` (REST); edited via `apps/Web` (React). The bot uses `TRADEKING_API_URL` (or legacy `LEVELS_API_URL`) as the sole API base for `GET /api/v1/levels/{date}` and `GET /api/v1/kite/request-token` (no API key; no local JSON fallback).

## Design Constraints

- BUY options only (CE/PE), no option writing.
- MARKET + MIS orders only.
- Enforce risk controls: auto-lock, max daily loss, EOD squareoff.
- Event-driven flow: ticks -> candles -> signals -> risk -> execution -> analytics.
