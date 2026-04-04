def compute_metrics(candle: dict[str, float]) -> dict[str, float | bool]:
    high, low, open_, close = candle['high'], candle['low'], candle['open'], candle['close']
    total_range = high - low
    body = abs(close - open_)
    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low
    body_pct = (body / total_range) * 100 if total_range > 0 else 0
    upper_wick_pct = (upper_wick / total_range) * 100 if total_range > 0 else 0
    lower_wick_pct = (lower_wick / total_range) * 100 if total_range > 0 else 0
    return {'body_pct': body_pct, 'upper_wick_pct': upper_wick_pct, 'lower_wick_pct': lower_wick_pct, 'is_bullish': close > open_, 'is_bearish': close < open_}

def matches_pattern(candle: dict[str, float], pattern: dict, level_price: float) -> bool:
    rules = pattern.get('rules', {})
    m = compute_metrics(candle)
    checks = {
        'close_gt_open': candle['close'] > candle['open'],
        'open_gt_close': candle['open'] > candle['close'],
        'close_gt_level': candle['close'] > level_price,
        'close_lt_level': candle['close'] < level_price,
        'body_pct_min': m['body_pct'] >= rules.get('body_pct_min', 0),
        'upper_wick_pct_max': m['upper_wick_pct'] <= rules.get('upper_wick_pct_max', 100),
        'lower_wick_pct_max': m['lower_wick_pct'] <= rules.get('lower_wick_pct_max', 100),
    }
    for key, value in rules.items():
        if isinstance(value, bool):
            if checks.get(key) != value:
                return False
        elif key in ('body_pct_min', 'upper_wick_pct_max', 'lower_wick_pct_max') and not checks[key]:
            return False
    return True
