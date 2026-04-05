"""Path resolution in config.settings (subprocess: fresh import per env)."""

import os
import subprocess
import sys
from pathlib import Path

_TRADING_ROOT = Path(__file__).resolve().parents[1]


def test_token_cache_file_uses_env_override() -> None:
    """KITE_TOKEN_CACHE_PATH overrides default auth/token_cache.json."""
    env = os.environ.copy()
    env["KITE_TOKEN_CACHE_PATH"] = "/data/kite_token_cache.json"
    prog = (
        "from pathlib import Path; "
        "from config.settings import TOKEN_CACHE_FILE; "
        "assert TOKEN_CACHE_FILE == Path('/data/kite_token_cache.json')"
    )
    r = subprocess.run(
        [sys.executable, "-c", prog],
        cwd=str(_TRADING_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_token_cache_file_default_under_auth() -> None:
    """Without KITE_TOKEN_CACHE_PATH, cache file lives under auth/."""
    env = os.environ.copy()
    env.pop("KITE_TOKEN_CACHE_PATH", None)
    prog = (
        "from config.settings import ROOT_DIR, TOKEN_CACHE_FILE; "
        "assert TOKEN_CACHE_FILE == ROOT_DIR / 'auth' / 'token_cache.json'"
    )
    r = subprocess.run(
        [sys.executable, "-c", prog],
        cwd=str(_TRADING_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_api_base_url_prefers_tradeking_over_levels() -> None:
    """TRADEKING_API_URL wins when both env vars are set."""
    env = os.environ.copy()
    env.pop("TRADEKING_API_URL", None)
    env.pop("LEVELS_API_URL", None)
    env["TRADEKING_API_URL"] = "http://primary:3001"
    env["LEVELS_API_URL"] = "http://legacy:3001"
    prog = (
        "import importlib; "
        "import config.settings as s; "
        "importlib.reload(s); "
        "assert s.settings.api_base_url == 'http://primary:3001'"
    )
    r = subprocess.run(
        [sys.executable, "-c", prog],
        cwd=str(_TRADING_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_api_base_url_falls_back_to_levels_url() -> None:
    """LEVELS_API_URL is used when TRADEKING_API_URL is empty (and not overridden by .env)."""
    env = os.environ.copy()
    env["TRADEKING_API_URL"] = ""
    env["LEVELS_API_URL"] = "http://only-legacy:3001"
    prog = (
        "import importlib; "
        "import config.settings as s; "
        "importlib.reload(s); "
        "assert s.settings.api_base_url == 'http://only-legacy:3001'"
    )
    r = subprocess.run(
        [sys.executable, "-c", prog],
        cwd=str(_TRADING_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
