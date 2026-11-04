# Market Data Provider Evaluation — November 2026

## Decision
Primary India spot-data candidate: CoinSwitch PRO. Its official API documents INR and USDT spot markets, historical OHLCV REST candles and an unauthenticated public 1-minute Socket.IO candlestick stream. This is a read-only data-provider decision, not approval for live execution.

Secondary global reference: Binance public market-data endpoints, conditional on validating cloud-region reachability and permitted use. Preserve it as a separate venue feed; never silently merge prices.

Supporting context: CoinGecko Demo for asset metadata and broad market discovery. Do not subscribe to a paid plan until actual request volumes and historical-depth needs are measured.

## CoinSwitch evidence
- Historical REST: GET /trade/api/v2/candles; required fields are exchange, BASE/QUOTE symbol, interval in minutes, start_time and end_time (Unix milliseconds).
- REST response fields: o, h, l, c, volume, symbol, interval, start_time and close_time.
- Public spot WebSocket: Socket.IO v4 at wss://ws.coinswitch.co/, namespace /coinswitchx, path /pro/realtime-rates-socket/spot, event FETCH_CANDLESTICK_CS_PRO.
- WebSocket symbols use BASE,QUOTE; REST symbols use BASE/QUOTE.
- WebSocket emits 1-minute candle updates around close, with o/h/l/c, volume, end_time, symbol and interval.
- Authenticated REST uses Ed25519; store credentials in cloud environment secrets only.
- Handle HTTP 429 with backoff.

Official documentation:
- https://api-trading.coinswitch.co/spot/reference/candles
- https://api-trading.coinswitch.co/spot/websockets/connection
- https://api-trading.coinswitch.co/spot/websockets/candlestick
- https://api-trading.coinswitch.co/resources/reference-client
- https://api-trading.coinswitch.co/resources/errors-and-rate-limits

## Integration decision
CoinSwitch is the first adapter because the user already has a CoinSwitch account and official docs cover historical and live spot data. Public candle WebSocket does not require credentials; historical REST requires the API key pair. Never share secrets in chat or commit them.
