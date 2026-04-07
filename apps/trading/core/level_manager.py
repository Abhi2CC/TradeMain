from collections import defaultdict
import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


def _http_error_message(exc: HTTPError) -> str:
    """Build a log message; include API JSON body when present."""
    base = f"HTTP {exc.code}: {exc.reason}"
    detail = ""
    try:
        if exc.fp is not None:
            raw = exc.fp.read().decode("utf-8", errors="replace").strip()
            if raw:
                try:
                    parsed = json.loads(raw)
                    msg = parsed.get("message") or parsed.get("error")
                    if msg:
                        detail = f" ({msg})"
                except json.JSONDecodeError:
                    detail = f" ({raw[:200]})"
    except Exception:
        pass
    return base + detail


class LevelManager:
    """Load levels from GET /api/v1/levels/{date} (Mongo via apps/Api). Never raises — logs on failure."""

    def __init__(
        self,
        *,
        date_str: str,
        api_base_url: str | None = None,
    ) -> None:
        self.date_str = date_str
        self.api_base_url = (api_base_url or "").strip().rstrip("/") or None
        self.levels: list[dict] = []
        self._indexed: dict[tuple[str, str], list[dict]] = defaultdict(list)

    def _fetch_from_api(self) -> dict:
        """GET /api/v1/levels/{date} and parse JSON.

        Returns:
            dict: Parsed response body (expects ``levels`` list).

        Raises:
            HTTPError: Non-success HTTP status.
            URLError: Network failure.
            json.JSONDecodeError: Invalid JSON body.
        """
        url = f"{self.api_base_url}/api/v1/levels/{self.date_str}"
        req = Request(url, method="GET")
        with urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
        return json.loads(body)

    def load(self) -> None:
        """Fetch levels from Mongo via API. On missing URL or any error: log and use 0 levels."""
        self.levels = []
        self._indexed.clear()
        data: dict = {"levels": []}

        if not self.api_base_url:
            logger.warning(
                "Levels: TRADEKING_API_URL / LEVELS_API_URL not set — using 0 levels."
            )
        else:
            try:
                data = self._fetch_from_api()
            except HTTPError as e:
                logger.warning(
                    "Levels GET failed for %s — using 0 levels. %s",
                    self.date_str,
                    _http_error_message(e),
                )
            except URLError as e:
                logger.warning(
                    "Levels GET unreachable for %s — using 0 levels. %s",
                    self.date_str,
                    e.reason,
                )
            except Exception as exc:
                logger.warning(
                    "Levels GET error for %s — using 0 levels: %s",
                    self.date_str,
                    exc,
                )

        response_date = str(data.get("date") or "").strip()
        if response_date and response_date != self.date_str:
            logger.warning(
                "Levels date mismatch: expected %s, got %s — using 0 levels.",
                self.date_str,
                response_date,
            )
            data = {"levels": []}

        self.levels = list(data.get("levels") or [])
        for level in self.levels:
            level.setdefault("status", "ACTIVE")
            self._indexed[(level["index"], level["timeframe"])].append(level)
        logger.info(
            "Levels from API for %s: %s level(s)",
            self.date_str,
            len(self.levels),
        )

    def reload(self) -> None:
        """Reload levels from the API (same as ``load``)."""
        self.load()

    def active_levels(self, index: str, timeframe: str) -> list[dict]:
        """Return active levels for the given index and candle timeframe.

        Args:
            index (str): Index name (e.g. ``NIFTY``).
            timeframe (str): Candle timeframe (e.g. ``1m``).

        Returns:
            list[dict]: Levels with ``status == ACTIVE``.
        """
        return [l for l in self._indexed.get((index, timeframe), []) if l.get("status") == "ACTIVE"]

    def mark_used(self, level: dict) -> None:
        """Mark a level as used so it is ignored by ``active_levels``."""
        level["status"] = "USED"
