#!/bin/bash
set -euo pipefail

LOG_FILE="/home/catalin/Workspace/Jupiter/job_market_md_refactor/scraper.log"
STATE_FILE="/tmp/job_scraper_last_run"
NOW=$(date +%s)  # current epoch time
TIMESTAMP="[$(date '+%Y-%m-%d %H:%M:%S')]"

# Check last run time
if [[ -f "$STATE_FILE" ]]; then
    LAST_RUN=$(cat "$STATE_FILE")
    ELAPSED=$(( NOW - LAST_RUN ))
    if (( ELAPSED < 3600 )); then
        echo "$TIMESTAMP Skipped (last run $((ELAPSED / 60)) min ago)" >> "$LOG_FILE"
        exit 0
    fi
fi

# Log start
echo "$NOW" > "$STATE_FILE"
echo "$TIMESTAMP Starting job scraper..." >> "$LOG_FILE"

# Run the job
cd /home/catalin/Workspace/Jupiter
source venv/bin/activate
cd job_market_md_refactor

python3 job_scraper.py >> "$LOG_FILE" 2>&1

# Log end
echo "$TIMESTAMP Finished." >> "$LOG_FILE"