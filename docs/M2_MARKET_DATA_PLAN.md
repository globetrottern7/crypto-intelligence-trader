# M2 — Market Data Intelligence

## Implemented
- Venue-aware OHLCV candle schema with UTC normalisation and OHLC validation.
- Deterministic SMA, EMA and Wilder RSI primitives.
- CoinSwitch PRO signed historical spot-candle REST client (read-only).
- CoinSwitch public 1-minute Socket.IO candle stream adapter (read-only).
- Complete-minute aggregation into 5m, 15m, 1h, 4h, 1d and 1w candles; incomplete groups are discarded.
- Candle freshness gate.
- PostgreSQL market-candle model and Alembic migration with venue/symbol/interval/open-time uniqueness.
- Idempotent repository persistence through SQLAlchemy merge.
- Tests for signatures, payload normalisation, aggregation, freshness and invalid stream events.

## Provider evidence
CoinSwitch official Spot REST candles use exchange, BASE/QUOTE symbol, interval in minutes, start_time and end_time. Responses contain OHLCV plus start_time and close_time. The public Socket.IO v4 stream emits one-minute candles using FETCH_CANDLESTICK_CS_PRO and BASE,QUOTE symbols. Historical REST uses Ed25519 signing. See docs/PROVIDER_EVALUATION.md.

## Runtime status
Adapters and persistence are implemented, but no cloud worker is running yet. No API credentials have been configured, and no live market data is claimed. The stream adapter is opt-in and does not start automatically. Runtime connectivity, actual provider responses and PostgreSQL writes must be verified in cloud before production readiness.

## Safety gates
- Only closed candles enter aggregation.
- Missing-minute or non-contiguous groups are not emitted as complete aggregate candles.
- Preserve venue, pair and source timestamps.
- Do not average or silently merge prices across venues.
- Stale, future-dated or invalid data blocks downstream signals.
- No exchange order methods, live execution, futures or leverage in this milestone.
