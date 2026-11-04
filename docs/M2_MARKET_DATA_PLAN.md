# M2 — Market Data Intelligence

## Objective
Establish a trustworthy, venue-aware historical and live market-data layer before enabling scanners or signals. No exchange provider has been selected or configured yet.

## Implemented foundation
- Immutable OHLCV candle contract with venue, symbol, interval and UTC timestamps.
- Validation for positive prices, non-negative volume, candle time ordering and OHLC consistency.
- Deterministic SMA, EMA and Wilder RSI primitives.
- API status endpoint that explicitly reports provider-pending and live ingestion disabled.
- Automated tests for candle validation and indicator edge cases.

## Next delivery slices
1. Provider evaluation: India accessibility, API reliability, spot market coverage, WebSocket + REST support, historical depth, rate limits, fees, terms/licensing and uptime.
2. Venue-aware instrument registry and allowlisted spot universe; stablecoins classified as reserve/liquidity assets rather than default directional trades.
3. Historical OHLCV ingestion, deduplication, gap detection, closed-candle handling and provenance.
4. Live WebSocket ingestion with REST reconciliation, reconnect/backfill and stale-feed circuit breaker.
5. Quality monitoring: delayed/out-of-order candles, duplicates, impossible ranges, volume anomalies and venue outages.
6. Persist candles and feed health in PostgreSQL with migrations and retention policy.
7. Only after data quality gates: multi-timeframe feature pipeline and research/backtesting datasets.

## Required safeguards
- Never combine venues or quote currencies silently.
- Never use an unfinished candle as a confirmed close.
- Block downstream signals on stale, missing or invalid data.
- Preserve source, venue, symbol, interval, event time and ingestion time.
- Backtests must account for fees, spread, slippage, liquidity, partial fills and survivorship/look-ahead bias.
- Paper-only; no live order endpoint or exchange trading credential in M2.

## Provider decision gate
Do not hard-code a provider until current documentation, geographic availability, market coverage, historical limits, WebSocket behaviour, rate limits and commercial terms have been checked. CoinSwitch PRO is a candidate for later execution/data evaluation, not an assumed compatible provider.
