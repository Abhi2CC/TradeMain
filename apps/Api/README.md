# TradeKing Levels API

Node.js REST API backed by MongoDB for daily trading levels and Kite request tokens.

## Setup

```bash
cd apps/Api
copy .env.example .env
# Set MONGODB_URI, KITE_API_KEY (for Kite login URL), optional dashboard auth for Web
npm install
npm run dev
```

## Endpoints

- `GET /health` — liveness
- `GET /api/v1/levels/:date` — `{ date, levels }` for `YYYY-MM-DD` (no API key)
- `POST /api/v1/levels` — body `{ date, levels }` — upsert
- `PATCH /api/v1/levels/:date` — body `{ levels }` — update existing day

**Dashboard auth (Web UI only)** — optional; does not gate `/levels` or `/kite`:

- `GET /api/v1/auth/status` — `{ authRequired: boolean }`
- `POST /api/v1/auth/login` — body `{ userId, password }` — `{ token, tokenType, expiresInSeconds }`
- `GET /api/v1/auth/me` — validates Bearer token

Set `DASHBOARD_USER_ID`, `DASHBOARD_PASSWORD`, and `WEB_SESSION_SECRET` (min 16 chars) if you want the React app to require login.

### Kite (manual request token)

- `GET /api/v1/kite/login-url` — `{ loginUrl }` (requires `KITE_API_KEY` on server)
- `GET /api/v1/kite/request-token` — latest `{ requestToken, updatedAt }` or 404
- `POST /api/v1/kite/request-token` — body `{ requestToken }` — upsert in MongoDB
- `PUT /api/v1/kite/request-token` — same as POST (update)

The trading bot uses **`TRADEKING_API_URL`** only: `GET .../api/v1/kite/request-token` and `GET .../api/v1/levels/{date}`.
