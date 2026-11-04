# Production Runbook

## Preconditions
1. Choose a cloud host supporting Docker Compose or equivalent long-running containers.
2. Provision persistent PostgreSQL storage and encrypted backups.
3. Configure HTTPS/TLS and a domain/reverse proxy for the frontend.
4. Set strong database password, database URL, long random API token, dashboard password, session secret, trusted CORS origin and paper cost assumptions in the host secret manager.
5. Never store credentials in Git, browser storage, Android app code or chat.
6. Keep API and database private to the deployment network. Expose only HTTPS frontend and required health probes.

## Container images
Run the GitHub Actions workflow "Publish container images" manually or push a version tag. It publishes backend and frontend images to GitHub Container Registry. Set BACKEND_IMAGE and FRONTEND_IMAGE to published immutable SHA tags in production.

## Start services
On the cloud host, set required environment variables and run:
docker compose -f docker-compose.production.yml up -d

After confirming database and API health, enable workers only when symbol allowlist and exchange connectivity are ready:
docker compose -f docker-compose.production.yml --profile market-data --profile paper up -d

Workers do not run on Android. Paper monitor polls every 15 seconds and acts only on fresh closed one-minute candles.

## Smoke tests
- GET /health returns liveness.
- GET /ready confirms PostgreSQL connectivity.
- Sign in to the dashboard; its server-side proxy then authenticates to the backend.
- Confirm migration head includes 0003_paper_portfolio.
- Verify no live order endpoints exist.
- Verify paper entry is rejected without fresh data, a confirmed bullish candidate, or risk approval.
- Verify stop-loss monitor does nothing when candles are stale.

## Important limits
CoinSwitch public WebSocket has not been verified in a sustained hosted session. Historical REST access needs user-configured API credentials in cloud secret storage. Worker consumes public one-minute stream; historical backfill is not wired into worker startup. Provider terms, symbol availability and fees must be checked before relying on the feed.

Initial paper fee/slippage defaults are illustrative, not verified CoinSwitch fees. Indian VDA taxes are not calculated. Maintain a transaction-level ledger and consult a qualified Indian tax professional before live investing.

## Recovery
Use container health status and logs to identify failures. Restart only affected workers after confirming database readiness. Preserve PostgreSQL volume; never use down -v in production. Back up before migrations or version changes.
