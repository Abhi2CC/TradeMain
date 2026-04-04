import "dotenv/config";
import express from "express";
import cors from "cors";
import mongoose from "mongoose";
import { optionalApiKey } from "./middleware/auth.js";
import { levelsRouter } from "./routes/levels.js";

const PORT = Number(process.env.PORT) || 3001;
const MONGODB_URI = process.env.MONGODB_URI || "mongodb://127.0.0.1:27017/tradeking";

const app = express();
app.use(
  cors({
    origin: true,
    credentials: true,
    allowedHeaders: ["Content-Type", "X-API-Key"],
  })
);
app.use(express.json({ limit: "2mb" }));

app.get("/health", (_req, res) => {
  res.json({ ok: true, mongo: mongoose.connection.readyState === 1 });
});

app.use("/api/v1/levels", optionalApiKey, levelsRouter);

async function main() {
  await mongoose.connect(MONGODB_URI);
  console.log("MongoDB connected");
  app.listen(PORT, () => {
    console.log(`Levels API http://localhost:${PORT}`);
    console.log("  GET    /api/v1/levels/:date");
    console.log("  POST   /api/v1/levels");
    console.log("  PATCH  /api/v1/levels/:date");
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
