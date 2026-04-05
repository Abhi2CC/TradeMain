import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from urllib.error import HTTPError

from auth.kite_auth import fetch_kite_request_token, try_fetch_kite_request_token


def test_fetch_kite_request_token_success() -> None:
    body = json.dumps({"requestToken": "abc123", "updatedAt": "2026-04-05T00:00:00.000Z"}).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_resp
    mock_cm.__exit__.return_value = None
    with patch("auth.kite_auth.urlopen", return_value=mock_cm):
        assert fetch_kite_request_token("http://localhost:3001") == "abc123"


def test_fetch_kite_request_token_builds_url() -> None:
    """GET uses base URL + /api/v1/kite/request-token only."""
    body = json.dumps({"requestToken": "t"}).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_resp
    mock_cm.__exit__.return_value = None
    with patch("auth.kite_auth.urlopen", return_value=mock_cm) as mock_urlopen:
        fetch_kite_request_token("http://api.example")
    req = mock_urlopen.call_args[0][0]
    assert req.full_url == "http://api.example/api/v1/kite/request-token"


def test_fetch_kite_request_token_empty_base_raises() -> None:
    with pytest.raises(RuntimeError, match="TradeKing API base URL"):
        fetch_kite_request_token("   ")


def test_fetch_kite_request_token_missing_field_raises() -> None:
    body = json.dumps({"updatedAt": "x"}).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_resp
    mock_cm.__exit__.return_value = None
    with patch("auth.kite_auth.urlopen", return_value=mock_cm):
        with pytest.raises(RuntimeError, match="missing requestToken"):
            fetch_kite_request_token("http://localhost:3001")


def test_try_fetch_kite_request_token_empty_url_returns_none() -> None:
    assert try_fetch_kite_request_token("") is None
    assert try_fetch_kite_request_token("   ") is None


def test_try_fetch_kite_request_token_swallows_fetch_error() -> None:
    with patch("auth.kite_auth.fetch_kite_request_token", side_effect=RuntimeError("boom")):
        assert try_fetch_kite_request_token("http://localhost:3001") is None


def test_fetch_kite_request_token_404_raises() -> None:
    err = HTTPError(
        "http://localhost:3001/api/v1/kite/request-token",
        404,
        "Not Found",
        hdrs=None,
        fp=BytesIO(b"{}"),
    )
    with patch("auth.kite_auth.urlopen", side_effect=err):
        with pytest.raises(RuntimeError, match="404"):
            fetch_kite_request_token("http://localhost:3001")
