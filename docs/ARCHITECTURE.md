# Architecture — P0

## Shape
Modular monolith initially: Next.js + TypeScript, Python + FastAPI, PostgreSQL, Docker Compose, GitHub Actions. Avoid Kubernetes/microservices until measured scale requires them. Add Redis or TimescaleDB only after profiling.

## Backend modules
`market_data`, `quantitative`, `historical`, `intraday`, `swing`, `risk`, `backtesting`, `paper_trading`, `portfolio`, `capital_allocation`, `performance`, `ai_mentor`.

## Data principles
Preserve provider/venue and pair identity; store UTC timestamps and provenance; do not mix venues without explicit normalisation; detect missing, duplicate, delayed and abnormal observations; block signals on stale/invalid inputs.

## Decision boundary
Python owns calculations, signal rules, sizing, risk checks and simulated execution. AI consumes structured timestamped evidence to explain and summarise; it cannot authorise or bypass orders.

## Access
Desktop web, responsive mobile web and installable PWA use the same Next.js app and backend. Server-side monitoring continues when clients disconnect.
