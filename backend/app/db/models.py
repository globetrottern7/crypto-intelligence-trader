from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True,
    )


class MarketCandle(Base):
    __tablename__ = "market_candles"
    __table_args__ = (
        UniqueConstraint("venue", "symbol", "interval", "open_time",
                         name="uq_market_candle_identity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venue: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    interval: Mapped[str] = mapped_column(String(8), nullable=False)
    open_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    close_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC),
    )
