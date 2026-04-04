from collections import defaultdict
import json
import logging
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class LevelManager:
    """Load levels from Levels API (GET) or optional local JSON fallback."""

    def __init__(
        self,
        *,
        date_str: str,
        api_base_url: str | None = None,
        api_key: str | None = None,
        fallback_file: Path | None = None,
    ) -> None:
        self.date_str = date_str
        self.api_base_url = (api_base_url or "").strip().rstrip("/") or None
        self.api_key = (api_key or "").strip() or None
        self.fallback_file = fallback_file
        self.levels: list[dict] = []
        self._indexed: dict[tuple[str, str], list[dict]] = defaultdict(list)

    def _fetch_from_api(self) -> dict:
        url = f"{self.api_base_url}/api/v1/levels/{self.date_str}"
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        req = Request(url, headers=headers, method="GET")
        with urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
        return json.loads(body)

    def load(self) -> None:
        self.levels = []
        self._indexed.clear()

        data: dict | None = None
        if self.api_base_url:
            try:
                data = self._fetch_from_api()
                logger.info("Levels loaded from API for %s", self.date_str)
            except HTTPError as e:
                logger.error("Levels API HTTP %s: %s", e.code, e.reason)
            except URLError as e:
                logger.error("Levels API network error: %s", e.reason)
            except Exception as exc:
                logger.exception("Levels API error: %s", exc)

        if data is None and self.fallback_file and self.fallback_file.exists():
            logger.warning("Using fallback levels file: %s", self.fallback_file)
            data = json.loads(self.fallback_file.read_text(encoding="utf-8"))

        if data is None:
            logger.error("No levels available (API failed and no fallback file)")
            return

        self.levels = data.get("levels", [])
        for level in self.levels:
            level.setdefault("status", "ACTIVE")
            self._indexed[(level["index"], level["timeframe"])].append(level)

    def reload(self) -> None:
        self.load()

    def active_levels(self, index: str, timeframe: str) -> list[dict]:
        return [l for l in self._indexed.get((index, timeframe), []) if l.get("status") == "ACTIVE"]

    def mark_used(self, level: dict) -> None:
        level["status"] = "USED"
