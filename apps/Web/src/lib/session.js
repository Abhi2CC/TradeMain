const STORAGE_KEY = "squareoff_algoryx_dashboard_jwt";

/**
 * @returns {string | null}
 */
export function getSessionToken() {
  try {
    return sessionStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

/**
 * @param {string} token
 */
export function setSessionToken(token) {
  sessionStorage.setItem(STORAGE_KEY, token);
}

export function clearSessionToken() {
  sessionStorage.removeItem(STORAGE_KEY);
}
