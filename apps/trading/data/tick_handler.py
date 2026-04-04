from kiteconnect import KiteTicker

class TickHandler:
    def __init__(self, api_key: str, access_token: str, on_ticks):
        self.kws = KiteTicker(api_key, access_token, reconnect=True, reconnect_max_tries=5, reconnect_max_delay=60)
        self.kws.on_ticks = on_ticks

    def attach_callbacks(self, on_connect, on_close, on_error, on_order_update):
        self.kws.on_connect = on_connect
        self.kws.on_close = on_close
        self.kws.on_error = on_error
        self.kws.on_order_update = on_order_update
        self.kws.on_reconnect = lambda ws, attempts_count: on_error(ws, 0, f"Reconnecting attempt={attempts_count}")
        self.kws.on_noreconnect = lambda ws: on_error(ws, 0, "Reconnect attempts exhausted")

    def subscribe_full(self, instrument_tokens: list[int]) -> None:
        self.kws.subscribe(instrument_tokens)
        self.kws.set_mode(self.kws.MODE_FULL, instrument_tokens)

    def connect(self) -> None:
        self.kws.connect(threaded=True)
