import mongoose from "mongoose";

/**
 * Single-document store for the latest Kite Connect request_token (manual flow).
 * The trading bot can read this via GET /api/v1/kite/request-token.
 */
const kiteAuthStateSchema = new mongoose.Schema(
  {
    singletonKey: {
      type: String,
      required: true,
      unique: true,
      default: "default",
      enum: ["default"],
    },
    requestToken: { type: String, required: true, trim: true },
  },
  { timestamps: true }
);

export const KiteAuthState = mongoose.model("KiteAuthState", kiteAuthStateSchema);
