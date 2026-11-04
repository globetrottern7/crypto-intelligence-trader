# Market Data Provider Evaluation — November 2026

## Decision

**Primary India venue adapter: CoinSwitch PRO Spot (read-only integration first).** It is the best initial candidate because the user already has a CoinSwitch account, the official API documents INR/USDT spot pairs, historical OHLCV candles and public real-time spot WebSockets. This is a provider selection for market-data research only; it is not approval for live trading or order execution.

**Independent global reference: Binance public market-data endpoints, conditionally.** Its official documentation describes unauthenticated market-data-only REST and WebSocket endpoints. Treat this as a separate venue feed, never silently merge its prices with CoinSwitch prices, and verify reachability and permitted use from the actual cloud deployment region before relying on it.

**Market context: CoinGecko Demo initially.** Use for asset metadata, broad market context and cross-exchange aggregated reference prices—not as the execution venue's candle source. The Demo plan is limited for intraday historical research.

## Evidence and trade-offs

### CoinSwitch PRO Spot
- Official REST candles endpoint: `GET /trade/api/v2/candles`, with exchange, BASE/QUOTE symbol, interval in minutes and millisecond start/end timestamps.
- Official REST documentation provides 1, 5, 60 and 1440 minute examples and returns OHLCV with start/close times.
- Public Spot WebSocket uses Socket.IO v4; unauthenticated public market streams are documented.
- Candlestick WebSocket emits 1-minute candles roughly at candle close; REST is the documented route for arbitrary intervals and historical ranges.
- WebSocket symbols use `BASE,QUOTE`; REST uses `BASE/QUOTE`.
- The candles REST page demonstrates the signed-request flow. Authenticated REST uses Ed25519; keep API credentials only in cloud environment secrets.
- Public market-data endpoints have a global per-key fair-use limit rather than a published per-endpoint limit; respect 429 and exponential backoff.
- Initial adapter is read-only and contains no order placement methods.

### Binance public market data
- Official market-data-only REST domain exposes klines, depth, trades, exchange info and ticker endpoints without API authentication.
- Official market-data-only WebSocket domain is `data-stream.binance.vision`.
- WebSocket connections are limited to 24 hours and must reconnect; official docs describe ping/pong and stream limits.
- It is a global reference venue feed, not assumed to be available as an Indian execution venue. Verify connectivity and current legal/terms considerations before production use.

### CoinGecko
- Demo: 10,000 monthly calls and 100 calls/minute; attribution required.
- Basic is currently listed at USD 35/month billed monthly or USD 29/month billed annually; 100k calls/month and WebSocket support. Do not subscribe yet.
- CoinGecko's current plan comparison lists 5-minute history only for one day on Demo/Basic/Analyst/Lite/Pro, with long-range 5-minute history reserved for Enterprise. Daily/hourly history is more broadly available by plan.
- Useful for independent cross-market context, metadata and asset discovery; not sufficient as the only long-history intraday backtest dataset at the free tier.

## M2 integration order
1. Validate CoinSwitch PRO API access and allowed spot pairs from cloud runtime; do not send credentials through ChatGPT or commit them.
2. Test signed historical candles for BTC/INR and BTC/USDT with a small bounded range.
3. Compare returned candle count, timestamp boundaries, duplicate/gap behaviour and OHLCV consistency against the schema.
4. Connect public 1-minute Socket.IO candles and implement reconnect, heartbeat, duplicate suppression and REST reconciliation.
5. Build derived 5m/15m/1h/4h/1d/1w candles from closed 1m data, preserving source provenance. Use REST backfill for gaps.
6. Add Binance as a distinct global reference venue after cloud-region connectivity validation.
7. Add CoinGecko metadata/context only if the free-tier limits and attribution terms fit.

## Explicit gates
- No strategy signals until source freshness, candle completeness, symbol mapping and venue provenance pass validation.
- No price averaging across venues unless a separate, explicit aggregation model is built.
- No live orders, futures, leverage or transfer permissions in this milestone.
- No paid data subscription until a measured request budget demonstrates that free limits are inadequate.
- Never put API keys or secret seeds in source, logs, issue comments or chat.
