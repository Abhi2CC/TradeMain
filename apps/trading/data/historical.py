def fetch_historical(kite, instrument_token: int, from_date: str, to_date: str, interval: str) -> list[dict]:
    return kite.historical_data(instrument_token, from_date, to_date, interval)
