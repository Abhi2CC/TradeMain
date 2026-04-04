from core.candle_analyzer import matches_pattern


def test_bullish_pattern_match() -> None:
    candle = {"open": 100, "high": 112, "low": 99, "close": 110}
    pattern = {"rules": {"close_gt_open": True, "body_pct_min": 60, "upper_wick_pct_max": 30, "lower_wick_pct_max": 30, "close_gt_level": True}}
    assert matches_pattern(candle, pattern, 105)


def test_zero_range_edge_case() -> None:
    candle = {"open": 100, "high": 100, "low": 100, "close": 100}
    pattern = {"rules": {"close_gt_open": True}}
    assert not matches_pattern(candle, pattern, 99)


def test_failure_wrong_direction() -> None:
    candle = {"open": 110, "high": 112, "low": 100, "close": 101}
    pattern = {"rules": {"close_gt_open": True}}
    assert not matches_pattern(candle, pattern, 100)
