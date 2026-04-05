import { useState } from "react";

/**
 * @param {{ apiBase: string, onLoggedIn: (token: string) => void }} props
 */
export default function LoginPage({ apiBase, onLoggedIn }) {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: userId.trim(), password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.message || data.error || "Sign-in failed");
        return;
      }
      if (!data.token) {
        setError("Invalid response from server");
        return;
      }
      onLoggedIn(data.token);
    } catch (err) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-shell">
      <div className="login-glow" aria-hidden />
      <div className="login-card">
        <div className="brand-block brand-block--hero">
          <span className="brand-squareoff">SQUARE OFF</span>
          <span className="brand-divider" aria-hidden>
            |
          </span>
          <span className="brand-algoryx">ALGORYX.IO</span>
        </div>
        <p className="login-tagline">Control center · levels &amp; Kite session</p>

        <form className="login-form" onSubmit={submit}>
          {error ? <div className="msg msg--error">{error}</div> : null}
          <label className="field-label">
            User ID
            <input
              className="field-input"
              type="text"
              autoComplete="username"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Dashboard user ID"
              required
            />
          </label>
          <label className="field-label">
            Password
            <input
              className="field-input"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </label>
          <button type="submit" className="btn btn--primary btn--full" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
      <footer className="login-footer">
        <span className="brand-legal">SQUARE OFF | ALGORYX.IO</span>
      </footer>
    </div>
  );
}
