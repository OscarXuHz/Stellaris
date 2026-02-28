#!/bin/bash
# Run from eduloop_NextJS/nextjs/ — starts Next.js dev server
# Usage: bash start_frontend.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/nextjs"

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "Starting EduLoop Next.js frontend on http://localhost:3000 ..."
exec npm run dev
