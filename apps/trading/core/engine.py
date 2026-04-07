from datetime import datetime, time
import json
import logging
import threading
import time as time_mod

from analytics.missed_trade_tracker import MissedTradeTracker
from analytics.trade_logger import log_trade
from analytics.report_generator import generate_report
from auth.kite_auth import KiteAuth
from config.instruments import build_option_lookup
from config.logging_config import configure_logging
from config.settings import INDEX_EXCHANGE_SYMBOLS, LOT_SIZES, ROOT_DIR, settings
from core.fund_allocator import FundAllocator
from core.level_manager import LevelManager
from core.order_executor import OrderExecutor
from core.position_manager import PositionManager
from core.risk_manager import RiskManager
from core.signal_generator import SignalGenerator
from core.strike_selector import select_optimal_strike
from data.candle_builder import CandleBuilder
from data.tick_handler import TickHandler
from storage.db import init_db

logger = logging.getLogger(__name__)


class TradingEngine:
    """Main orchestrator for the trading bot."""

    def __init__(self) -> None:
        configure_logging()
        init_db()
        self.auth = KiteAuth(settings.kite_api_key, settings.kite_api_secret)
        self.kite = None
        self.candle_builder = CandleBuilder()
        self.position_manager = PositionManager()
        self.missed = MissedTradeTracker()
        self.closed_positions: list = []
        self.running = False
        self.tick_handler: TickHandler | None = None
        self.last_tick_at = datetime.now()
        self.instrument_cache: dict[str, dict[tuple[int, str], dict]] = {}
        self.index_token_to_name: dict[int, str] = {}
        self.eod_done = False

        daily = json.loads((ROOT_DIR / "config" / "daily_config.json").read_text(encoding="utf-8"))
        patterns = json.loads((ROOT_DIR / "config" / "candle_patterns.json").read_text(encoding="utf-8"))["patterns"]
        date_str = datetime.now().date().isoformat()

        self.levels = LevelManager(
            date_str=date_str,
            api_base_url=settings.api_base_url or None,
        )
        self.levels.load()
        self.signals = SignalGenerator(patterns=patterns, max_candles=daily.get("max_candles", settings.max_candles_default))
        self.risk = RiskManager(max_trades=daily.get("max_trades_before_lock", settings.max_trades_before_lock), max_daily_loss=daily.get("max_daily_loss"))
        self.funds = FundAllocator(daily.get("fund_allocation", {}))
        self.strike_prices = daily.get("strike_prices", {})
        self.latest_index_prices: dict[str, float] = {}

    def start(self) -> None:
        self._wait_for_market_start()
        self.kite = self.auth.bootstrap()
        self.order_executor = OrderExecutor(self.kite)
        self._load_instrument_cache()
        self._check_crash_recovery_positions()
        self.running = True

        self.tick_handler = TickHandler(settings.kite_api_key, self.kite.access_token, self._on_ticks)
        self.tick_handler.attach_callbacks(self._on_connect, self._on_close, self._on_error, self._on_order_update)
        self.tick_handler.connect()
        threading.Thread(target=self._watchdog_loop, daemon=True).start()
        threading.Thread(target=self._cli_loop, daemon=True).start()

        logger.info("Trading engine initialized. DRY_RUN=%s", settings.dry_run)
        while self.running:
            if not self.eod_done and self.is_eod_squareoff(datetime.now()):
                logger.warning("EOD squareoff time reached, exiting all positions")
                self.emergency_exit_all(reason="EOD_SQUAREOFF")
                self.eod_done = True
            if self._is_after_market_end(datetime.now()):
                logger.info("Market end reached (%s). Stopping engine.", settings.market_end_time)
                self.running = False
            time_mod.sleep(1)
        self.stop()

    def stop(self) -> None:
        self.running = False
        if self.tick_handler:
            self.tick_handler.kws.close()
        report = generate_report(self.closed_positions, self.missed.missed, ROOT_DIR / "logs")
        logger.info("Engine stopped. Report: %s", report)

    def is_eod_squareoff(self, now: datetime) -> bool:
        h, m = settings.eod_squareoff_time.split(":")
        return now.time() >= time(hour=int(h), minute=int(m))

    def on_tick(self, index: str, ltp: float, timestamp: datetime, volume: float = 0) -> None:
        """Process live index tick and evaluate exits + candle close events."""
        self.latest_index_prices[index] = ltp
        for position, reason in self.position_manager.on_tick(index, ltp):
            self._exit_position(position, reason)

        for candle in self.candle_builder.on_tick(index=index, timestamp=timestamp, ltp=ltp, volume=volume):
            self.on_candle_close(candle)

    def on_candle_close(self, candle: dict) -> None:
        """Generate signals and process timeout exits on candle close."""
        levels = self.levels.active_levels(candle["index"], candle["timeframe"])
        for signal in self.signals.generate(candle, levels):
            self.on_signal(signal)
        for position, reason in self.position_manager.on_candle_close(candle["index"], candle["timeframe"]):
            self._exit_position(position, reason)

    def _resolver(self, index: str, strike: int, option_type: str) -> tuple[str, int]:
        """Resolve tradingsymbol and token from the daily instruments dump."""
        ins = self.instrument_cache.get(index, {}).get((int(strike), option_type))
        if ins:
            return ins["tradingsymbol"], int(ins["instrument_token"])
        raise ValueError(f"No instrument found for {index} {strike} {option_type}")

    def on_signal(self, signal) -> None:
        """Validate signal with risk and execution constraints, then place order."""
        if not self._is_within_trading_window(datetime.now()):
            self.missed.add(signal, "OUTSIDE_WINDOW")
            logger.info("Signal blocked (OUTSIDE_WINDOW): %s", signal)
            return
        allowed, reason = self.risk.can_trade()
        if not allowed:
            self.missed.add(signal, "AUTO_LOCKED")
            logger.info("Signal blocked (%s): %s", reason, signal)
            return
        if self.position_manager.has_open_for_index(signal.index):
            self.missed.add(signal, "DUPLICATE_POSITION")
            return

        strike_info = select_optimal_strike(
            available_strikes=self.strike_prices.get(signal.index, []),
            option_type=signal.option_type,
            allocated_funds=self.funds.funds_for(signal.index),
            kite=self.kite,
            index=signal.index,
            tradingsymbol_resolver=self._resolver,
        )
        if not strike_info:
            self.missed.add(signal, "NO_FUNDS")
            return

        order_id = self.order_executor.place_entry_order(signal, strike_info)
        entry_price = self.order_executor.get_order_fill_price(order_id) or strike_info["ltp"]
        position = self.position_manager.open_position(
            signal=signal,
            order_id=order_id,
            tradingsymbol=strike_info["tradingsymbol"],
            quantity=strike_info["lots"] * LOT_SIZES[signal.index],
            entry_price=entry_price,
        )
        signal.status = "EXECUTED"
        logger.info("Position opened: %s", position.id)

    def _exit_position(self, position, reason: str) -> None:
        """Exit a position and update realized PnL."""
        if position.status != "OPEN":
            return
        order_id = self.order_executor.place_exit_order(position)
        exit_price = self.order_executor.get_order_fill_price(order_id)
        if exit_price is None:
            exit_price = self.order_executor.get_option_ltp(position.tradingsymbol)
        self.position_manager.close_position(position, exit_price=exit_price, reason=reason)
        self.closed_positions.append(position)
        log_trade(position)
        self.risk.record_trade(position.pnl or 0)
        logger.info("Position closed: %s reason=%s pnl=%s", position.id, reason, position.pnl)

    def emergency_exit_all(self, reason: str = "MANUAL") -> None:
        """Kill switch: close all open positions immediately."""
        for position in list(self.position_manager.positions.values()):
            self._exit_position(position, reason)

    def _load_instrument_cache(self) -> None:
        """Cache exchange instruments and token lookups once per startup."""
        nfo = self.kite.instruments("NFO")
        nse = self.kite.instruments("NSE")
        for index in ("NIFTY", "BANKNIFTY", "FINNIFTY"):
            self.instrument_cache[index] = build_option_lookup(nfo, index)

        symbol_map = {
            "NIFTY 50": "NIFTY",
            "NIFTY BANK": "BANKNIFTY",
            "NIFTY FIN SERVICE": "FINNIFTY",
        }
        for ins in nse:
            ts = str(ins.get("tradingsymbol", ""))
            if ts in symbol_map:
                self.index_token_to_name[int(ins["instrument_token"])] = symbol_map[ts]

    def _all_subscribe_tokens(self) -> list[int]:
        tokens = list(self.index_token_to_name.keys())
        for index, strikes in self.strike_prices.items():
            for strike in strikes:
                for side in ("CE", "PE"):
                    ins = self.instrument_cache.get(index, {}).get((int(strike), side))
                    if ins:
                        tokens.append(int(ins["instrument_token"]))
        return sorted(set(tokens))

    def _on_connect(self, ws, response) -> None:
        tokens = self._all_subscribe_tokens()
        if tokens:
            self.tick_handler.subscribe_full(tokens)
            logger.info("Subscribed %s tokens", len(tokens))

    def _on_close(self, ws, code, reason) -> None:
        logger.warning("WebSocket closed code=%s reason=%s", code, reason)

    def _on_error(self, ws, code, reason) -> None:
        logger.error("WebSocket error code=%s reason=%s", code, reason)

    def _on_order_update(self, ws, data) -> None:
        logger.info("Order update: %s", data)

    def _on_ticks(self, ws, ticks: list[dict]) -> None:
        self.last_tick_at = datetime.now()
        for tick in ticks:
            token = int(tick.get("instrument_token", 0))
            index = self.index_token_to_name.get(token)
            if not index:
                continue
            ltp = float(tick.get("last_price", 0))
            timestamp = tick.get("timestamp") or datetime.now()
            volume = float(tick.get("volume", 0))
            self.on_tick(index=index, ltp=ltp, timestamp=timestamp, volume=volume)

    def _watchdog_loop(self) -> None:
        while self.running:
            now = datetime.now()
            if self._is_within_trading_window(now):
                stale = (now - self.last_tick_at).total_seconds()
                if stale > 30:
                    logger.warning("Stale market data: no tick for %.0f seconds", stale)
            time_mod.sleep(5)

    @staticmethod
    def _parse_hhmm(value: str) -> time:
        h, m = value.split(":")
        return time(hour=int(h), minute=int(m))

    def _is_within_trading_window(self, now: datetime) -> bool:
        t = now.time()
        return self._parse_hhmm(settings.market_start_time) <= t <= self._parse_hhmm(settings.market_end_time)

    def _is_after_market_end(self, now: datetime) -> bool:
        return now.time() > self._parse_hhmm(settings.market_end_time)

    def _wait_for_market_start(self) -> None:
        while True:
            now = datetime.now()
            start_time = self._parse_hhmm(settings.market_start_time)
            end_time = self._parse_hhmm(settings.market_end_time)
            if now.time() >= end_time:
                raise RuntimeError(
                    f"Current time {now.strftime('%H:%M')} is after MARKET_END_TIME {settings.market_end_time}. "
                    "Start bot during the configured trading day."
                )
            if now.time() >= start_time:
                return
            wait_seconds = int((datetime.combine(now.date(), start_time) - now).total_seconds())
            logger.info(
                "Waiting for market start %s (about %ss)...",
                settings.market_start_time,
                max(wait_seconds, 1),
            )
            time_mod.sleep(min(max(wait_seconds, 1), 30))

    def _check_crash_recovery_positions(self) -> None:
        try:
            positions = self.kite.positions()
            net_positions = positions.get("net", []) if isinstance(positions, dict) else []
            open_mis = [p for p in net_positions if p.get("product") == "MIS" and int(p.get("quantity", 0)) != 0]
            if open_mis:
                logger.critical("Crash recovery: found %s open MIS positions", len(open_mis))
        except Exception as exc:
            logger.warning("Crash recovery check failed: %s", exc)

    def _cli_loop(self) -> None:
        while self.running:
            try:
                cmd = input().strip().lower()
            except EOFError:
                return
            if cmd == "u":
                self.risk.unlock()
                logger.info("Manual unlock applied")
            elif cmd == "s":
                open_positions = [p for p in self.position_manager.positions.values() if p.status == "OPEN"]
                logger.info("Open positions: %s", len(open_positions))
            elif cmd == "p":
                logger.info("Realized PnL: %s | Trades: %s", self.risk.realized_pnl, self.risk.trade_count_today)
            elif cmd == "r":
                self.levels.reload()
                logger.info("Levels reloaded")
            elif cmd == "k":
                self.emergency_exit_all(reason="MANUAL")
                self.running = False
            elif cmd == "q":
                self.emergency_exit_all(reason="MANUAL")
                self.running = False
