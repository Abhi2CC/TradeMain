from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class TradeSignal:
    timestamp: datetime
    index: str
    timeframe: str
    level_type: str
    level_price: float
    action: str
    option_type: str
    target_price: float
    stoploss_price: float
    max_candles: int
    pattern_id: str
    candle_data: dict[str, Any]
    status: str = 'PENDING'

@dataclass
class Position:
    id: str
    signal: TradeSignal
    entry_order_id: str
    entry_price: float
    entry_time: datetime
    tradingsymbol: str
    quantity: int
    index: str
    option_type: str
    target_price: float
    stoploss_price: float
    max_candles: int
    candles_elapsed: int = 0
    status: str = 'OPEN'
    exit_price: float | None = None
    exit_time: datetime | None = None
    exit_reason: str | None = None
    pnl: float | None = None
