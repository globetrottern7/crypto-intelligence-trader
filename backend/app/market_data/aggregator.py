# ruff: noqa: I001
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from app.market_data.schemas import CandleInterval, OHLCVCandle


MINUTES_PER_INTERVAL = {
    CandleInterval.M5: 5,
    CandleInterval.M15: 15,
    CandleInterval.H1: 60,
    CandleInterval.H4: 240,
    CandleInterval.D1: 1440,
    CandleInterval.W1: 10080,
}


def _bucket_start(value: datetime, interval: CandleInterval) -> datetime:
    value = value.astimezone(UTC)
    if interval == CandleInterval.W1:
        return datetime(value.year, value.month, value.day, tzinfo=UTC) - timedelta(
            days=value.weekday()
        )
    minutes = MINUTES_PER_INTERVAL[interval]
    epoch_minutes = int(value.timestamp() // 60)
    return datetime.fromtimestamp((epoch_minutes // minutes) * minutes * 60, tz=UTC)


def aggregate_closed_minutes(
    candles: list[OHLCVCandle], target: CandleInterval
) -> list[OHLCVCandle]:
    """Build only complete target candles from contiguous, closed 1-minute candles."""
    if target not in MINUTES_PER_INTERVAL:
        raise ValueError("target must be a supported interval above one minute")
    if any(c.interval != CandleInterval.M1 for c in candles):
        raise ValueError("aggregation input must contain 1-minute candles")
    groups = defaultdict(list)
    for candle in candles:
        groups[(candle.venue, candle.symbol, _bucket_start(candle.open_time, target))].append(
            candle
        )

    expected = MINUTES_PER_INTERVAL[target]
    result = []
    for (venue, symbol, bucket), group in sorted(groups.items(), key=lambda item: item[0][2]):
        group.sort(key=lambda candle: candle.open_time)
        if len(group) != expected or not all(candle.is_closed for candle in group):
            continue
        if any(
            current.open_time - previous.open_time != timedelta(minutes=1)
            for previous, current in pairwise(group)
        ):
            continue
        if group[0].open_time != bucket:
            continue
        result.append(
            OHLCVCandle(
                venue=venue,
                symbol=symbol,
                interval=target,
                open_time=group[0].open_time,
                close_time=group[-1].close_time,
                open=group[0].open,
                high=max(c.high for c in group),
                low=min(c.low for c in group),
                close=group[-1].close,
                volume=sum((c.volume for c in group), start=group[0].volume * 0),
                is_closed=True,
            )
        )
    return result
