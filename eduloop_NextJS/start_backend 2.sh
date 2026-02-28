#!/bin/bash
# Run from eduloop_NextJS/ — starts FastAPI backend without --reload
# Usage: bash start_backend.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PATH="/Users/jiahangx/Library/Python/3.9/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "Starting EduLoop FastAPI backend on http://localhost:8000 ..."
exec uvicorn backend.main:app --port 8000
