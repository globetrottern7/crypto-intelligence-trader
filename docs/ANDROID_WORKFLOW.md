# Android-first development and usage

## Goal
All project management, review and day-to-day access should be possible from the Android phone. Compute-heavy builds, tests, database and monitoring run in cloud services, not on the handset.

## What runs where
- Android phone: GitHub app/Chrome, dashboard/PWA, notifications and review.
- GitHub: source control, issues, pull requests and CI workflow.
- Cloud development environment (optional): GitHub Codespaces for terminal/editor sessions in a browser.
- Cloud runtime (later milestone): frontend, FastAPI backend, PostgreSQL and background market-data workers.

## Phone-only workflow
1. Open the repository in Chrome or the GitHub app.
2. Review code and commits; use the repository's Actions tab to inspect CI runs.
3. For changes requiring a terminal, open the repository's Code menu and check whether Codespaces is available. If enabled, create a Codespace from `main` and use its browser editor/terminal.
4. Run checks in that cloud environment or let GitHub Actions run them on commits/pull requests.
5. Preview the dashboard using the cloud environment's forwarded port or the deployed preview URL.
6. Install the eventual production PWA from Chrome's browser menu when the hosted application is ready.

## Important constraints
- Android itself is not the build server. Do not expect Docker Compose, PostgreSQL or a continuous market-data worker to run reliably on the phone.
- A PWA installed on Android is the user interface, not the backend host. Market monitoring must continue in cloud infrastructure when the phone is offline.
- Codespaces is optional and account-dependent. If unavailable, use GitHub Actions plus cloud deployment; no PC is required for ordinary review and use.
- Never paste API secrets into chat, source files, screenshots or commits. Store them in the cloud provider's secret manager when integrations are introduced.

## P0 safety boundary
The application remains paper-trading only. No live exchange order execution or leverage is enabled.
