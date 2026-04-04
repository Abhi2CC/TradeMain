from core.signal_generator import SignalGenerator


def test_signal_generation_expected_use() -> None:
    candle = {"open": 100, "high": 112, "low": 99, "close": 110}
    level = {"index": "NIFTY", "timeframe": "1m", "price": 100, "type": "EU-S", "action": "BUY", "target_price": 120, "stoploss": 95}
    patterns = [{"id": "P1", "rules": {"close_gt_open": True, "close_gt_level": True}}]
    out = SignalGenerator(patterns, max_candles=10).generate(candle, [level])
    assert len(out) == 1


def test_signal_edge_case_no_levels() -> None:
    out = SignalGenerator([], max_candles=10).generate({"open": 1, "high": 1, "low": 1, "close": 1}, [])
    assert out == []


def test_signal_failure_proximity_fail() -> None:
    candle = {"open": 100, "high": 101, "low": 100.5, "close": 101}
    level = {"index": "NIFTY", "timeframe": "1m", "price": 99, "type": "EU-S", "action": "BUY", "target_price": 102, "stoploss": 95}
    patterns = [{"id": "P1", "rules": {"close_gt_open": True, "close_gt_level": True}}]
    assert SignalGenerator(patterns).generate(candle, [level]) == []
