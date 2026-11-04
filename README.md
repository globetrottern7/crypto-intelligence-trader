# Crypto Intelligence & Trading Assistant

Personal, learning-first digital-asset intelligence and paper-trading system.

## P0 guardrails
- Intraday universe: 30–50 liquid cryptocurrencies; swing research covers a broader screened universe.
- Stablecoins are liquidity/reserve instruments with separate depeg and issuer-risk monitoring.
- Quantitative calculations and risk controls are deterministic; AI explains but cannot authorise trades.
- Paper trading only. Live exchange order execution and leverage are out of scope for P0.
- No fabricated prices or signals: market data must be connected and validated before scanner output is enabled.

## Local setup
Prerequisites: Docker Desktop with Compose, Node.js 20+ (for non-Docker frontend development), Python 3.11+.

1. Copy `.env.example` to `.env` and change the local database password.
2. Run `docker compose up --build` from the repository root.
3. Website: http://localhost:3000
4. API liveness: http://localhost:8000/health
5. API readiness (includes PostgreSQL connectivity): http://localhost:8000/ready
6. API docs: http://localhost:8000/docs

The backend applies Alembic migrations before starting. PostgreSQL data persists in the `postgres_data` Docker volume. To stop services use `docker compose down`; to remove local database data as well, use `docker compose down -v`.

Never commit `.env`, API keys or exchange credentials. Backtests do not guarantee future profitability.
