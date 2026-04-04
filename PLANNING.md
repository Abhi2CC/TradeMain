# Project Planning

## Architecture Goal

Build a modular intraday index options scalping bot under `apps/trading` using Zerodha Kite Connect.

Levels are stored in MongoDB and served by `apps/Api` (REST); edited via `apps/Web` (React). The bot loads levels with `GET /api/v1/levels/{date}` using `LEVELS_API_URL`.

## Design Constraints

- BUY options only (CE/PE), no option writing.
- MARKET + MIS orders only.
- Enforce risk controls: auto-lock, max daily loss, EOD squareoff.
- Event-driven flow: ticks -> candles -> signals -> risk -> execution -> analytics.
