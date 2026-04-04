# Project Planning

## Architecture Goal

Build a modular intraday index options scalping bot under `apps/trading/scalping_bot` using Zerodha Kite Connect.

## Design Constraints

- BUY options only (CE/PE), no option writing.
- MARKET + MIS orders only.
- Enforce risk controls: auto-lock, max daily loss, EOD squareoff.
- Event-driven flow: ticks -> candles -> signals -> risk -> execution -> analytics.
