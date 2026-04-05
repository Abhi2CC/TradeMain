import crypto from "crypto";
import * as jose from "jose";

/**
 * Constant-time string compare for credentials.
 *
 * Args:
 *   a (string): First value.
 *   b (string): Second value.
 *
 * Returns:
 *   bool: True if equal.
 */
export function timingSafeEqualString(a, b) {
  const ba = Buffer.from(String(a), "utf8");
  const bb = Buffer.from(String(b), "utf8");
  if (ba.length !== bb.length) {
    return false;
  }
  return crypto.timingSafeEqual(ba, bb);
}

/**
 * Verify a dashboard JWT from the Authorization header value (Bearer token only).
 *
 * Args:
 *   token (string): Raw JWT string.
 *
 * Returns:
 *   object | null: JWT payload if valid, else null.
 */
export async function verifyDashboardJwt(token) {
  const secret = process.env.WEB_SESSION_SECRET?.trim();
  if (!secret || !token) {
    return null;
  }
  try {
    const { payload } = await jose.jwtVerify(token, new TextEncoder().encode(secret));
    if (payload.sub === "dashboard") {
      return payload;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Mint a short-lived dashboard session JWT.
 *
 * Returns:
 *   str: Signed JWT.
 *
 * Raises:
 *   Error: If WEB_SESSION_SECRET is missing.
 */
export async function signDashboardJwt() {
  const secret = process.env.WEB_SESSION_SECRET?.trim();
  if (!secret) {
    throw new Error("WEB_SESSION_SECRET is not set");
  }
  return new jose.SignJWT({ sub: "dashboard" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("12h")
    .sign(new TextEncoder().encode(secret));
}

/**
 * Optional middleware: X-API-Key (API_KEY) or Bearer dashboard JWT.
 * Not mounted on `/levels` or `/kite` in server.js (bot uses base URL only).
 */
export async function protectApiRoutes(req, res, next) {
  try {
    const apiKey = process.env.API_KEY?.trim();
    const dashUser = process.env.DASHBOARD_USER_ID?.trim();

    if (!apiKey && !dashUser) {
      return next();
    }

    const providedKey = req.get("X-API-Key") || req.get("x-api-key") || "";
    if (apiKey && providedKey === apiKey) {
      return next();
    }

    if (dashUser) {
      const authHeader = req.get("Authorization") || "";
      const m = authHeader.match(/^Bearer\s+(.+)$/i);
      if (m) {
        const payload = await verifyDashboardJwt(m[1].trim());
        if (payload) {
          return next();
        }
      }
    }

    const message =
      apiKey && dashUser
        ? "Invalid or missing credentials (X-API-Key or Bearer session)"
        : apiKey
          ? "Invalid or missing X-API-Key"
          : "Invalid or missing session (login required)";
    return res.status(401).json({ error: "Unauthorized", message });
  } catch (err) {
    return next(err);
  }
}
