from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class CandleState:
    bucket_start: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class CandleBuilder:
    def __init__(self) -> None:
        self.frames = {'1m': 1, '5m': 5, '15m': 15}
        self.history = defaultdict(lambda: {'1m': deque(maxlen=500), '5m': deque(maxlen=200), '15m': deque(maxlen=100)})
        self.current: dict[tuple[str, str], CandleState] = {}

    @staticmethod
    def _floor(ts: datetime, minutes: int) -> datetime:
        stripped = ts.replace(second=0, microsecond=0)
        return stripped.replace(minute=stripped.minute - (stripped.minute % minutes))

    def on_tick(self, index: str, timestamp: datetime, ltp: float, volume: float = 0) -> list[dict]:
        closed = []
        for timeframe, mins in self.frames.items():
            key = (index, timeframe)
            bucket = self._floor(timestamp, mins)
            state = self.current.get(key)
            if state is None:
                self.current[key] = CandleState(bucket, ltp, ltp, ltp, ltp, volume)
                continue
            if state.bucket_start == bucket:
                state.high = max(state.high, ltp)
                state.low = min(state.low, ltp)
                state.close = ltp
                state.volume += volume
                continue
            c = {'index': index, 'timeframe': timeframe, 'timestamp': state.bucket_start + timedelta(minutes=mins), 'open': state.open, 'high': state.high, 'low': state.low, 'close': state.close, 'volume': state.volume}
            self.history[index][timeframe].append(c)
            closed.append(c)
            self.current[key] = CandleState(bucket, ltp, ltp, ltp, ltp, volume)
        return closed
