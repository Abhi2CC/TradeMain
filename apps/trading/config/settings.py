from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


def _read_tradeking_api_base_url() -> str:
    """Base URL for apps/Api (MongoDB): levels, Kite request_token, etc."""
    return (
        os.getenv("TRADEKING_API_URL", "").strip()
        or os.getenv("LEVELS_API_URL", "").strip()
    ).rstrip("/")


@dataclass(frozen=True)
class Settings:
    kite_api_key: str = os.getenv('KITE_API_KEY', '')
    kite_api_secret: str = os.getenv('KITE_API_SECRET', '')
    kite_access_token: str = os.getenv('KITE_ACCESS_TOKEN', '')
    db_path: str = os.getenv('DB_PATH', str(ROOT_DIR / 'storage' / 'scalping_bot.db'))
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    max_trades_before_lock: int = int(os.getenv('MAX_TRADES_BEFORE_LOCK', '2'))
    max_candles_default: int = int(os.getenv('MAX_CANDLES_DEFAULT', '10'))
    market_start_time: str = os.getenv('MARKET_START_TIME', '09:15')
    market_end_time: str = os.getenv('MARKET_END_TIME', '15:30')
    eod_squareoff_time: str = os.getenv('EOD_SQUAREOFF_TIME', '15:15')
    dry_run: bool = os.getenv('DRY_RUN', 'true').lower() == 'true'
    api_base_url: str = _read_tradeking_api_base_url()

LOT_SIZES = {'NIFTY': 75, 'BANKNIFTY': 30, 'FINNIFTY': 65}
INDEX_EXCHANGE_SYMBOLS = {
    "NIFTY": "NSE:NIFTY 50",
    "BANKNIFTY": "NSE:NIFTY BANK",
    "FINNIFTY": "NSE:NIFTY FIN SERVICE",
}
_token_cache_override = os.getenv("KITE_TOKEN_CACHE_PATH", "").strip()
TOKEN_CACHE_FILE = (
    Path(_token_cache_override)
    if _token_cache_override
    else ROOT_DIR / "auth" / "token_cache.json"
)
settings = Settings()
