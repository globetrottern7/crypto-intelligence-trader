# M1 Acceptance Criteria

- [x] Repository and README present.
- [x] Frontend foundation, responsive layout and PWA manifest committed.
- [x] Backend liveness endpoint and paper-only system status committed.
- [x] PostgreSQL Compose service and health check configured.
- [x] SQLAlchemy connection and Alembic initial migration configured.
- [x] Backend readiness endpoint checks PostgreSQL connectivity.
- [x] Secrets excluded from Git; `.env.example` contains placeholders only.
- [x] Backend unit tests pass in the available local runtime (2 tests).
- [x] GitHub Actions CI workflow committed.
- [ ] GitHub Actions run completes successfully.
- [ ] Frontend dependencies install, TypeScript check and production build pass.
- [ ] Docker Compose build and end-to-end service startup verified.
- [ ] Verify migration application and `/ready` against a running PostgreSQL instance.
- [x] No fabricated market prices/signals.
- [x] No live execution functionality exists.

Items marked pending require a Docker/npm-capable runtime with network access; they are not represented as passed.
