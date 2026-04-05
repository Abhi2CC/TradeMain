import { Router } from "express";
import { KiteAuthState } from "../models/KiteAuthState.js";

export const kiteRouter = Router();

const SINGLETON = "default";
const MAX_TOKEN_LEN = 512;

/**
 * GET /api/v1/kite/login-url
 * Same URL shape as KiteConnect.login_url() (api_key from server env).
 */
kiteRouter.get("/login-url", (_req, res) => {
  const apiKey = process.env.KITE_API_KEY?.trim();
  if (!apiKey) {
    return res.status(503).json({
      error: "Kite not configured",
      message: "Set KITE_API_KEY on the API server (same key as the trading app).",
    });
  }
  const loginUrl = `https://kite.zerodha.com/connect/login?v=3&api_key=${encodeURIComponent(apiKey)}`;
  return res.json({ loginUrl });
});

function parseRequestToken(body) {
  const raw = body?.requestToken ?? body?.request_token;
  return typeof raw === "string" ? raw.trim() : "";
}

async function upsertRequestToken(req, res) {
  const requestToken = parseRequestToken(req.body || {});
  if (!requestToken) {
    return res.status(400).json({
      error: "Invalid body",
      message: "Include requestToken (non-empty string).",
    });
  }
  if (requestToken.length > MAX_TOKEN_LEN) {
    return res.status(400).json({ error: "requestToken too long" });
  }
  try {
    const doc = await KiteAuthState.findOneAndUpdate(
      { singletonKey: SINGLETON },
      { $set: { requestToken }, $setOnInsert: { singletonKey: SINGLETON } },
      { new: true, upsert: true, runValidators: true }
    ).lean();
    const code = req.method === "POST" ? 201 : 200;
    return res.status(code).json({
      message: "Saved",
      updatedAt: doc.updatedAt,
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Server error", message: err.message });
  }
}

/**
 * POST /api/v1/kite/request-token
 * Body: { requestToken: string } — upserts the latest token.
 */
kiteRouter.post("/request-token", upsertRequestToken);

/**
 * PUT /api/v1/kite/request-token
 * Same as POST (upsert / update).
 */
kiteRouter.put("/request-token", upsertRequestToken);

/**
 * GET /api/v1/kite/request-token
 * Returns the latest saved request_token (if any).
 */
kiteRouter.get("/request-token", async (_req, res) => {
  try {
    const doc = await KiteAuthState.findOne({ singletonKey: SINGLETON }).lean();
    if (!doc?.requestToken) {
      return res.status(404).json({
        error: "Not found",
        message: "No request token saved yet. POST one from the Kite login page.",
      });
    }
    return res.json({
      requestToken: doc.requestToken,
      updatedAt: doc.updatedAt,
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Server error", message: err.message });
  }
});
