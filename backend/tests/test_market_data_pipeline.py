from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.market_data.aggregator import aggregate_closed_minutes
from app.market_data.quality import candle_is_fresh
from app.market_data.schemas import CandleInterval, OHLCVCandle
from app.market_data.stream import parse_coinswitch_minute_candle


def minute_candle(index: int, *, closed: bool = True) -> OHLCVCandle:
    start = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index)
    return OHLCVCandle(
        venue="coinswitchx", symbol="BTC/INR", interval="1m",
        open_time=start, close_time=start + timedelta(minutes=1),
        open=Decimal(100 + index), high=Decimal(110 + index),
        low=Decimal(90 + index), close=Decimal(105 + index),
        volume=Decimal("0.5"), is_closed=closed,
    )


def test_stream_payload_normalises_pair_and_closed_minute():
    candle = parse_coinswitch_minute_candle({
        "o": "100", "h": "105", "l": "99", "c": "103",
        "volume": "2.5", "end_time": "1767225660000",
        "symbol": "BTC,INR", "interval": "1",
    })
    assert candle.symbol == "BTC/INR"
    assert candle.interval == CandleInterval.M1
    assert candle.is_closed is True


def test_stream_rejects_wrong_interval_and_symbol_shape():
    with pytest.raises(ValueError):
        parse_coinswitch_minute_candle({"interval": "5"})
    with pytest.raises(ValueError):
        parse_coinswitch_minute_candle({
            "interval": "1", "symbol": "BTC/INR", "end_time": "1767225660000",
            "o": "1", "h": "1", "l": "1", "c": "1", "volume": "1",
        })


def test_aggregator_creates_only_complete_five_minute_candles():
    result = aggregate_closed_minutes([minute_candle(i) for i in range(5)], CandleInterval.M5)
    assert len(result) == 1
    assert result[0].open == Decimal(100)
    assert result[0].close == Decimal(109)
    assert result[0].high == Decimal(114)
    assert result[0].low == Decimal(90)
    assert result[0].volume == Decimal("2.5")


def test_aggregator_rejects_missing_or_open_minute():
    assert aggregate_closed_minutes(
        [minute_candle(i) for i in [0, 1, 3, 4]], CandleInterval.M5
    ) == []
    assert aggregate_closed_minutes(
        [minute_candle(i, closed=i != 4) for i in range(5)], CandleInterval.M5
    ) == []


def test_stale_or_future_candles_are_not_fresh():
    candle = minute_candle(0)
    now = candle.close_time + timedelta(seconds=30)
    assert candle_is_fresh(candle, now=now)
    assert not candle_is_fresh(candle, now=now + timedelta(minutes=3))
    assert not candle_is_fresh(candle, now=candle.close_time - timedelta(seconds=1))
