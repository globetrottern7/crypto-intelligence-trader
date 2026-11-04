# P0 Trading Guardrails

1. Paper trading only; no live order endpoint or exchange credential is enabled.
2. Intraday and swing are independent strategy contexts.
3. Intraday starts with 5m signals and 15m trend context; swing uses 4h, daily and weekly context.
4. Stablecoins are liquidity/reserve assets, not presumed appreciation trades.
5. No trade is a valid outcome.
6. Size positions from risk budget, entry, stop distance, costs and available capital.
7. Stops do not guarantee execution price; model gaps and slippage.
8. Evaluate correlated positions for aggregate exposure.
9. Block entries when data is stale, inputs are missing or risk limits are breached.
10. Backtests must avoid look-ahead bias and separate training, validation and out-of-sample periods.
11. Transaction-level records must support tax review; daily aggregate net profit is not a tax calculation.
