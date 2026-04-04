from datetime import datetime
from uuid import uuid4
from core.types import Position

class PositionManager:
    def __init__(self) -> None:
        self.positions: dict[str, Position] = {}

    def has_open_for_index(self, index: str) -> bool:
        return any(p.status == 'OPEN' and p.index == index for p in self.positions.values())

    def open_position(self, signal, order_id: str, tradingsymbol: str, quantity: int, entry_price: float) -> Position:
        p = Position(id=str(uuid4()), signal=signal, entry_order_id=order_id, entry_price=entry_price, entry_time=datetime.now(), tradingsymbol=tradingsymbol, quantity=quantity, index=signal.index, option_type=signal.option_type, target_price=signal.target_price, stoploss_price=signal.stoploss_price, max_candles=signal.max_candles)
        self.positions[p.id] = p
        return p

    def on_tick(self, index: str, price: float) -> list[tuple[Position, str]]:
        exits = []
        for p in self.positions.values():
            if p.status != 'OPEN' or p.index != index:
                continue
            action = p.signal.action
            if action == 'BUY' and price <= p.stoploss_price:
                exits.append((p, 'SL_HIT'))
            elif action == 'BUY' and price >= p.target_price:
                exits.append((p, 'TARGET_HIT'))
            elif action == 'SELL' and price >= p.stoploss_price:
                exits.append((p, 'SL_HIT'))
            elif action == 'SELL' and price <= p.target_price:
                exits.append((p, 'TARGET_HIT'))
        return exits

    def on_candle_close(self, index: str, timeframe: str) -> list[tuple[Position, str]]:
        exits = []
        for p in self.positions.values():
            if p.status != 'OPEN':
                continue
            if p.index == index and p.signal.timeframe == timeframe:
                p.candles_elapsed += 1
                if p.candles_elapsed >= p.max_candles:
                    exits.append((p, 'CANDLE_TIMEOUT'))
        return exits

    def close_position(self, position: Position, exit_price: float, reason: str) -> None:
        position.status = 'CLOSED'
        position.exit_reason = reason
        position.exit_price = exit_price
        position.exit_time = datetime.now()
        if position.signal.action == 'BUY':
            position.pnl = (exit_price - position.entry_price) * position.quantity
        else:
            position.pnl = (position.entry_price - exit_price) * position.quantity
