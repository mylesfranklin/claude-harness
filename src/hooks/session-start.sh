#!/bin/bash
# Claude Code Harness - Session Start Hook
# Injects BOOTSTRAP.md and relevant memory at session start
#
# This hook runs when a new Claude Code session begins.
# It outputs context to be included in the conversation.

HARNESS_DIR="$HOME/.claude"
KNOWLEDGE_DIR="$HARNESS_DIR/knowledge"
MEMORY_DIR="$HARNESS_DIR/memory"
SCRIPTS_DIR="$HARNESS_DIR/scripts"

BOOTSTRAP_FILE="$KNOWLEDGE_DIR/BOOTSTRAP.md"
RETRIEVAL_SCRIPT="$SCRIPTS_DIR/memory-retrieval.py"
WORKING_BUFFER="$MEMORY_DIR/working/context-buffer.json"

# Initialize working memory for this session
initialize_working_memory() {
    mkdir -p "$MEMORY_DIR/working"

    # Create initial working memory buffer
    cat > "$WORKING_BUFFER" << EOF
{
  "session_id": "current",
  "started_at": "$(date -Iseconds)",
  "project_path": "$(pwd)",
  "current_task": "",
  "tools_used": [],
  "files_modified": [],
  "decisions_made": [],
  "accumulated_context_tokens": 0
}
EOF
}

# 1. Load BOOTSTRAP.md (always)
echo "=== HARNESS CONTEXT ==="
if [[ -f "$BOOTSTRAP_FILE" ]]; then
    cat "$BOOTSTRAP_FILE"
else
    echo "WARNING: BOOTSTRAP.md not found at $BOOTSTRAP_FILE"
    echo "Run install.sh to set up the harness."
fi
echo ""

# 2. Load recent successful patterns (quick summary)
SKILLS_FILE="$MEMORY_DIR/procedural/skills.jsonl"
if [[ -f "$SKILLS_FILE" ]] && [[ -s "$SKILLS_FILE" ]]; then
    SKILL_COUNT=$(wc -l < "$SKILLS_FILE" | tr -d ' ')
    if [[ "$SKILL_COUNT" -gt 0 ]]; then
        echo "### Available Learned Skills ($SKILL_COUNT total)"
        echo ""
        # Show last 5 skills with their triggers
        tail -5 "$SKILLS_FILE" 2>/dev/null | while read -r line; do
            python3 -c "
import sys, json
try:
    data = json.loads('''$line''')
    name = data.get('name', 'unknown')[:30]
    triggers = ', '.join(data.get('triggers', [])[:3])
    rate = data.get('success_rate', 0)
    print(f'- **{name}** (triggers: {triggers}) - {rate:.0%} success')
except Exception as e:
    pass
" 2>/dev/null
        done
        echo ""
    fi
fi

# 3. Load recent outcomes (failures are more important for learning)
FAILURES_FILE="$MEMORY_DIR/episodic/outcomes/failures.jsonl"
if [[ -f "$FAILURES_FILE" ]] && [[ -s "$FAILURES_FILE" ]]; then
    echo "### Recent Failures to Avoid"
    echo ""
    tail -3 "$FAILURES_FILE" 2>/dev/null | while read -r line; do
        python3 -c "
import sys, json
try:
    data = json.loads('''$line''')
    task = data.get('task', '')[:40]
    mistake = data.get('mistake', data.get('task', ''))[:50]
    print(f'- {mistake}')
except:
    pass
" 2>/dev/null
    done
    echo ""
fi

# 4. Load user preferences summary
PROFILE_FILE="$MEMORY_DIR/semantic/user-profile.json"
if [[ -f "$PROFILE_FILE" ]]; then
    echo "### User Preferences"
    python3 -c "
import json
try:
    with open('$PROFILE_FILE') as f:
        data = json.load(f)
    prefs = data.get('preferences', {})
    comm = prefs.get('communication', {})
    if comm.get('ask_before_major_changes'):
        print('- Ask before major changes: Yes')
    if comm.get('verbosity'):
        print(f'- Communication style: {comm[\"verbosity\"]}')
    code = prefs.get('code_style', {})
    if code:
        indent = code.get('indent', 'spaces')
        size = code.get('indent_size', 2)
        print(f'- Code style: {size} {indent}')
except:
    pass
" 2>/dev/null
    echo ""
fi

echo "=== END HARNESS CONTEXT ==="

# 5. Initialize working memory
initialize_working_memory

exit 0
