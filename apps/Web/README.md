# SQUARE OFF | ALGORYX.IO — Dashboard

Dark dashboard for daily levels and Kite request tokens via the TradeKing API.

## Setup

```bash
cd apps/Web
copy .env.example .env
# VITE_API_URL=http://localhost:3001
npm install
npm run dev
```

By default (`VITE_REQUIRE_LOGIN` omitted or `true`), the **login page appears first**. Configure the API with `DASHBOARD_USER_ID`, `DASHBOARD_PASSWORD`, and `WEB_SESSION_SECRET` (min 16 chars) so `POST /api/v1/auth/login` succeeds.

For local dev without dashboard auth, set `VITE_REQUIRE_LOGIN=false` in `.env` and use `VITE_API_KEY` if the API uses `API_KEY` only.

Open http://localhost:5173 — **Daily levels** and **Kite login** after sign-in.
