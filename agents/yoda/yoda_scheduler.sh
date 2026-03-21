#!/bin/bash
# Yoda Learning Loop Scheduler
# Runs learning agent 4 times daily: 2 AM, 8 AM, 2 PM, 8 PM EST
# Install with: crontab -e
# Add these lines:
# 0 2 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
# 0 8 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
# 0 14 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
# 0 20 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh

set -e

AGENT_DIR="/home/r2d2/brain/agents/yoda"
LOG_DIR="/home/r2d2/.openclaw/workspace/memory"
LOG_FILE="$LOG_DIR/yoda_learning_$(date +%Y-%m-%d).log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log execution
{
    echo "=========================================="
    echo "Yoda Learning Loop - $(date)"
    echo "=========================================="
    
    # Run the learning agent
    cd "$AGENT_DIR"
    python3 yoda_learning_agent.py 2>&1
    
    echo ""
    echo "✅ Completed at $(date)"
} >> "$LOG_FILE"

# Also log to a separate state file for monitoring
LAST_RUN_FILE="$AGENT_DIR/last_run.json"
python3 -c "
import json
import datetime
with open('$LAST_RUN_FILE', 'w') as f:
    json.dump({
        'last_run': datetime.datetime.now().isoformat(),
        'schedule': ['2 AM', '8 AM', '2 PM', '8 PM EST']
    }, f, indent=2)
" 2>/dev/null || true

exit 0
