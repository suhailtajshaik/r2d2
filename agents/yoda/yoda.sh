#!/bin/bash
# yoda.sh — Talk to Yoda without typing docker commands
# Usage:
#   ./yoda.sh learn --file paper.pdf
#   ./yoda.sh learn --url https://arxiv.org/abs/2301.08243
#   ./yoda.sh evolve
#   ./yoda.sh status
#   ./yoda.sh train --epochs 5
#   ./yoda.sh demo

set -e

YODA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env if exists
if [ -f "$YODA_DIR/.env" ]; then
    export $(grep -v '^#' "$YODA_DIR/.env" | xargs)
fi

# If ANTHROPIC_API_KEY not set, warn but continue (local extraction still works)
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set — running in local extraction mode"
    echo "   For full Claude-powered evolution, add key to $YODA_DIR/.env"
fi

# Run Yoda — prefer Docker if available, fallback to local python
if command -v docker &>/dev/null && docker ps &>/dev/null 2>&1; then
    docker compose -f "$YODA_DIR/docker-compose.yml" run --rm \
        -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
        yoda "$@"
else
    cd "$YODA_DIR"
    python3 agent.py "$@"
fi
