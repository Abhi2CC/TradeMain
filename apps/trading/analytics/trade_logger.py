from datetime import date

from config.settings import LOT_SIZES
from storage.db import SessionLocal
from storage.models import Trade


def log_trade(position) -> None:
    """Persist closed trade in the trades table."""
    lot_size = LOT_SIZES.get(position.index, 1)
    lots = max(1, int(position.quantity / lot_size))
    with SessionLocal() as db:
        db.add(
            Trade(
                id=position.id,
                date=date.today(),
                index_name=position.index,
                timeframe=position.signal.timeframe,
                level_type=position.signal.level_type,
                level_price=position.signal.level_price,
                action=position.signal.action,
                option_type=position.option_type,
                tradingsymbol=position.tradingsymbol,
                strike_price=position.signal.level_price,
                entry_time=position.entry_time,
                entry_price=position.entry_price,
                exit_time=position.exit_time,
                exit_price=position.exit_price,
                exit_reason=position.exit_reason,
                quantity=position.quantity,
                lots=lots,
                pnl=position.pnl,
                candles_elapsed=position.candles_elapsed,
                max_candles=position.max_candles,
                pattern_id=position.signal.pattern_id,
            )
        )
        db.commit()
