import json
import logging
from datetime import datetime
from analytics.mongo_event_logger import get_mongo_event_logger
from config.settings import ROOT_DIR, settings

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({'timestamp': datetime.utcnow().isoformat(), 'level': record.levelname, 'logger': record.name, 'message': record.getMessage()})


class MongoEventHandler(logging.Handler):
    """Forward all log records to Mongo event sink."""

    def emit(self, record: logging.LogRecord) -> None:
        get_mongo_event_logger().log_record(record)


def configure_logging() -> None:
    log_dir = ROOT_DIR / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'bot_{datetime.now().date()}.log'
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())
    root_logger.handlers.clear()
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setFormatter(JsonFormatter())
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    root_logger.addHandler(fh)
    root_logger.addHandler(ch)
    get_mongo_event_logger().start()
    root_logger.addHandler(MongoEventHandler())
