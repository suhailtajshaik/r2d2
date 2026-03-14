#!/bin/bash
# Collect daily memory entries from the last 30 days

MEMORY_DIR="${WORKSPACE:-/home/r2d2/.openclaw/workspace}/memory"
CUTOFF_DATE=$(date -d "30 days ago" +%Y-%m-%d 2>/dev/null || date -v-30d +%Y-%m-%d)

if [ ! -d "$MEMORY_DIR" ]; then
    echo "No memory directory found at $MEMORY_DIR"
    exit 0
fi

# Find and sort daily files, filter by date
for file in "$MEMORY_DIR"/????-??-??.md; do
    [ -f "$file" ] || continue
    
    # Extract date from filename
    filename=$(basename "$file" .md)
    
    # Compare dates (works because YYYY-MM-DD sorts lexicographically)
    if [[ "$filename" > "$CUTOFF_DATE" ]] || [[ "$filename" == "$CUTOFF_DATE" ]]; then
        echo "=== $filename ==="
        cat "$file"
        echo ""
    fi
done | sort -r
