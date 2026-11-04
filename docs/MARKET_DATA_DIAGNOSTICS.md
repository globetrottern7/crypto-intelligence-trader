# Market Data Diagnostics

Endpoint: `GET /api/v1/market-data/diagnostics`

The diagnostics endpoint groups persisted closed candles by venue, symbol and interval. It reports row count, latest close timestamp, age and a conservative freshness classification. It returns an empty coverage set when no candles have been persisted.

Freshness thresholds are operational warning thresholds, not trading signals. A stale group must not be used by a strategy. The endpoint deliberately reports worker health as `not_observable_from_candle_rows`: recent database rows do not prove that a worker is connected now, and old rows do not prove why it stopped.

The endpoint does not claim live prices or enable trading. It is intended for the mobile dashboard and cloud operations checks. Database errors return HTTP 503.
