import { useCallback, useEffect, useState } from "react";
import Dashboard from "./components/Dashboard.jsx";
import LoginPage from "./components/LoginPage.jsx";
import { clearSessionToken, getSessionToken, setSessionToken } from "./lib/session.js";

/** Empty base = same-origin (e.g. Docker nginx proxy). "same" / "." also mean relative. */
function resolveApiBase() {
  const v = import.meta.env.VITE_API_URL;
  if (v === undefined || v === null) return "http://localhost:3001";
  const s = String(v).trim().replace(/\/$/, "");
  if (s === "" || s === "same" || s === ".") return "";
  return s;
}

const API_BASE = resolveApiBase();
const API_KEY = import.meta.env.VITE_API_KEY || "";

/** Default true: show id/password login first unless VITE_REQUIRE_LOGIN=false (or 0). */
const REQUIRE_LOGIN_DEFAULT =
  String(import.meta.env.VITE_REQUIRE_LOGIN ?? "true").toLowerCase() !== "false" &&
  import.meta.env.VITE_REQUIRE_LOGIN !== "0";

export default function App() {
  const [ready, setReady] = useState(false);
  const [authRequired, setAuthRequired] = useState(false);
  const [sessionToken, setSessionTokenState] = useState(() => getSessionToken());

  const refreshAuthStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/status`);
      const data = await res.json().catch(() => ({}));
      const serverRequires = Boolean(data.authRequired);
      setAuthRequired(REQUIRE_LOGIN_DEFAULT || serverRequires);
    } catch {
      setAuthRequired(REQUIRE_LOGIN_DEFAULT);
    } finally {
      setReady(true);
    }
  }, []);

  useEffect(() => {
    refreshAuthStatus();
  }, [refreshAuthStatus]);

  useEffect(() => {
    if (!ready || !authRequired || !sessionToken) return;
    (async () => {
      const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (res.status === 401) {
        clearSessionToken();
        setSessionTokenState(null);
      }
    })();
  }, [ready, authRequired, sessionToken]);

  const handleLoggedIn = (token) => {
    setSessionToken(token);
    setSessionTokenState(token);
  };

  const handleLogout = () => {
    clearSessionToken();
    setSessionTokenState(null);
  };

  if (!ready) {
    return (
      <div className="app-loading">
        <div className="brand-block brand-block--compact">
          <span className="brand-squareoff">SQUARE OFF</span>
          <span className="brand-divider">|</span>
          <span className="brand-algoryx">ALGORYX.IO</span>
        </div>
        <p className="meta">Loading…</p>
      </div>
    );
  }

  if (authRequired && !sessionToken) {
    return <LoginPage apiBase={API_BASE} onLoggedIn={handleLoggedIn} />;
  }

  return (
    <Dashboard
      apiBase={API_BASE}
      sessionToken={authRequired ? sessionToken : null}
      apiKey={API_KEY}
      showLogout={authRequired}
      onLogout={handleLogout}
    />
  );
}
