from __future__ import annotations

from datetime import datetime, timezone
import logging
import queue
import threading
from typing import Any

from config.settings import settings

try:
    from pymongo import MongoClient
except Exception:  # pragma: no cover
    MongoClient = None


class MongoEventLogger:
    """Best-effort async MongoDB sink for bot logs/events."""

    def __init__(self) -> None:
        self.enabled = bool(settings.mongo_events_enabled and settings.mongo_events_uri.strip())
        self._q: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=5000)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._client = None
        self._collection = None
        self._internal_logger = logging.getLogger("analytics.mongo_event_logger")

    def start(self) -> None:
        if not self.enabled or self._thread is not None:
            return
        if MongoClient is None:
            self._internal_logger.warning("Mongo events disabled: pymongo is not installed.")
            self.enabled = False
            return
        try:
            self._client = MongoClient(settings.mongo_events_uri, serverSelectionTimeoutMS=3000)
            self._collection = self._client[settings.mongo_events_db][settings.mongo_events_collection]
            self._collection.create_index("ts")
            self._collection.create_index([("event_type", 1), ("ts", -1)])
        except Exception as exc:
            self._internal_logger.warning("Mongo events disabled: unable to connect (%s)", exc)
            self.enabled = False
            return
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        self._internal_logger.info(
            "Mongo events enabled: %s/%s",
            settings.mongo_events_db,
            settings.mongo_events_collection,
        )

    def stop(self) -> None:
        if not self.enabled:
            return
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        self._flush_once()
        if self._client:
            self._client.close()

    def event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        if not self.enabled:
            return
        doc = {
            "ts": datetime.now(timezone.utc),
            "event_type": event_type,
            "payload": payload or {},
        }
        self._push(doc)

    def log_record(self, record: logging.LogRecord) -> None:
        if not self.enabled:
            return
        self._push(
            {
                "ts": datetime.now(timezone.utc),
                "event_type": "LOG_RECORD",
                "payload": {
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                },
            }
        )

    def _push(self, doc: dict[str, Any]) -> None:
        try:
            self._q.put_nowait(doc)
        except queue.Full:
            # Drop oldest-ish behavior: discard newest when overloaded.
            pass

    def _worker(self) -> None:
        while not self._stop.is_set():
            self._flush_once()
            self._stop.wait(1.0)

    def _flush_once(self) -> None:
        if not self._collection:
            return
        batch: list[dict[str, Any]] = []
        while len(batch) < settings.mongo_events_batch_size:
            try:
                batch.append(self._q.get_nowait())
            except queue.Empty:
                break
        if not batch:
            return
        try:
            self._collection.insert_many(batch, ordered=False)
        except Exception:
            # Best-effort only; don't break trading flow.
            pass


_LOGGER = MongoEventLogger()


def get_mongo_event_logger() -> MongoEventLogger:
    return _LOGGER

