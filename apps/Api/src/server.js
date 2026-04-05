import "dotenv/config";
import express from "express";
import cors from "cors";
import mongoose from "mongoose";
import { authRouter } from "./routes/auth.js";
import { kiteRouter } from "./routes/kite.js";
import { levelsRouter } from "./routes/levels.js";

const PORT = Number(process.env.PORT) || 3001;
const MONGODB_URI = process.env.MONGODB_URI || "mongodb://127.0.0.1:27017/tradeking";

const app = express();
app.use(
  cors({
    origin: true,
    credentials: true,
    allowedHeaders: ["Content-Type", "X-API-Key", "Authorization"],
  })
);
app.use(express.json({ limit: "2mb" }));

app.get("/health", (_req, res) => {
  res.json({ ok: true, mongo: mongoose.connection.readyState === 1 });
});

app.use("/api/v1/auth", authRouter);
// Levels + Kite data routes: no API key (bot uses TRADEKING_API_URL only).
app.use("/api/v1/levels", levelsRouter);
app.use("/api/v1/kite", kiteRouter);

async function main() {
  await mongoose.connect(MONGODB_URI);
  console.log("MongoDB connected");
  app.listen(PORT, () => {
    console.log(`Levels API http://localhost:${PORT}`);
    console.log("  GET    /api/v1/auth/status");
    console.log("  POST   /api/v1/auth/login");
    console.log("  GET    /api/v1/auth/me");
    console.log("  GET    /api/v1/levels/:date");
    console.log("  POST   /api/v1/levels");
    console.log("  PATCH  /api/v1/levels/:date");
    console.log("  GET    /api/v1/kite/login-url");
    console.log("  GET    /api/v1/kite/request-token");
    console.log("  POST   /api/v1/kite/request-token");
    console.log("  PUT    /api/v1/kite/request-token");
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
