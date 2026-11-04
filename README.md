# Crypto Intelligence & Trading Assistant

Personal, learning-first digital-asset intelligence and paper-trading system. Designed to be developed and used from an Android phone. No PC, local Docker or local Python setup is required for the intended workflow.

## Android-first development

1. Open the repository in Chrome on Android: https://github.com/globetrottern7/crypto-intelligence-trader
2. In GitHub, open Code → Codespaces → Create codespace on main if Codespaces is enabled for your account.
3. Use the cloud workspace terminal/editor for code work; use GitHub Actions for automated validation.
4. Open the forwarded frontend port to use the dashboard on your phone. The backend runs in the cloud workspace or deployed cloud host.
5. Use the GitHub Actions tab to monitor tests and container publishing.

If Codespaces is unavailable, the repository can still be reviewed from Android and CI can run in GitHub Actions. A separate cloud host is required for continuous market ingestion and monitoring. Codespaces availability and usage limits depend on your GitHub account.

## Delivered application foundations

- M2: CoinSwitch spot market-data adapters, candle validation, aggregation, ingestion worker and coverage diagnostics.
- M3: SMA, EMA, RSI, MACD, ATR, VWAP and regime analysis.
- M4: Independent intraday (5m/15m) and swing (4h/1d) scanners.
- M5: Long-only SMA crossover backtesting with fees and slippage.
- M6: Persistent INR paper ledger, fee/slippage simulation and stop-loss monitor.
- M7: Deterministic risk guardian with per-trade, daily, weekly, position-count and asset-exposure limits.
- M8: Explain-only mentor layer; optional LLM integration is not enabled.
- M9: Responsive Android-first dashboard with password-protected server-side API proxy.
- M10: Production Compose file, API bearer-token protection and GHCR publishing workflow.

See docs/M3_M10_DELIVERY.md and docs/PRODUCTION_RUNBOOK.md.

## Key endpoints

/health; /ready; /api/v1/system/status; /api/v1/market-data/status; /api/v1/market-data/diagnostics; /api/v1/intelligence/analyse; /api/v1/intelligence/scan; /api/v1/intelligence/backtest; /api/v1/paper/portfolio; /api/v1/paper/trades; /api/v1/paper/trades/open; /api/v1/paper/trades/close; /api/v1/paper/monitor.

## Safety

Paper trading only. No live exchange order execution, leverage or futures. Risk controls are deterministic; AI explanations cannot override them. No fabricated prices or signals: a scanner must have validated, fresh, complete candles. Backtests do not guarantee future profitability. Fees/slippage defaults are illustrative, not verified venue fees. Tax calculations are not included.

Never commit .env, API keys or exchange credentials. Production API routes require a server-side bearer token and dashboard login. Keep PostgreSQL private and use persistent storage/backups.
