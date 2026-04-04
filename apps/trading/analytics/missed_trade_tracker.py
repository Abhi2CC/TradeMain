from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from storage.db import SessionLocal
from storage.models import MissedTrade as MissedTradeModel


@dataclass
class MissedTradeRecord:
    signal: object
    reason: str
    theoretical_entry: float
    theoretical_target: float
    outcome: str | None = None
    theoretical_pnl: float | None = None


class MissedTradeTracker:
    """Collect valid-but-blocked signals for EOD analysis."""

    def __init__(self) -> None:
        self.missed: list[MissedTradeRecord] = []

    def add(self, signal, reason: str) -> None:
        record = MissedTradeRecord(signal, reason, signal.level_price, signal.target_price)
        self.missed.append(record)
        with SessionLocal() as db:
            db.add(
                MissedTradeModel(
                    id=str(uuid4()),
                    date=date.today(),
                    index_name=signal.index,
                    timeframe=signal.timeframe,
                    level_type=signal.level_type,
                    level_price=signal.level_price,
                    action=signal.action,
                    signal_time=signal.timestamp,
                    reason=reason,
                    theoretical_entry=signal.level_price,
                    theoretical_target=signal.target_price,
                )
            )
            db.commit()
