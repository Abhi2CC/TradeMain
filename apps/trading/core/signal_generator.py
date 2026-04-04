from datetime import datetime
from core.candle_analyzer import matches_pattern
from core.types import TradeSignal

class SignalGenerator:
    def __init__(self, patterns: list[dict], max_candles: int = 10) -> None:
        self.patterns = patterns
        self.max_candles = max_candles

    @staticmethod
    def _proximity(level: dict, candle: dict) -> bool:
        p = float(level['price'])
        a = level.get('action', '').upper()
        if a == 'BUY':
            return candle['low'] <= p and candle['close'] >= p
        if a == 'SELL':
            return candle['high'] >= p and candle['close'] <= p
        return False

    def generate(self, candle: dict, levels: list[dict]) -> list[TradeSignal]:
        out = []
        for level in levels:
            if not self._proximity(level, candle):
                continue
            for pattern in self.patterns:
                if matches_pattern(candle, pattern, float(level['price'])):
                    action = level['action'].upper()
                    out.append(TradeSignal(timestamp=candle.get('timestamp', datetime.now()), index=level['index'], timeframe=level['timeframe'], level_type=level['type'], level_price=float(level['price']), action=action, option_type='CE' if action == 'BUY' else 'PE', target_price=float(level['target_price']), stoploss_price=float(level['stoploss']), max_candles=int(level.get('max_candles', self.max_candles)), pattern_id=pattern['id'], candle_data=candle))
                    break
        return out
