# Crypto Intelligence & Trading Assistant

Personal, learning-first digital-asset intelligence and paper-trading system. **Designed to be developed and used from an Android phone.** No PC, local Docker or local Python setup is required for the intended workflow.

## Android-first development

1. Open the repository in Chrome on Android: https://github.com/globetrottern7/crypto-intelligence-trader
2. In GitHub, open **Code → Codespaces → Create codespace on main** (if Codespaces is enabled for your account).
3. Wait for the cloud workspace to build. First setup installs Python dependencies and frontend packages automatically.
4. In the Codespaces terminal, run:
   `bash scripts/dev-start.sh`
5. Open the forwarded **port 3000** link to use the dashboard on your phone. Port 8000 is the API.
6. Use the **Actions** tab in GitHub to monitor automated tests and builds.

If Codespaces is not available on your account, the repository can still be reviewed from Android and CI can run in GitHub Actions. A cloud deployment will provide the hosted dashboard once configured. Codespaces usage limits and availability depend on your GitHub plan/account.

## Local endpoints inside the cloud workspace

- Dashboard: forwarded port 3000
- API liveness: forwarded port 8000, `/health`
- API readiness: forwarded port 8000, `/ready`
- API docs: forwarded port 8000, `/docs`

The devcontainer includes PostgreSQL and applies Alembic migrations when the development start script runs.

## P0 guardrails

- Intraday universe: 30–50 liquid cryptocurrencies; swing research covers a broader screened universe.
- Stablecoins are liquidity/reserve instruments with separate depeg and issuer-risk monitoring.
- Quantitative calculations and risk controls are deterministic; AI explains but cannot authorise trades.
- Paper trading only. Live exchange order execution and leverage are out of scope for P0.
- No fabricated prices or signals: market data must be connected and validated before scanner output is enabled.

Never commit `.env`, API keys or exchange credentials. Backtests do not guarantee future profitability.
