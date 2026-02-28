#!/bin/bash
# Starts FastAPI backend without --reload.
# Can be run from ANY directory: bash /path/to/start_backend.sh

# Resolve the directory this script lives in, even if cwd is broken
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [ -z "$SCRIPT_DIR" ]; then
  # Fallback: hardcoded absolute path
  SCRIPT_DIR="/Users/jiahangx/Library/Mobile Documents/com~apple~CloudDocs/Activities and Registration/HTE/Stellaris/eduloop_NextJS"
fi
cd "$SCRIPT_DIR" || { echo "ERROR: cannot cd to $SCRIPT_DIR"; exit 1; }

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PATH="/Users/jiahangx/Library/Python/3.9/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "Starting EduLoop FastAPI backend on http://localhost:8000 ..."
exec uvicorn backend.main:app --port 8000
