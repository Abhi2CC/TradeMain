import { useCallback, useState } from "react";

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

/**
 * @param {{
 *   apiBase: string,
 *   sessionToken: string | null,
 *   apiKey: string,
 *   showLogout: boolean,
 *   onLogout: () => void,
 * }} props
 */
export default function Dashboard({ apiBase, sessionToken, apiKey, showLogout, onLogout }) {
  const [tab, setTab] = useState("levels");
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [levels, setLevels] = useState([emptyLevel()]);
  const [message, setMessage] = useState(null);
  const [kiteLoginUrl, setKiteLoginUrl] = useState("");
  const [kiteRequestToken, setKiteRequestToken] = useState("");
  const [kiteUpdatedAt, setKiteUpdatedAt] = useState(null);

  const headersJson = useCallback(() => {
    const h = { "Content-Type": "application/json" };
    if (sessionToken) h.Authorization = `Bearer ${sessionToken}`;
    else if (apiKey) h["X-API-Key"] = apiKey;
    return h;
  }, [sessionToken, apiKey]);

  const headersGet = useCallback(() => {
    const h = {};
    if (sessionToken) h.Authorization = `Bearer ${sessionToken}`;
    else if (apiKey) h["X-API-Key"] = apiKey;
    return h;
  }, [sessionToken, apiKey]);

  const showError = (text) => setMessage({ type: "error", text });
  const showOk = (text) => setMessage({ type: "ok", text });

  const loadLevels = useCallback(async () => {
    setMessage(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/levels/${date}`, { headers: headersGet() });
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
  }, [apiBase, date, headersGet]);

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
      const res = await fetch(`${apiBase}/api/v1/levels`, {
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
      const res = await fetch(`${apiBase}/api/v1/levels/${date}`, {
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

  const fetchKiteLoginUrl = async () => {
    setMessage(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/kite/login-url`, { headers: headersGet() });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        showError(data.message || data.error || res.statusText);
        setKiteLoginUrl("");
        return;
      }
      setKiteLoginUrl(data.loginUrl || "");
      showOk("Login URL loaded — complete Zerodha login, then paste request_token.");
    } catch (e) {
      showError(e.message || "Network error");
    }
  };

  const saveKiteRequestToken = async () => {
    setMessage(null);
    const token = kiteRequestToken.trim();
    if (!token) {
      showError("Enter the request_token first.");
      return;
    }
    try {
      const res = await fetch(`${apiBase}/api/v1/kite/request-token`, {
        method: "POST",
        headers: headersJson(),
        body: JSON.stringify({ requestToken: token }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        showError(data.message || data.error || res.statusText);
        return;
      }
      setKiteUpdatedAt(data.updatedAt || null);
      showOk(data.message || "Request token saved.");
    } catch (e) {
      showError(e.message || "Network error");
    }
  };

  const loadSavedKiteToken = async () => {
    setMessage(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/kite/request-token`, { headers: headersGet() });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        showError(data.message || data.error || res.statusText);
        setKiteRequestToken("");
        setKiteUpdatedAt(null);
        return;
      }
      setKiteRequestToken(data.requestToken || "");
      setKiteUpdatedAt(data.updatedAt || null);
      showOk("Loaded latest saved request token.");
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
    <div className="app-frame">
      <header className="top-bar">
        <div className="brand-block brand-block--compact">
          <span className="brand-squareoff">SQUARE OFF</span>
          <span className="brand-divider">|</span>
          <span className="brand-algoryx">ALGORYX.IO</span>
        </div>
        <div className="top-bar__actions">
          <span className="api-pill" title="API base URL">
            {apiBase.replace(/^https?:\/\//, "")}
          </span>
          {showLogout ? (
            <button type="button" className="btn btn--ghost" onClick={onLogout}>
              Sign out
            </button>
          ) : null}
        </div>
      </header>

      <main className="main-card">
        <div className="tabs">
          <button type="button" className={tab === "levels" ? "tab tab--active" : "tab"} onClick={() => setTab("levels")}>
            Daily levels
          </button>
          <button type="button" className={tab === "kite" ? "tab tab--active" : "tab"} onClick={() => setTab("kite")}>
            Kite login
          </button>
        </div>

        {message ? (
          <div className={`msg ${message.type === "error" ? "msg--error" : "msg--ok"}`}>{message.text}</div>
        ) : null}

        {tab === "levels" ? (
          <section className="section">
            <h2 className="section-title">Daily levels</h2>
            <div className="toolbar">
              <label className="field-label field-label--inline">
                Date
                <input className="field-input field-input--narrow" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
              </label>
              <button type="button" className="btn btn--primary" onClick={loadLevels}>
                Load
              </button>
              <button type="button" className="btn btn--primary" onClick={savePost}>
                Save (upsert)
              </button>
              <button type="button" className="btn btn--secondary" onClick={savePatch}>
                Update
              </button>
              <button type="button" className="btn btn--secondary" onClick={addRow}>
                Add row
              </button>
            </div>
            <div className="table-wrap">
              <table className="data-table">
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
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {levels.map((row, i) => (
                    <tr key={i}>
                      <td>{i + 1}</td>
                      <td>
                        <select className="field-select" value={row.index} onChange={(e) => updateRow(i, "index", e.target.value)}>
                          <option>NIFTY</option>
                          <option>BANKNIFTY</option>
                          <option>FINNIFTY</option>
                        </select>
                      </td>
                      <td>
                        <select className="field-select" value={row.timeframe} onChange={(e) => updateRow(i, "timeframe", e.target.value)}>
                          <option>1m</option>
                          <option>5m</option>
                          <option>15m</option>
                        </select>
                      </td>
                      <td>
                        <input className="field-input field-input--table" value={row.price} onChange={(e) => updateRow(i, "price", e.target.value)} />
                      </td>
                      <td>
                        <input className="field-input field-input--table" value={row.type} onChange={(e) => updateRow(i, "type", e.target.value)} />
                      </td>
                      <td>
                        <select className="field-select" value={row.action} onChange={(e) => updateRow(i, "action", e.target.value)}>
                          <option>BUY</option>
                          <option>SELL</option>
                        </select>
                      </td>
                      <td>
                        <input
                          className="field-input field-input--table"
                          value={row.target_price}
                          onChange={(e) => updateRow(i, "target_price", e.target.value)}
                        />
                      </td>
                      <td>
                        <input className="field-input field-input--table" value={row.stoploss} onChange={(e) => updateRow(i, "stoploss", e.target.value)} />
                      </td>
                      <td>
                        <input className="field-input field-input--table" value={row.notes} onChange={(e) => updateRow(i, "notes", e.target.value)} />
                      </td>
                      <td>
                        <button type="button" className="btn btn--danger btn--icon" onClick={() => removeRow(i)} aria-label="Remove row">
                          ×
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {tab === "kite" ? (
          <section className="section">
            <h2 className="section-title">Kite Connect</h2>
            <p className="prose">
              Open the login URL, complete Zerodha auth, then paste the <code>request_token</code> from the redirect. It is stored for the trading
              bot.
            </p>
            <div className="toolbar">
              <button type="button" className="btn btn--primary" onClick={fetchKiteLoginUrl}>
                Get login URL
              </button>
              <button type="button" className="btn btn--secondary" onClick={loadSavedKiteToken}>
                Load saved token
              </button>
            </div>
            {kiteLoginUrl ? (
              <p className="kite-link">
                <a href={kiteLoginUrl} target="_blank" rel="noopener noreferrer">
                  {kiteLoginUrl}
                </a>
              </p>
            ) : null}
            <label className="field-label" htmlFor="kite-req-token">
              Request token
            </label>
            <input
              id="kite-req-token"
              className="field-input"
              type="text"
              autoComplete="off"
              placeholder="Paste request_token from redirect URL"
              value={kiteRequestToken}
              onChange={(e) => setKiteRequestToken(e.target.value)}
            />
            <div className="toolbar toolbar--mt">
              <button type="button" className="btn btn--primary" onClick={saveKiteRequestToken}>
                Save token
              </button>
            </div>
            {kiteUpdatedAt ? <p className="meta">Last saved: {new Date(kiteUpdatedAt).toLocaleString()}</p> : null}
          </section>
        ) : null}
      </main>
    </div>
  );
}
