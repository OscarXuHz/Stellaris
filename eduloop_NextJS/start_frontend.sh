#!/bin/bash
# Starts Next.js dev server.
# Can be run from ANY directory: bash /path/to/start_frontend.sh

# Resolve the directory this script lives in, even if cwd is broken
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [ -z "$SCRIPT_DIR" ]; then
  SCRIPT_DIR="/Users/jiahangx/Library/Mobile Documents/com~apple~CloudDocs/Activities and Registration/HTE/Stellaris/eduloop_NextJS"
fi
cd "$SCRIPT_DIR/nextjs" || { echo "ERROR: cannot cd to $SCRIPT_DIR/nextjs"; exit 1; }

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "Starting EduLoop Next.js frontend on http://localhost:3000 ..."
exec npm run dev
