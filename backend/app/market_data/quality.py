from datetime import UTC, datetime, timedelta

from app.market_data.schemas import OHLCVCandle


def candle_is_fresh(
    candle: OHLCVCandle,
    *,
    now: datetime | None = None,
    max_delay: timedelta = timedelta(minutes=2),
) -> bool:
    """A candle is usable only if closed and within the configured arrival delay."""
    current = now or datetime.now(UTC)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if not candle.is_closed:
        return False
    age = current.astimezone(UTC) - candle.close_time
    return timedelta(0) <= age <= max_delay
