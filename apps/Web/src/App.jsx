import { useCallback, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL?.replace(/\/$/, "") || "http://localhost:3001";
const API_KEY = import.meta.env.VITE_API_KEY || "";

const emptyLevel = () => ({
  index: "NIFTY",
  timeframe: "5m",
  price: "",
  type: "ED",
  action: "SELL",
  target_type: "TFU",
  target_price: "",
  stoploss: "",
  notes: "",
});

function headersJson() {
  const h = { "Content-Type": "application/json" };
  if (API_KEY) h["X-API-Key"] = API_KEY;
  return h;
}

function headersGet() {
  const h = {};
  if (API_KEY) h["X-API-Key"] = API_KEY;
  return h;
}

export default function App() {
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [levels, setLevels] = useState([emptyLevel()]);
  const [message, setMessage] = useState(null);

  const showError = (text) => setMessage({ type: "error", text });
  const showOk = (text) => setMessage({ type: "ok", text });

  const loadLevels = useCallback(async () => {
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/levels/${date}`, { headers: headersGet() });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        showError(data.message || data.error || res.statusText);
        return;
      }
      const list = data.levels?.length ? data.levels : [emptyLevel()];
      setLevels(
        list.map((l) => ({
          index: l.index ?? "NIFTY",
          timeframe: l.timeframe ?? "5m",
          price: l.price ?? "",
          type: l.type ?? "",
          action: l.action ?? "SELL",
          target_type: l.target_type ?? "TFU",
          target_price: l.target_price ?? "",
          stoploss: l.stoploss ?? "",
          notes: l.notes ?? "",
        }))
      );
      showOk(`Loaded ${data.levels?.length ?? 0} levels for ${date}`);
    } catch (e) {
      showError(e.message || "Network error");
    }
  }, [date]);

  const normalizeLevels = () =>
    levels.map((l) => ({
      index: String(l.index).toUpperCase(),
      timeframe: l.timeframe,
      price: Number(l.price),
      type: l.type,
      action: String(l.action).toUpperCase(),
      target_type: l.target_type || undefined,
      target_price: Number(l.target_price),
      stoploss: Number(l.stoploss),
      notes: l.notes || undefined,
    }));

  const savePost = async () => {
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/levels`, {
        method: "POST",
        headers: headersJson(),
        body: JSON.stringify({ date, levels: normalizeLevels() }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        showError(data.message || data.error || res.statusText);
        return;
      }
      showOk(data.message || "Saved (POST upsert)");
    } catch (e) {
      showError(e.message || "Network error");
    }
  };

  const savePatch = async () => {
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/levels/${date}`, {
        method: "PATCH",
        headers: headersJson(),
        body: JSON.stringify({ levels: normalizeLevels() }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        showError(data.message || data.error || res.statusText);
        return;
      }
      showOk(data.message || "Updated (PATCH)");
    } catch (e) {
      showError(e.message || "Network error");
    }
  };

  const addRow = () => setLevels((prev) => [...prev, emptyLevel()]);
  const removeRow = (i) => setLevels((prev) => prev.filter((_, j) => j !== i));

  const updateRow = (i, field, value) => {
    setLevels((prev) => prev.map((row, j) => (j === i ? { ...row, [field]: value } : row)));
  };

  return (
    <div className="card">
      <h1>TradeKing — Daily levels</h1>
      <p style={{ color: "#64748b", marginTop: 0 }}>
        API: <code>{API_BASE}</code>
      </p>

      {message && (
        <div className={`msg ${message.type === "error" ? "error" : "ok"}`}>{message.text}</div>
      )}

      <div className="row">
        <label>
          Date (YYYY-MM-DD)
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
        <button type="button" onClick={loadLevels}>
          Load (GET)
        </button>
        <button type="button" onClick={savePost}>
          Save upsert (POST)
        </button>
        <button type="button" className="secondary" onClick={savePatch}>
          Update (PATCH)
        </button>
        <button type="button" className="secondary" onClick={addRow}>
          Add row
        </button>
      </div>

      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Index</th>
            <th>TF</th>
            <th>Price</th>
            <th>Type</th>
            <th>Action</th>
            <th>Target</th>
            <th>SL</th>
            <th>Notes</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {levels.map((row, i) => (
            <tr key={i}>
              <td>{i + 1}</td>
              <td>
                <select value={row.index} onChange={(e) => updateRow(i, "index", e.target.value)}>
                  <option>NIFTY</option>
                  <option>BANKNIFTY</option>
                  <option>FINNIFTY</option>
                </select>
              </td>
              <td>
                <select value={row.timeframe} onChange={(e) => updateRow(i, "timeframe", e.target.value)}>
                  <option>1m</option>
                  <option>5m</option>
                  <option>15m</option>
                </select>
              </td>
              <td>
                <input
                  style={{ width: "90px" }}
                  value={row.price}
                  onChange={(e) => updateRow(i, "price", e.target.value)}
                />
              </td>
              <td>
                <input
                  style={{ width: "100px" }}
                  value={row.type}
                  onChange={(e) => updateRow(i, "type", e.target.value)}
                />
              </td>
              <td>
                <select value={row.action} onChange={(e) => updateRow(i, "action", e.target.value)}>
                  <option>BUY</option>
                  <option>SELL</option>
                </select>
              </td>
              <td>
                <input
                  style={{ width: "90px" }}
                  value={row.target_price}
                  onChange={(e) => updateRow(i, "target_price", e.target.value)}
                />
              </td>
              <td>
                <input
                  style={{ width: "90px" }}
                  value={row.stoploss}
                  onChange={(e) => updateRow(i, "stoploss", e.target.value)}
                />
              </td>
              <td>
                <input
                  style={{ width: "140px" }}
                  value={row.notes}
                  onChange={(e) => updateRow(i, "notes", e.target.value)}
                />
              </td>
              <td>
                <button type="button" className="danger" onClick={() => removeRow(i)}>
                  ×
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
