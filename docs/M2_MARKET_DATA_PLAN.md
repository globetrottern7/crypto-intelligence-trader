# M2 — Market Data Intelligence

## Implemented
- Venue-aware OHLCV candle schema with UTC normalisation and OHLC validation.
- Deterministic SMA, EMA and Wilder RSI primitives.
- CoinSwitch PRO signed historical spot-candle REST client (read-only).
- CoinSwitch public 1-minute Socket.IO candle stream adapter (read-only).
- Complete-minute aggregation into 5m, 15m, 1h, 4h, 1d and 1w candles; incomplete groups are discarded.
- Candle freshness, duplicate and out-of-order gates.
- PostgreSQL market-candle model and Alembic migration with venue/symbol/interval/open-time uniqueness.
- Idempotent persistence repository.
- Ingestion service and opt-in Docker Compose worker profile.
- Tests for signatures, REST payloads, stream parsing, aggregation, freshness, idempotent persistence and ingestion.

## Provider decision
CoinSwitch PRO is the primary India spot-data adapter because its official documentation describes historical OHLCV REST candles and an unauthenticated public 1-minute Socket.IO stream. REST symbols use BASE/QUOTE; WebSocket symbols use BASE,QUOTE. Binance remains a separate optional global reference venue; CoinGecko is supporting asset metadata/context only.

## Starting the worker in a hosted Docker runtime
1. Deploy PostgreSQL and the API backend first; the backend applies Alembic migrations before serving.
2. Set a strong database password and a comma-separated allowlist in MARKET_DATA_SYMBOLS, for example BTC/INR,ETH/INR.
3. Start the opt-in worker profile with: docker compose --profile market-data up -d --build.
4. Check /api/v1/market-data/status and inspect worker logs for Socket.IO connection and subscription messages.

The public candle stream does not require CoinSwitch API credentials. The historical REST adapter does; store the API key and private secret in the cloud secret manager only. Never place secrets in source, chat or the PWA.

## Runtime status and remaining verification
The adapter, worker, aggregation, persistence and CI integration tests are implemented. GitHub Actions validates the frontend, backend, PostgreSQL migration and /ready probe. Actual external CoinSwitch connectivity, a sustained cloud worker session and live historical REST access have not been verified because no CoinSwitch credentials or cloud runtime have been configured. Do not describe the feed as live until those runtime checks pass.

## Safety gates
- Only closed one-minute candles are persisted and aggregated.
- Missing-minute or non-contiguous groups are not emitted as complete aggregate candles.
- Preserve venue, pair and source timestamps.
- Do not average or silently merge prices across venues.
- Stale, future-dated, duplicate or out-of-order stream data is rejected.
- No exchange order methods, live execution, futures or leverage are included.
