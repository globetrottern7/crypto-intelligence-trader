# M3–M10 Delivery

This release adds application-level foundations for M3 through M10. It does not claim that a cloud host, CoinSwitch connection, credentials, or public production domain have been provisioned.

## M3 — Quantitative intelligence
SMA, EMA, Wilder RSI, MACD, ATR and cumulative VWAP. Closed-candle analysis includes interval-specific freshness windows, deterministic scoring and market-regime classification. Insufficient, invalid, stale and high-volatility data return no-trade states.

## M4 — Independent trading engines
Intraday scanner uses 5-minute entry candles and 15-minute trend confirmation. Swing scanner uses 4-hour entry candles and daily trend confirmation. Both timeframes must independently confirm a fresh bullish setup. Maximum 50 assets per scan request. No minimum trade count is imposed.

## M5 — Historical strategy validation
Long-only SMA crossover backtest. Signals are evaluated on closed candles and simulated at the next candle open. Configurable fees and slippage; reports trades, net P&L, win rate and maximum drawdown. No partial fills, market impact, outages or tax treatment. Walk-forward and out-of-sample validation remain mandatory.

## M6 — Paper portfolio
Persistent INR paper account and trade ledger. Long-only entries require 60 recent closed one-minute candles, a fresh confirmed long candidate and risk approval. Entry/exit fees and adverse slippage are applied. Stop-loss monitor is an opt-in worker and ignores stale candles. Default ₹5,000 is virtual seed capital, not a live deposit.

## M7 — Risk Guardian
Defaults: 1% account equity risk per trade, 2% daily loss limit, 5% weekly loss limit, four concurrent positions and 20% per-asset exposure. Requires a protective stop below entry. Rejects stale data, bearish/high-volatility/unknown regimes, oversized orders and insufficient cash. Risk rules are deterministic and cannot be overridden by an explanation.

## M8 — AI Mentor
A deterministic explanation layer reports evidence and caveats and treats no-trade as valid. It is explain-only. No external LLM API call is made in this release; optional model integration requires a server-side secret and evaluation before activation.

## M9 — Android-first dashboard
Responsive web dashboard and server-side API proxy. Displays market data coverage, freshness, paper portfolio, engine descriptions and system capabilities. Android is a client; continuous ingestion and monitoring run in cloud containers, not on the phone.

## M10 — Cloud deployment assets
Production Docker Compose, API bearer-token protection and GHCR image-publishing workflow. GitHub Actions validates backend lint/tests, PostgreSQL migrations/readiness and frontend typecheck/build. Deployment to a real host remains gated on host, DNS/TLS, persistent database, strong secrets and external feed connectivity.

## API
GET /api/v1/market-data/status; GET /api/v1/market-data/diagnostics; POST /api/v1/intelligence/analyse; POST /api/v1/intelligence/scan; POST /api/v1/intelligence/backtest; GET /api/v1/paper/portfolio; GET /api/v1/paper/trades; POST /api/v1/paper/trades/open; POST /api/v1/paper/trades/close; POST /api/v1/paper/monitor.

Production /api/v1 routes require Authorization: Bearer <API_ACCESS_TOKEN>. Health and readiness probes remain available for orchestration. Do not expose the database port publicly.
