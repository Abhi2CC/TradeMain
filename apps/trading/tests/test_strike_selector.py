from core.strike_selector import select_optimal_strike


class FakeKite:
    def ltp(self, instrument: str):
        m = {"NFO:NIFTY29050CE": {"last_price": 50}, "NFO:NIFTY29100CE": {"last_price": 65}}
        return {instrument: m[instrument]}


def resolver(index: str, strike: int, option_type: str):
    return f"{index}{strike}{option_type}", strike


def test_select_optimal_expected_use() -> None:
    out = select_optimal_strike([29050, 29100], "CE", 20000, FakeKite(), "NIFTY", resolver)
    assert out and out["strike"] == 29050


def test_select_optimal_edge_case_no_affordable() -> None:
    class K(FakeKite):
        def ltp(self, instrument: str):
            return {instrument: {"last_price": 10000}}

    assert select_optimal_strike([29050], "CE", 100, K(), "NIFTY", resolver) is None


def test_select_optimal_failure_empty_strikes() -> None:
    assert select_optimal_strike([], "CE", 20000, FakeKite(), "NIFTY", resolver) is None
