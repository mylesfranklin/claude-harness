#!/bin/bash
# Claude Code Harness - Session Start Hook
# Injects BOOTSTRAP.md context at session start
#
# This hook runs when a new Claude Code session begins.
# It outputs the bootstrap context to be included in the conversation.

HARNESS_DIR="$HOME/.claude/knowledge"
BOOTSTRAP_FILE="$HARNESS_DIR/BOOTSTRAP.md"

# Check if bootstrap file exists
if [[ -f "$BOOTSTRAP_FILE" ]]; then
    echo "=== HARNESS CONTEXT LOADED ==="
    cat "$BOOTSTRAP_FILE"
    echo ""
    echo "=== END HARNESS CONTEXT ==="
else
    echo "WARNING: BOOTSTRAP.md not found at $BOOTSTRAP_FILE"
    echo "Run install.sh to set up the harness."
fi

# Load recent successful patterns if available
SKILLS_FILE="$HOME/.claude/memory/procedural/skills.jsonl"
if [[ -f "$SKILLS_FILE" ]] && [[ -s "$SKILLS_FILE" ]]; then
    echo ""
    echo "=== RECENT SUCCESSFUL PATTERNS ==="
    tail -3 "$SKILLS_FILE" 2>/dev/null | while read -r line; do
        echo "$line" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"- {data.get('task_description', 'Unknown task')[:50]}...\")
except:
    pass
" 2>/dev/null
    done
    echo "=== END PATTERNS ==="
fi

exit 0
