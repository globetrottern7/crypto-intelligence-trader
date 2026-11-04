#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
python -m pip install -r backend/requirements-dev.txt
cd frontend
npm install
cd ..
