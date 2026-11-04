from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.market_data.schemas import CandleInterval, OHLCVCandle
from app.quant.analysis import analyse_candles
from app.quant.backtesting import run_sma_crossover_backtest
from app.quant.indicators import atr, ema, macd, rsi, sma, vwap
from app.risk.guardian import evaluate_long_entry


def candle(index, price):
    start = datetime.now(UTC) - timedelta(minutes=200 - index)
    return OHLCVCandle(
        venue="test", symbol="BTC/INR", interval=CandleInterval.M1,
        open_time=start, close_time=start + timedelta(minutes=1),
        open=Decimal(str(price)), high=Decimal(str(price + 1)),
        low=Decimal(str(price - 1)), close=Decimal(str(price)),
        volume=Decimal(2), is_closed=True,
    )


def test_indicator_primitives_have_expected_shapes():
    values = [float(x) for x in range(1, 61)]
    assert ema(values, 20)[18] is None
    assert ema(values, 20)[19] is not None
    assert sma(values, 5)[3] is None
    assert sma(values, 5)[4] == 3
    assert rsi(values, 14)[-1] == 100
    line, signal, histogram = macd(values)
    assert len(line) == len(signal) == len(histogram) == len(values)
    assert atr(values, values, values)[-1] is not None
    assert vwap(values, values, values, values)[-1] is not None


def test_risk_guardian_blocks_stale_and_oversized_positions():
    common = {
        "equity": 5000, "price": 100, "stop_loss": 98, "requested_quantity": 11,
        "daily_loss_fraction": 0, "weekly_loss_fraction": 0, "open_positions": 0,
        "asset_exposure": 0, "regime": "bullish", "data_fresh": True,
    }
    assert not evaluate_long_entry(**{**common, "data_fresh": False}).approved
    assert not evaluate_long_entry(**common).approved


def test_risk_guardian_approves_within_limits():
    result = evaluate_long_entry(
        equity=5000, price=100, stop_loss=99, requested_quantity=10,
        daily_loss_fraction=0, weekly_loss_fraction=0, open_positions=0,
        asset_exposure=0, regime="bullish", data_fresh=True,
    )
    assert result.approved


def test_analysis_returns_no_trade_for_insufficient_history():
    result = analyse_candles([candle(i, 100 + i) for i in range(10)])
    assert result["recommendation"] == "no_trade"


def test_analysis_stale_data_is_never_actionable():
    old = datetime(2020, 1, 1, tzinfo=UTC)
    rows = []
    for i in range(60):
        start = old + timedelta(minutes=i)
        price = Decimal(100 + i)
        rows.append(OHLCVCandle(
            venue="test", symbol="BTC/INR", interval=CandleInterval.M1,
            open_time=start, close_time=start + timedelta(minutes=1),
            open=price, high=price + 1, low=price - 1, close=price,
            volume=Decimal(2), is_closed=True,
        ))
    result = analyse_candles(rows)
    assert result["recommendation"] == "no_trade"
    assert result["status"] == "stale_data"


def test_backtest_accounts_for_fees_and_slippage():
    prices = [100 + (i if i < 30 else 60 - i) for i in range(80)]
    rows = [candle(i, p) for i, p in enumerate(prices)]
    result = run_sma_crossover_backtest(
        rows, fast_period=3, slow_period=8, initial_capital=5000,
        fee_bps=10, slippage_bps=10,
    )
    assert result["trade_count"] >= 1
    assert result["total_fees"] > 0
    assert "limitations" in result
    with pytest.raises(ValueError):
        run_sma_crossover_backtest(rows[:5], fast_period=3, slow_period=8)
