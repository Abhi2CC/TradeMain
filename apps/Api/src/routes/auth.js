import { Router } from "express";
import {
  signDashboardJwt,
  timingSafeEqualString,
  verifyDashboardJwt,
} from "../middleware/auth.js";

export const authRouter = Router();

const TWELVE_HOURS_SEC = 12 * 3600;

function dashboardAuthConfigured() {
  const user = process.env.DASHBOARD_USER_ID?.trim();
  const pass = process.env.DASHBOARD_PASSWORD;
  return Boolean(user && pass !== undefined && String(pass).length > 0);
}

/**
 * GET /api/v1/auth/status
 * Whether the SPA must log in before calling other /api/v1 routes.
 */
authRouter.get("/status", (_req, res) => {
  res.json({
    authRequired: dashboardAuthConfigured(),
  });
});

/**
 * POST /api/v1/auth/login
 * Body: { userId: string, password: string }
 */
authRouter.post("/login", async (req, res) => {
  if (!dashboardAuthConfigured()) {
    return res.status(503).json({
      error: "Auth not configured",
      message: "Set DASHBOARD_USER_ID and DASHBOARD_PASSWORD on the server.",
    });
  }
  const secret = process.env.WEB_SESSION_SECRET?.trim();
  if (!secret || secret.length < 16) {
    return res.status(503).json({
      error: "Server misconfigured",
      message: "WEB_SESSION_SECRET must be set (min 16 characters).",
    });
  }

  const expectedId = process.env.DASHBOARD_USER_ID.trim();
  const expectedPass = String(process.env.DASHBOARD_PASSWORD);

  const { userId, password } = req.body || {};
  const id = String(userId ?? "").trim();
  const pw = String(password ?? "");

  if (!timingSafeEqualString(id, expectedId) || !timingSafeEqualString(pw, expectedPass)) {
    return res.status(401).json({ error: "Unauthorized", message: "Invalid user ID or password" });
  }

  try {
    const token = await signDashboardJwt();
    return res.json({
      token,
      tokenType: "Bearer",
      expiresInSeconds: TWELVE_HOURS_SEC,
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Server error", message: err.message });
  }
});

/**
 * GET /api/v1/auth/me
 * Validates Bearer token (optional ping for the SPA).
 */
authRouter.get("/me", async (req, res) => {
  if (!dashboardAuthConfigured()) {
    return res.json({ ok: true, authRequired: false });
  }
  const authHeader = req.get("Authorization") || "";
  const m = authHeader.match(/^Bearer\s+(.+)$/i);
  if (!m) {
    return res.status(401).json({ error: "Unauthorized", message: "Missing Bearer token" });
  }
  const payload = await verifyDashboardJwt(m[1].trim());
  if (!payload) {
    return res.status(401).json({ error: "Unauthorized", message: "Invalid or expired session" });
  }
  return res.json({ ok: true, authRequired: true });
});
