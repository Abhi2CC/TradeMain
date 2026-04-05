# TradeKing Levels API

Node.js REST API backed by MongoDB for daily trading levels.

## Setup

```bash
cd apps/Api
copy .env.example .env
# Set MONGODB_URI, KITE_API_KEY (for Kite login URL), optional API_KEY (bot), and optional dashboard auth
npm install
npm run dev
```

## Endpoints

- `GET /health` — liveness (no API key)
- `GET /api/v1/levels/:date` — `{ date, levels }` for `YYYY-MM-DD`
- `POST /api/v1/levels` — body `{ date, levels }` — upsert
- `PATCH /api/v1/levels/:date` — body `{ levels }` — update existing day

**Auth**

- If only `API_KEY` is set: send `X-API-Key` on `/api/v1/levels` and `/api/v1/kite` (trading bot, scripts).
- If `DASHBOARD_USER_ID` + `DASHBOARD_PASSWORD` + `WEB_SESSION_SECRET` (min 16 chars) are set: the Web app logs in via `POST /api/v1/auth/login` and sends `Authorization: Bearer <jwt>`. You can set **both** `API_KEY` and dashboard env vars so the bot keeps using `X-API-Key` while humans use JWT.
- If neither is set, those routes are open (dev only).

- `GET /api/v1/auth/status` — `{ authRequired: boolean }` (no auth)
- `POST /api/v1/auth/login` — body `{ userId, password }` — `{ token, tokenType, expiresInSeconds }`
- `GET /api/v1/auth/me` — validates Bearer token

### Kite (manual request token)

- `GET /api/v1/kite/login-url` — `{ loginUrl }` (matches `KiteConnect.login_url()`; requires `KITE_API_KEY`)
- `GET /api/v1/kite/request-token` — latest `{ requestToken, updatedAt }` or 404
- `POST /api/v1/kite/request-token` — body `{ requestToken }` — upsert in MongoDB
- `PUT /api/v1/kite/request-token` — same as POST (update)
