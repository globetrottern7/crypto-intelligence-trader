from collections.abc import Sequence

from app.market_data.schemas import OHLCVCandle
from app.quant.indicators import sma


def run_sma_crossover_backtest(
    candles: Sequence[OHLCVCandle], *, fast_period: int = 10, slow_period: int = 30,
    initial_capital: float = 5_000, fee_bps: float = 10, slippage_bps: float = 10
) -> dict:
    if fast_period < 2 or slow_period <= fast_period:
        raise ValueError("Require 2 <= fast_period < slow_period")
    if initial_capital <= 0 or fee_bps < 0 or slippage_bps < 0:
        raise ValueError("Capital must be positive and costs cannot be negative")
    ordered = sorted(candles, key=lambda item: item.open_time)
    if len(ordered) <= slow_period + 1:
        raise ValueError("Not enough candles for the selected periods")
    if any(not item.is_closed for item in ordered):
        raise ValueError("Backtest accepts closed candles only")
    closes = [float(item.close) for item in ordered]
    opens = [float(item.open) for item in ordered]
    fast = sma(closes, fast_period)
    slow = sma(closes, slow_period)
    cash = initial_capital
    position = 0.0
    entry_price = 0.0
    entry_fee = 0.0
    trades = []
    equity_curve = [initial_capital]
    fee_rate = fee_bps / 10_000
    slippage_rate = slippage_bps / 10_000
    for index in range(slow_period, len(ordered) - 1):
        previous_up = fast[index - 1] is not None and slow[index - 1] is not None and fast[index - 1] <= slow[index - 1]
        current_up = fast[index] is not None and slow[index] is not None and fast[index] > slow[index]
        previous_down = fast[index - 1] is not None and slow[index - 1] is not None and fast[index - 1] >= slow[index - 1]
        current_down = fast[index] is not None and slow[index] is not None and fast[index] < slow[index]
        execution = opens[index + 1]
        if position == 0 and previous_up and current_up:
            entry_price = execution * (1 + slippage_rate)
            position = cash / (entry_price * (1 + fee_rate))
            entry_fee = position * entry_price * fee_rate
            cash = 0.0
            entry_time = ordered[index + 1].open_time.isoformat()
        elif position > 0 and previous_down and current_down:
            exit_price = execution * (1 - slippage_rate)
            gross = (exit_price - entry_price) * position
            exit_fee = exit_price * position * fee_rate
            net = gross - entry_fee - exit_fee
            cash = position * exit_price - exit_fee
            trades.append({
                "entry_time": entry_time, "exit_time": ordered[index + 1].open_time.isoformat(),
                "entry_price": entry_price, "exit_price": exit_price, "quantity": position,
                "gross_pnl": gross, "fees": entry_fee + exit_fee, "net_pnl": net,
            })
            position = 0.0
            entry_fee = 0.0
        equity_curve.append(cash + position * closes[index])
    if position > 0:
        exit_price = closes[-1] * (1 - slippage_rate)
        exit_fee = exit_price * position * fee_rate
        gross = (exit_price - entry_price) * position
        net = gross - entry_fee - exit_fee
        cash = position * exit_price - exit_fee
        trades.append({
            "entry_time": entry_time, "exit_time": ordered[-1].close_time.isoformat(),
            "entry_price": entry_price, "exit_price": exit_price, "quantity": position,
            "gross_pnl": gross, "fees": entry_fee + exit_fee, "net_pnl": net,
        })
    final_equity = cash
    peak = initial_capital
    max_drawdown = 0.0
    for value in [*equity_curve, final_equity]:
        peak = max(peak, value)
        if peak:
            max_drawdown = max(max_drawdown, (peak - value) / peak)
    wins = sum(1 for trade in trades if trade["net_pnl"] > 0)
    total_fees = sum(trade["fees"] for trade in trades)
    return {
        "strategy": "long_only_sma_crossover", "fast_period": fast_period, "slow_period": slow_period,
        "initial_capital": round(initial_capital, 2), "final_equity": round(final_equity, 2),
        "net_pnl": round(final_equity - initial_capital, 2),
        "return_percent": round((final_equity / initial_capital - 1) * 100, 4),
        "max_drawdown_percent": round(max_drawdown * 100, 4), "trade_count": len(trades),
        "win_rate_percent": round(wins / len(trades) * 100, 2) if trades else 0.0,
        "total_fees": round(total_fees, 2), "fee_bps_per_side": fee_bps,
        "slippage_bps_per_side": slippage_bps, "trades": trades,
        "limitations": [
            "Educational simulation, not a prediction.",
            "Signals execute at the next candle open to reduce look-ahead bias.",
            "No partial fills, market impact, exchange outages or tax treatment are modelled.",
            "Use out-of-sample and walk-forward validation before relying on results.",
        ],
    }
