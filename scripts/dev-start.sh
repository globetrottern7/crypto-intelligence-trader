#!/usr/bin/env bash
set -euo pipefail
mkdir -p .runtime-logs
(
  cd backend
  alembic upgrade head
  uvicorn app.main:app --host 0.0.0.0 --port 8000
) > .runtime-logs/backend.log 2>&1 &
BACKEND_PID=$!
(
  cd frontend
  npm run dev -- --hostname 0.0.0.0
) > .runtime-logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cleanup() {
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
echo "Backend logs: .runtime-logs/backend.log"
echo "Frontend logs: .runtime-logs/frontend.log"
echo "Wait for both services, then open forwarded port 3000."
wait
