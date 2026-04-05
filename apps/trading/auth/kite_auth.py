from datetime import date
import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from kiteconnect import KiteConnect
from config.settings import TOKEN_CACHE_FILE, settings

logger = logging.getLogger(__name__)

API_TIMEOUT_SEC = 30


def fetch_kite_request_token(api_base_url: str, api_key: str | None = None) -> str:
    """
    Load the latest Kite ``request_token`` saved via TradeKing API (Mongo).

    Args:
        api_base_url (str): Base URL of the Levels API (e.g. ``http://localhost:3001``).
        api_key (str | None): Optional ``X-API-Key`` if the API enforces ``API_KEY``.

    Returns:
        str: Non-empty request token.

    Raises:
        RuntimeError: If the URL is invalid, the API returns an error, or the token is missing.
    """
    base = api_base_url.strip().rstrip("/")
    if not base:
        raise RuntimeError("LEVELS_API_URL is empty; cannot fetch Kite request_token from API.")
    url = f"{base}/api/v1/kite/request-token"
    headers: dict[str, str] = {}
    key = (api_key or "").strip()
    if key:
        headers["X-API-Key"] = key
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=API_TIMEOUT_SEC) as resp:
            body = resp.read().decode("utf-8")
    except HTTPError as e:
        if e.code == 404:
            raise RuntimeError(
                "No Kite request_token in API (404). Save one from apps/Web (Kite login tab) first."
            ) from e
        raise RuntimeError(f"Kite token API HTTP {e.code}: {e.reason}") from e
    except URLError as e:
        raise RuntimeError(f"Kite token API unreachable: {e.reason}") from e
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise RuntimeError("Kite token API returned invalid JSON.") from e
    token = (data.get("requestToken") or "").strip()
    if not token:
        raise RuntimeError("Kite token API response missing requestToken.")
    return token


def try_fetch_kite_request_token(api_base_url: str, api_key: str | None = None) -> str | None:
    """
    Same as ``fetch_kite_request_token`` but returns ``None`` on any failure (logs, no raise).

    Args:
        api_base_url (str): Base URL of the Levels API.
        api_key (str | None): Optional ``X-API-Key``.

    Returns:
        str | None: Token string, or ``None`` if missing or unreachable.
    """
    if not (api_base_url or "").strip():
        return None
    try:
        return fetch_kite_request_token(api_base_url, api_key)
    except RuntimeError as exc:
        logger.info("Kite request_token not loaded from API: %s", exc)
        return None


class KiteAuth:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)

    def get_login_url(self) -> str:
        return self.kite.login_url()

    def generate_session(self, request_token: str) -> None:
        session = self.kite.generate_session(request_token, api_secret=self.api_secret)
        self.kite.set_access_token(session['access_token'])
        os.environ['KITE_ACCESS_TOKEN'] = session['access_token']
        os.environ['KITE_ACCESS_DATE'] = str(date.today())
        TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_CACHE_FILE.write_text(
            json.dumps({"access_token": session["access_token"], "access_date": str(date.today())}),
            encoding="utf-8",
        )

    def validate_session(self) -> bool:
        try:
            self.kite.profile()
            return True
        except Exception as exc:
            logger.warning('Session validation failed: %s', exc)
            return False

    def bootstrap(self) -> KiteConnect:
        # 1) Prefer a request_token from the TradeKing API (Web Kite tab) before file/env cache.
        request_token = try_fetch_kite_request_token(
            settings.levels_api_url,
            settings.levels_api_key or None,
        )
        if request_token:
            try:
                self.generate_session(request_token)
                if self.validate_session():
                    logger.info(
                        "Kite session established via GET %s/api/v1/kite/request-token",
                        settings.levels_api_url.strip().rstrip("/") or "(api)",
                    )
                    return self.kite
            except Exception as exc:
                logger.warning(
                    "Exchanging API request_token failed (stale or already used); trying cached access token: %s",
                    exc,
                )

        token = settings.kite_access_token
        token_date = settings.kite_access_date
        if TOKEN_CACHE_FILE.exists():
            try:
                cached = json.loads(TOKEN_CACHE_FILE.read_text(encoding="utf-8"))
                token = token or cached.get("access_token", "")
                token_date = token_date or cached.get("access_date", "")
            except json.JSONDecodeError:
                logger.warning("Ignoring malformed token cache")

        if token and token_date == str(date.today()):
            self.kite.set_access_token(token)
            if self.validate_session():
                logger.info("Kite session from cached access token for today")
                return self.kite

        login_url = self.get_login_url()
        logger.error("No valid Kite session. Save request_token via Web (Kite login). Login URL: %s", login_url)
        print(f"Login URL: {login_url}")
        raise RuntimeError(
            "No valid Kite session. Save a fresh request_token in apps/Web (Kite login), "
            "ensure the API returns it at GET /api/v1/kite/request-token, set LEVELS_API_URL, then restart."
        )
