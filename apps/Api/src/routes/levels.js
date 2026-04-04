import { Router } from "express";
import { LevelDay } from "../models/LevelDay.js";

export const levelsRouter = Router();

/**
 * GET /api/v1/levels/:date
 * Returns { date, levels } for YYYY-MM-DD
 */
levelsRouter.get("/:date", async (req, res) => {
  const { date } = req.params;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return res.status(400).json({ error: "Invalid date format. Use YYYY-MM-DD." });
  }
  try {
    const doc = await LevelDay.findOne({ date }).lean();
    if (!doc) {
      return res.status(404).json({ error: "Not found", message: `No levels for ${date}` });
    }
    return res.json({ date: doc.date, levels: doc.levels || [] });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Server error", message: err.message });
  }
});

/**
 * POST /api/v1/levels
 * Body: { date: "YYYY-MM-DD", levels: [...] }
 * Upsert: creates or replaces levels for that date.
 */
levelsRouter.post("/", async (req, res) => {
  const { date, levels } = req.body || {};
  if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return res.status(400).json({ error: "Body must include date (YYYY-MM-DD)" });
  }
  if (!Array.isArray(levels)) {
    return res.status(400).json({ error: "Body must include levels (array)" });
  }
  try {
    const doc = await LevelDay.findOneAndUpdate(
      { date },
      { $set: { levels } },
      { new: true, upsert: true, runValidators: true }
    ).lean();
    return res.status(201).json({ date: doc.date, levels: doc.levels, message: "Saved" });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Server error", message: err.message });
  }
});

/**
 * PATCH /api/v1/levels/:date
 * Body: { levels: [...] } — replaces the levels array for that date (document must exist).
 */
levelsRouter.patch("/:date", async (req, res) => {
  const { date } = req.params;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return res.status(400).json({ error: "Invalid date format. Use YYYY-MM-DD." });
  }
  const { levels } = req.body || {};
  if (!Array.isArray(levels)) {
    return res.status(400).json({ error: "Body must include levels (array)" });
  }
  try {
    const doc = await LevelDay.findOneAndUpdate(
      { date },
      { $set: { levels } },
      { new: true, runValidators: true }
    ).lean();
    if (!doc) {
      return res.status(404).json({ error: "Not found", message: `No document for ${date}. Use POST to create.` });
    }
    return res.json({ date: doc.date, levels: doc.levels, message: "Updated" });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Server error", message: err.message });
  }
});
