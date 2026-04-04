import json
from pathlib import Path
from tempfile import TemporaryDirectory

from core.level_manager import LevelManager


def test_level_manager_fallback_file() -> None:
    with TemporaryDirectory() as tmp:
        p = Path(tmp) / "day.json"
        p.write_text(
            json.dumps(
                {
                    "date": "2025-01-01",
                    "levels": [
                        {
                            "index": "NIFTY",
                            "timeframe": "1m",
                            "price": 100,
                            "type": "EU-S",
                            "action": "BUY",
                            "target_price": 110,
                            "stoploss": 95,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        lm = LevelManager(date_str="2025-01-01", api_base_url=None, fallback_file=p)
        lm.load()
        assert len(lm.active_levels("NIFTY", "1m")) == 1


def test_level_manager_empty_without_api_or_file() -> None:
    lm = LevelManager(date_str="2099-01-01", api_base_url=None, fallback_file=None)
    lm.load()
    assert lm.levels == []
