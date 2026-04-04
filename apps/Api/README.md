# TradeKing Levels API

Node.js REST API backed by MongoDB for daily trading levels.

## Setup

```bash
cd apps/Api
copy .env.example .env
# Set MONGODB_URI (and optional API_KEY)
npm install
npm run dev
```

## Endpoints

- `GET /health` — liveness (no API key)
- `GET /api/v1/levels/:date` — `{ date, levels }` for `YYYY-MM-DD`
- `POST /api/v1/levels` — body `{ date, levels }` — upsert
- `PATCH /api/v1/levels/:date` — body `{ levels }` — update existing day

If `API_KEY` is set in `.env`, send header `X-API-Key: <same value>` on `/api/*` routes.
