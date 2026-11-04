# Database Schema Plan

## Foundation
`assets`, `asset_categories`, `exchanges`, `trading_pairs`, `data_sources`, `market_candles`, `system_settings`, `users`, `audit_logs`.

## Later trading migrations
`market_indicators`, `market_regimes`, `historical_patterns`, `strategy_definitions`, `backtest_runs`, `opportunity_signals`, `paper_orders`, `paper_fills`, `paper_positions`, `trade_ledger`, `trading_costs`, `portfolio_wallets`, `capital_allocations`, `performance_metrics`, `prediction_records`, `risk_events`, `ai_analysis_logs`.

## Accounting
Use immutable transaction/ledger records. Store prices and quantities using fixed-precision decimal types, not binary floats. Preserve fee currency, fee amount, tax metadata, source timestamps and execution assumptions. Wallet transfers must balance.
