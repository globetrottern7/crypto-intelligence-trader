# Crypto Intelligence & Trading Assistant

Personal, learning-first digital-asset intelligence and paper-trading system. The project workflow is designed to be managed from an Android phone; a Windows PC or local Docker Desktop is not a requirement.

## P0 guardrails
- Intraday universe: 30–50 liquid cryptocurrencies; swing research covers a broader screened universe.
- Stablecoins are liquidity/reserve instruments with separate depeg and issuer-risk monitoring.
- Quantitative calculations and risk controls are deterministic; AI explains but cannot authorise trades.
- Paper trading only. Live exchange order execution and leverage are out of scope for P0.
- No fabricated prices or signals: market data must be connected and validated before scanner output is enabled.

## Android-first project workflow
1. Open this repository in Chrome on the Android phone: https://github.com/globetrottern7/crypto-intelligence-trader
2. Use the GitHub mobile app or browser to review commits, files and pull requests.
3. Code changes can be prepared and committed through the connected GitHub workflow; automated checks run in GitHub Actions.
4. If interactive terminal work is needed, use GitHub Codespaces in the browser if it is enabled for the GitHub account. It provides a cloud development environment; it does not require installing Python, Node.js or Docker on the phone.
5. Open forwarded web ports in the phone browser to preview the dashboard/API when a Codespace is running.

GitHub Codespaces availability and usage limits depend on the GitHub account. If it is unavailable, use GitHub Actions for automated builds/tests and a cloud deployment for phone-based preview. Do not install Docker Desktop or run the project locally on Android as a prerequisite.

## Cloud service endpoints (when running)
- Frontend: port 3000
- API liveness: `/health` on port 8000
- API readiness (includes PostgreSQL connectivity): `/ready` on port 8000
- API docs: `/docs` on port 8000

The backend applies Alembic migrations before starting. PostgreSQL data persists in the configured database volume/service. Never commit `.env`, API keys or exchange credentials. Backtests do not guarantee future profitability.
