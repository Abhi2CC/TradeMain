from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Trade(Base):
    __tablename__ = 'trades'
    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    index_name: Mapped[str] = mapped_column(String, nullable=False)
    timeframe: Mapped[str] = mapped_column(String, nullable=False)
    level_type: Mapped[str] = mapped_column(String, nullable=False)
    level_price: Mapped[float] = mapped_column(Float, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    option_type: Mapped[str] = mapped_column(String, nullable=False)
    tradingsymbol: Mapped[str] = mapped_column(String, nullable=False)
    strike_price: Mapped[float] = mapped_column(Float, nullable=False)
    entry_time: Mapped[str] = mapped_column(DateTime, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_time: Mapped[str | None] = mapped_column(DateTime)
    exit_price: Mapped[float | None] = mapped_column(Float)
    exit_reason: Mapped[str | None] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    lots: Mapped[int] = mapped_column(Integer, nullable=False)
    pnl: Mapped[float | None] = mapped_column(Float)
    candles_elapsed: Mapped[int | None] = mapped_column(Integer)
    max_candles: Mapped[int] = mapped_column(Integer, nullable=False)
    pattern_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

class MissedTrade(Base):
    __tablename__ = 'missed_trades'
    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    index_name: Mapped[str] = mapped_column(String, nullable=False)
    timeframe: Mapped[str] = mapped_column(String, nullable=False)
    level_type: Mapped[str] = mapped_column(String, nullable=False)
    level_price: Mapped[float] = mapped_column(Float, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    signal_time: Mapped[str] = mapped_column(DateTime, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    theoretical_entry: Mapped[float | None] = mapped_column(Float)
    theoretical_target: Mapped[float | None] = mapped_column(Float)
    target_hit: Mapped[bool | None] = mapped_column(Boolean)
    theoretical_pnl: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class DailySummary(Base):
    __tablename__ = "daily_summary"
    date: Mapped[str] = mapped_column(Date, primary_key=True)
    total_trades: Mapped[int | None] = mapped_column(Integer)
    winning_trades: Mapped[int | None] = mapped_column(Integer)
    losing_trades: Mapped[int | None] = mapped_column(Integer)
    net_pnl: Mapped[float | None] = mapped_column(Float)
    gross_pnl: Mapped[float | None] = mapped_column(Float)
    total_charges: Mapped[float | None] = mapped_column(Float)
    missed_trades: Mapped[int | None] = mapped_column(Integer)
    missed_theoretical_pnl: Mapped[float | None] = mapped_column(Float)
    auto_locks: Mapped[int | None] = mapped_column(Integer)
    manual_unlocks: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class LevelsLog(Base):
    __tablename__ = "levels_log"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    index_name: Mapped[str] = mapped_column(String, nullable=False)
    timeframe: Mapped[str] = mapped_column(String, nullable=False)
    level_type: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    triggered_at: Mapped[str | None] = mapped_column(DateTime)
    trade_id: Mapped[str | None] = mapped_column(String)
