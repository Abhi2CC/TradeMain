import mongoose from "mongoose";

const levelDaySchema = new mongoose.Schema(
  {
    date: { type: String, required: true, unique: true, index: true },
    levels: { type: [mongoose.Schema.Types.Mixed], default: [] },
  },
  { timestamps: true }
);

export const LevelDay = mongoose.model("LevelDay", levelDaySchema);
