from collections import deque
from datetime import UTC, datetime, timedelta
from typing import Callable

from sqlalchemy.orm import Session

from app.market_data.aggregator import MINUTES_PER_INTERVAL, aggregate_closed_minutes
from app.market_data.quality import candle_is_fresh
from app.market_data.repository import store_candles
from app.market_data.schemas import CandleInterval, OHLCVCandle


def _interval_boundary(close_time: datetime, interval: CandleInterval) -> bool:
    if interval == CandleInterval.M5:
        return close_time.minute % 5 == 0
    if interval == CandleInterval.M15:
        return close_time.minute % 15 == 0
    if interval == CandleInterval.H1:
        return close_time.minute == 0
    if interval == CandleInterval.H4:
        return close_time.minute == 0 and close_time.hour % 4 == 0
    if interval == CandleInterval.D1:
        return close_time.hour == 0 and close_time.minute == 0
    if interval == CandleInterval.W1:
        return close_time.weekday() == 0 and close_time.hour == 0 and close_time.minute == 0
    return False


class MarketDataIngestionService:
    """Validate, deduplicate, persist and aggregate closed one-minute candles."""

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory
        self.buffers: dict[tuple[str, str], deque[OHLCVCandle]] = {}
        self.stats = {"received": 0, "stored": 0, "stale": 0, "duplicates": 0}

    def handle(self, candle: OHLCVCandle, *, now: datetime | None = None) -> bool:
        self.stats["received"] += 1
        if candle.interval != CandleInterval.M1 or not candle.is_closed:
            return False
        if not candle_is_fresh(candle, now=now, max_delay=timedelta(minutes=2)):
            self.stats["stale"] += 1
            return False

        key = (candle.venue, candle.symbol)
        buffer = self.buffers.setdefault(
            key, deque(maxlen=MINUTES_PER_INTERVAL[CandleInterval.W1])
        )
        if buffer and candle.open_time <= buffer[-1].open_time:
            self.stats["duplicates"] += 1
            return False
        buffer.append(candle)

        derived = []
        for interval in MINUTES_PER_INTERVAL:
            if _interval_boundary(candle.close_time, interval):
                completed = aggregate_closed_minutes(list(buffer), interval)
                if completed:
                    derived.append(completed[-1])

        with self.session_factory() as session:
            self.stats["stored"] += store_candles(session, [candle, *derived])
            session.commit()
        return True
