import json
from io import BytesIO
from unittest.mock import MagicMock, patch

from urllib.error import HTTPError, URLError

from core.level_manager import LevelManager


def _mock_urlopen_response(payload: dict) -> MagicMock:
    body = json.dumps(payload).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_resp
    mock_ctx.__exit__.return_value = None
    return mock_ctx


@patch("core.level_manager.urlopen")
def test_level_manager_loads_from_api(mock_urlopen: MagicMock) -> None:
    """Levels are parsed from a successful API JSON body."""
    mock_urlopen.return_value = _mock_urlopen_response(
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
    )
    lm = LevelManager(date_str="2025-01-01", api_base_url="http://localhost:3001")
    lm.load()
    assert len(lm.active_levels("NIFTY", "1m")) == 1


@patch("core.level_manager.urlopen")
def test_level_manager_date_mismatch_starts_empty(mock_urlopen: MagicMock) -> None:
    """Response date mismatch should not be used for trading levels."""
    mock_urlopen.return_value = _mock_urlopen_response(
        {
            "date": "2025-01-02",
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
    )
    lm = LevelManager(date_str="2025-01-01", api_base_url="http://localhost:3001")
    lm.load()
    assert lm.levels == []


def test_level_manager_no_api_url_starts_empty() -> None:
    """Missing base URL does not raise; levels stay empty."""
    lm = LevelManager(date_str="2099-01-01", api_base_url=None)
    lm.load()
    assert lm.levels == []


@patch("core.level_manager.urlopen")
def test_level_manager_http_404_starts_empty(mock_urlopen: MagicMock) -> None:
    """404 does not raise; levels stay empty."""
    fp = BytesIO(b'{"error":"Not Found","message":"No levels for 2025-04-01"}')
    err = HTTPError("http://x", 404, "Not Found", hdrs=None, fp=fp)
    mock_urlopen.side_effect = err
    lm = LevelManager(date_str="2025-04-01", api_base_url="http://localhost:3001")
    lm.load()
    assert lm.levels == []
    assert lm.active_levels("NIFTY", "1m") == []


@patch("core.level_manager.urlopen")
def test_level_manager_http_5xx_starts_empty(mock_urlopen: MagicMock) -> None:
    """Other HTTP errors do not raise; levels stay empty."""
    err = HTTPError("http://x", 500, "Server Error", hdrs=None, fp=BytesIO())
    mock_urlopen.side_effect = err
    lm = LevelManager(date_str="2025-01-01", api_base_url="http://localhost:3001")
    lm.load()
    assert lm.levels == []


@patch("core.level_manager.urlopen")
def test_level_manager_url_error_starts_empty(mock_urlopen: MagicMock) -> None:
    """Network errors do not raise; levels stay empty."""
    mock_urlopen.side_effect = URLError("connection refused")
    lm = LevelManager(date_str="2025-01-01", api_base_url="http://localhost:3001")
    lm.load()
    assert lm.levels == []
