from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.market_data.indicators import ema, rsi, sma
from app.market_data.schemas import OHLCVCandle


def sample_candle(**overrides):
    values = {
        "venue": "test-exchange",
        "symbol": "BTC/USDT",
        "interval": "5m",
        "open_time": datetime(2026, 1, 1, tzinfo=UTC),
        "close_time": datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=5),
        "open": Decimal(100),
        "high": Decimal(110),
        "low": Decimal(95),
        "close": Decimal(105),
        "volume": Decimal("2.5"),
        "is_closed": True,
    }
    values.update(overrides)
    return values


def test_candle_accepts_valid_ohlcv_and_normalises_utc():
    candle = OHLCVCandle(**sample_candle())
    assert candle.symbol == "BTC/USDT"
    assert candle.open_time.utcoffset() == timedelta(0)


def test_candle_rejects_invalid_ohlc():
    with pytest.raises(ValidationError):
        OHLCVCandle(**sample_candle(high=Decimal(101)))


def test_candle_rejects_naive_timestamp():
    with pytest.raises(ValidationError):
        OHLCVCandle(**sample_candle(open_time=datetime(2026, 1, 1)))


def test_sma_and_ema_require_enough_values():
    assert sma([1, 2], 3) is None
    assert sma([1, 2, 3], 2) == 2.5
    assert ema([1, 2, 3], 2) == pytest.approx(2.5)


def test_rsi_flat_and_rising_series():
    assert rsi([10, 10, 10, 10], 3) == 50.0
    assert rsi([1, 2, 3, 4], 3) == 100.0


def test_indicators_reject_non_positive_period():
    with pytest.raises(ValueError):
        sma([1, 2], 0)
