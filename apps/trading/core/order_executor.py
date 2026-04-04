import logging
import time
from config.settings import LOT_SIZES, settings

logger = logging.getLogger(__name__)

class OrderExecutor:
    def __init__(self, kite) -> None:
        self.kite = kite

    def _has_funds(self) -> bool:
        return bool(self.kite.margins())

    def _has_open_order(self, tradingsymbol: str, transaction_type: str) -> bool:
        """Prevent duplicate OPEN/TRIGGER PENDING orders for same symbol + side."""
        try:
            for order in self.kite.orders():
                if order.get("tradingsymbol") != tradingsymbol:
                    continue
                if order.get("transaction_type") != transaction_type:
                    continue
                if order.get("status") in {"OPEN", "TRIGGER PENDING", "VALIDATION PENDING"}:
                    return True
        except Exception as exc:
            logger.warning("Unable to check existing open orders: %s", exc)
        return False

    def place_entry_order(self, signal, strike_info: dict) -> str:
        if not self._has_funds():
            raise RuntimeError('Insufficient margin')
        quantity = strike_info['lots'] * LOT_SIZES[signal.index]
        if self._has_open_order(strike_info["tradingsymbol"], self.kite.TRANSACTION_TYPE_BUY):
            raise RuntimeError("Duplicate entry blocked: open order exists")
        if settings.dry_run:
            logger.info('DRY_RUN entry: %s qty=%s', strike_info['tradingsymbol'], quantity)
            return f'DRY_ENTRY_{signal.timestamp.timestamp()}'
        time.sleep(0.35)  # Respect API pacing for order endpoints.
        return self.kite.place_order(variety=self.kite.VARIETY_REGULAR, exchange=self.kite.EXCHANGE_NFO, tradingsymbol=strike_info['tradingsymbol'], transaction_type=self.kite.TRANSACTION_TYPE_BUY, quantity=quantity, product=self.kite.PRODUCT_MIS, order_type=self.kite.ORDER_TYPE_MARKET, tag='SCALP')

    def place_exit_order(self, position) -> str:
        if settings.dry_run:
            logger.info('DRY_RUN exit: %s qty=%s', position.tradingsymbol, position.quantity)
            return f'DRY_EXIT_{position.id}'
        if self._has_open_order(position.tradingsymbol, self.kite.TRANSACTION_TYPE_SELL):
            raise RuntimeError("Duplicate exit blocked: open order exists")
        time.sleep(0.35)
        return self.kite.place_order(variety=self.kite.VARIETY_REGULAR, exchange=self.kite.EXCHANGE_NFO, tradingsymbol=position.tradingsymbol, transaction_type=self.kite.TRANSACTION_TYPE_SELL, quantity=position.quantity, product=self.kite.PRODUCT_MIS, order_type=self.kite.ORDER_TYPE_MARKET, tag='EXIT')

    def get_order_fill_price(self, order_id: str) -> float | None:
        """Poll order history and return average fill price once complete."""
        if settings.dry_run:
            return None
        for _ in range(12):
            history = self.kite.order_history(order_id)
            last = history[-1] if history else {}
            status = str(last.get("status", "")).upper()
            if status == "COMPLETE":
                return float(last.get("average_price", 0) or 0)
            if status in {"REJECTED", "CANCELLED"}:
                raise RuntimeError(f"Order {order_id} {status}: {last.get('status_message')}")
            time.sleep(0.5)
        return None

    def get_option_ltp(self, tradingsymbol: str) -> float:
        """Fetch option LTP for fill simulation fallback."""
        data = self.kite.ltp(f"NFO:{tradingsymbol}")
        return float(data[f"NFO:{tradingsymbol}"]["last_price"])
