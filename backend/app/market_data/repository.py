from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MarketCandle
from app.market_data.schemas import OHLCVCandle


def store_candles(session: Session, candles: list[OHLCVCandle]) -> int:
    """Idempotently insert/update venue-scoped candles; caller owns transaction commit."""
    for candle in candles:
        identity = (
            MarketCandle.venue == candle.venue,
            MarketCandle.symbol == candle.symbol,
            MarketCandle.interval == candle.interval.value,
            MarketCandle.open_time == candle.open_time,
        )
        record = session.scalar(select(MarketCandle).where(*identity))
        if record is None:
            record = MarketCandle(
                venue=candle.venue, symbol=candle.symbol, interval=candle.interval.value,
                open_time=candle.open_time, close_time=candle.close_time,
                open=candle.open, high=candle.high, low=candle.low, close=candle.close,
                volume=candle.volume, is_closed=candle.is_closed,
            )
            session.add(record)
        else:
            record.close_time = candle.close_time
            record.open = candle.open
            record.high = candle.high
            record.low = candle.low
            record.close = candle.close
            record.volume = candle.volume
            record.is_closed = candle.is_closed
    session.flush()
    return len(candles)
