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
