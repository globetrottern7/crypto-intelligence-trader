# Cloud Runtime — Market Data Worker

The Android device is the control surface. Keep the API, PostgreSQL and worker in a hosted runtime; do not run persistent workers on Android.

## Required environment
- DATABASE_URL: PostgreSQL connection string for the hosted database.
- POSTGRES_PASSWORD: strong database password (never the example value).
- MARKET_DATA_SYMBOLS: explicit comma-separated spot-pair allowlist, such as BTC/INR,ETH/INR.
- COINSWITCH_API_KEY and COINSWITCH_SECRET_KEY: only if historical REST backfill is enabled later. The current public WebSocket worker does not need them.

## Start
The Compose worker is opt-in under the market-data profile. Once the backend and database are healthy, start it with:

docker compose --profile market-data up -d --build

The worker waits for the API health check, connects to CoinSwitch's public Socket.IO spot namespace, subscribes to the configured symbols and writes closed one-minute candles plus complete derived intervals to PostgreSQL.

## Operational checks
- GET /health confirms API process liveness.
- GET /ready confirms PostgreSQL connectivity.
- GET /api/v1/market-data/status reports implemented adapters but does not claim a live feed.
- Inspect worker logs for connection, reconnect and subscription failures.
- Monitor market_candles for recent close_time values and venue/pair/interval identity.
- If the feed is stale, stop downstream signals; never substitute guessed or cached prices.

## Not yet done
No cloud project, database, domain, deployment secrets or CoinSwitch API keys have been configured. A successful CI run is not evidence of live exchange connectivity. Run a controlled cloud smoke test before enabling any strategy research based on the live feed.
