from dataclasses import asdict
from datetime import date
import json
from pathlib import Path


def generate_report(trades: list, missed: list, output_dir: Path) -> Path:
    """Write end-of-day JSON report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"report_{date.today()}.json"
    payload = {
        "date": str(date.today()),
        "total_trades": len(trades),
        "net_pnl": sum((t.pnl or 0) for t in trades),
        "missed_trades": len(missed),
        "trades": [asdict(t) for t in trades],
        "missed": [asdict(m) for m in missed],
    }
    path.write_text(json.dumps(payload, default=str, indent=2), encoding="utf-8")
    return path
