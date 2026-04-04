from core.risk_manager import RiskManager


def test_can_trade_expected_use() -> None:
    rm = RiskManager(max_trades=2)
    ok, _ = rm.can_trade()
    assert ok


def test_edge_manual_unlock() -> None:
    rm = RiskManager(max_trades=1)
    rm.record_trade(-10)
    ok, _ = rm.can_trade()
    assert not ok
    rm.unlock()
    assert rm.is_locked is False


def test_failure_max_daily_loss() -> None:
    rm = RiskManager(max_trades=5, max_daily_loss=100)
    rm.record_trade(-150)
    ok, msg = rm.can_trade()
    assert (not ok) and ("Max daily loss" in msg)
