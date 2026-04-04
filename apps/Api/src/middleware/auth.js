/**
 * If API_KEY is set in env, require matching X-API-Key header.
 */
export function optionalApiKey(req, res, next) {
  const expected = process.env.API_KEY?.trim();
  if (!expected) {
    return next();
  }
  const provided = req.get("X-API-Key") || req.get("x-api-key") || "";
  if (provided !== expected) {
    return res.status(401).json({ error: "Unauthorized", message: "Invalid or missing X-API-Key" });
  }
  next();
}
