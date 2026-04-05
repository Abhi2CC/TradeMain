# TASK Tracker

## Open Tasks

- [x] 2026-04-05: Production Dockerfiles + root `docker-compose.yml` for Api, Web, trading, MongoDB (`env.docker.example`).
- [x] 2026-04-01: Build production-grade index options scalping bot in `apps/trading` using Kite Connect.

## Discovered During Work

- [x] Wire full live event loop in `core/engine.py` with `KiteTicker` callbacks and CLI command loop.
- [ ] Add persistence for daily summaries in DB tables.
- [x] Levels API (Node + Mongo) in `apps/Api`, React UI in `apps/Web`; bot uses `TRADEKING_API_URL` only for `/levels` + `/kite/request-token` (no API key; no local `levels/*.json` fallback).
- [x] Add persistence for missed trades in DB tables.
- [x] Wire `apps/trading` bot to use `GET /api/v1/kite/request-token` for session bootstrap when cache/env token is missing or stale.

## Completed (session)

- [x] 2026-04-05: Kite login URL + request token APIs (`KiteAuthState` Mongo model) and **Kite login** tab in `apps/Web`.
- [x] 2026-04-05: Dashboard JWT auth (`POST /api/v1/auth/login`) + dark **SQUARE OFF | ALGORYX.IO** UI in `apps/Web`.
