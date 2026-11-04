from sqlalchemy.orm import Session

from app.db.models import MarketCandle
from app.market_data.schemas import OHLCVCandle


def store_candles(session: Session, candles: list[OHLCVCandle]) -> int:
    """Idempotently insert/update venue-scoped candles; caller owns transaction commit."""
    for candle in candles:
        session.merge(
            MarketCandle(
                venue=candle.venue,
                symbol=candle.symbol,
                interval=candle.interval.value,
                open_time=candle.open_time,
                close_time=candle.close_time,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                is_closed=candle.is_closed,
            )
        )
    session.flush()
    return len(candles)
