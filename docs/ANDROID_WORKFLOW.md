# Android-first development and usage

## Goal
The project is designed to be created, developed, reviewed and used from an Android phone. Compute-heavy builds, tests, database and monitoring run in cloud services, not on the handset.

## Start a cloud development workspace from Android
1. Open the repository in Chrome: https://github.com/globetrottern7/crypto-intelligence-trader
2. Open **Code → Codespaces → Create codespace on main**. If the Codespaces option is missing, check GitHub account availability/billing; do not install a local toolchain as a workaround.
3. Wait for the cloud workspace to initialise. The devcontainer installs backend and frontend dependencies and starts PostgreSQL.
4. Open the integrated terminal and run `bash scripts/dev-start.sh`.
5. In the Codespaces **Ports** panel, open port **3000** in the browser to use the dashboard on the phone. Port **8000** exposes the API for diagnostics.
6. Keep the Codespace running while developing. Stop it from the Codespaces menu when finished to avoid consuming usage time.

## What runs where
- Android phone: Chrome/GitHub app, browser editor/terminal, dashboard/PWA and review.
- GitHub: source control, issues, pull requests and CI.
- Codespaces: temporary cloud development machine and PostgreSQL container.
- Production cloud runtime (later milestone): always-on frontend, API, PostgreSQL and market-data workers.

## Important constraints
- Android is the control centre and interface, not the build server.
- A PWA is only the user interface; continuous market monitoring must run in cloud infrastructure even when the phone is offline.
- Codespaces availability, included usage and billing depend on the GitHub account. Stop unused Codespaces.
- If Codespaces is unavailable, CI and cloud deployment can still be used; do not assume the user has a PC.
- Never paste API secrets into chat, source files, screenshots or commits. Store secrets in the cloud provider's secret manager when integrations are introduced.

## P0 safety boundary
Paper trading only. No live exchange order execution or leverage is enabled.
