from dataclasses import dataclass

@dataclass
class RiskManager:
    trade_count_today: int = 0
    max_trades: int = 2
    is_locked: bool = False
    lock_reason: str | None = None
    max_daily_loss: float | None = None
    realized_pnl: float = 0.0

    def can_trade(self) -> tuple[bool, str]:
        if self.is_locked:
            return False, f'Locked: {self.lock_reason}'
        if self.trade_count_today >= self.max_trades:
            self.is_locked = True
            self.lock_reason = 'AUTO_LOCK: Max trades reached'
            return False, self.lock_reason
        if self.max_daily_loss and self.realized_pnl <= -self.max_daily_loss:
            self.is_locked = True
            self.lock_reason = 'AUTO_LOCK: Max daily loss breached'
            return False, self.lock_reason
        return True, 'OK'

    def record_trade(self, pnl: float) -> None:
        self.trade_count_today += 1
        self.realized_pnl += pnl

    def unlock(self) -> None:
        self.is_locked = False
        self.lock_reason = None
