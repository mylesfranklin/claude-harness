#!/bin/bash
#
# Claude Code Harness Installer
# Deploys the harness to ~/.claude/
#
# Usage: ./install.sh [--uninstall]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
DEST_DIR="$HOME/.claude"
BACKUP_DIR="$HOME/.claude-backup-$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Uninstall function
uninstall() {
    log_info "Uninstalling Claude Code Harness..."

    # Remove harness directories (but keep user data)
    rm -rf "$DEST_DIR/knowledge"
    rm -rf "$DEST_DIR/hooks"
    rm -rf "$DEST_DIR/scripts"

    # Restore original settings.json if we have a backup marker
    if [[ -f "$DEST_DIR/.harness-installed" ]]; then
        rm "$DEST_DIR/.harness-installed"
    fi

    log_info "Harness uninstalled. Memory directory preserved at $DEST_DIR/memory"
    log_info "You may need to manually restore your original settings.json"
    exit 0
}

# Check for uninstall flag
if [[ "$1" == "--uninstall" ]]; then
    uninstall
fi

log_info "Installing Claude Code Harness..."

# Check source directory exists
if [[ ! -d "$SRC_DIR" ]]; then
    log_error "Source directory not found: $SRC_DIR"
    log_error "Run this script from the claude-harness project root."
    exit 1
fi

# Create destination if it doesn't exist
mkdir -p "$DEST_DIR"

# Backup existing settings if harness not already installed
if [[ ! -f "$DEST_DIR/.harness-installed" ]]; then
    if [[ -f "$DEST_DIR/settings.json" ]]; then
        log_info "Backing up existing settings.json..."
        cp "$DEST_DIR/settings.json" "$DEST_DIR/settings.json.pre-harness"
    fi
fi

# Create directory structure
log_info "Creating directory structure..."
mkdir -p "$DEST_DIR/knowledge/tools"
mkdir -p "$DEST_DIR/knowledge/skills"
mkdir -p "$DEST_DIR/knowledge/agents"
mkdir -p "$DEST_DIR/knowledge/cost"
mkdir -p "$DEST_DIR/memory/episodic/sessions"
mkdir -p "$DEST_DIR/memory/episodic/outcomes"
mkdir -p "$DEST_DIR/memory/semantic/domain-knowledge"
mkdir -p "$DEST_DIR/memory/procedural"
mkdir -p "$DEST_DIR/memory/working"
mkdir -p "$DEST_DIR/hooks"
mkdir -p "$DEST_DIR/scripts"
mkdir -p "$DEST_DIR/metrics"
mkdir -p "$DEST_DIR/metrics/evolution"
mkdir -p "$DEST_DIR/metrics/evolution/backups"

# Copy knowledge files
log_info "Installing knowledge layer..."
cp "$SRC_DIR/knowledge/BOOTSTRAP.md" "$DEST_DIR/knowledge/"
cp "$SRC_DIR/knowledge/tools/"*.md "$DEST_DIR/knowledge/tools/" 2>/dev/null || true
cp "$SRC_DIR/knowledge/skills/index.json" "$DEST_DIR/knowledge/skills/"
cp "$SRC_DIR/knowledge/agents/roster.json" "$DEST_DIR/knowledge/agents/"
cp "$SRC_DIR/knowledge/cost/"*.md "$DEST_DIR/knowledge/cost/" 2>/dev/null || true

# Copy scripts first (needed for settings merge)
log_info "Installing scripts..."
if compgen -G "$SRC_DIR/scripts/*" > /dev/null; then
    cp "$SRC_DIR/scripts/"* "$DEST_DIR/scripts/" 2>/dev/null || true
    chmod +x "$DEST_DIR/scripts/"* 2>/dev/null || true
fi

# Copy hooks
log_info "Installing hooks..."
cp "$SRC_DIR/hooks/"*.sh "$DEST_DIR/hooks/" 2>/dev/null || true
cp "$SRC_DIR/hooks/"*.py "$DEST_DIR/hooks/" 2>/dev/null || true

# Make hooks executable
chmod +x "$DEST_DIR/hooks/"*.sh 2>/dev/null || true
chmod +x "$DEST_DIR/hooks/"*.py 2>/dev/null || true

# Initialize memory files if they don't exist
log_info "Initializing memory layer..."
touch "$DEST_DIR/memory/episodic/outcomes/successes.jsonl"
touch "$DEST_DIR/memory/episodic/outcomes/failures.jsonl"

# Copy memory schema documentation
if [[ -f "$SRC_DIR/memory/SCHEMA.md" ]]; then
    cp "$SRC_DIR/memory/SCHEMA.md" "$DEST_DIR/memory/"
fi

# Initialize procedural memory with seed skills if empty
SKILLS_FILE="$DEST_DIR/memory/procedural/skills.jsonl"
if [[ ! -f "$SKILLS_FILE" ]] || [[ ! -s "$SKILLS_FILE" ]]; then
    log_info "Seeding procedural memory with starter skills..."
    if [[ -f "$SRC_DIR/memory/procedural/seed-skills.jsonl" ]]; then
        cp "$SRC_DIR/memory/procedural/seed-skills.jsonl" "$SKILLS_FILE"
    else
        touch "$SKILLS_FILE"
    fi
fi

# Initialize user profile if it doesn't exist
if [[ ! -f "$DEST_DIR/memory/semantic/user-profile.json" ]]; then
    cat > "$DEST_DIR/memory/semantic/user-profile.json" << 'PROFILE'
{
  "version": "1.0",
  "preferences": {
    "communication": {
      "verbosity": "concise",
      "ask_before_major_changes": true
    },
    "code_style": {
      "indent": "spaces",
      "indent_size": 2
    }
  },
  "context": {},
  "learned_preferences": []
}
PROFILE
fi

# Update settings.json with hooks
log_info "Configuring hooks in settings.json..."

# Create empty settings if none exists
if [[ ! -f "$DEST_DIR/settings.json" ]]; then
    echo '{}' > "$DEST_DIR/settings.json"
fi

# Use merge script to update settings
python3 "$DEST_DIR/scripts/merge-settings.py" "$DEST_DIR/settings.json" "$DEST_DIR/settings.json.new"

if [[ -s "$DEST_DIR/settings.json.new" ]]; then
    mv "$DEST_DIR/settings.json.new" "$DEST_DIR/settings.json"
else
    log_warn "Could not update settings.json automatically"
    rm -f "$DEST_DIR/settings.json.new"
fi

# Mark installation
echo "$(date -Iseconds)" > "$DEST_DIR/.harness-installed"

log_info "Installation complete!"
echo ""
echo "=== Claude Code Harness v3.0 Installed ==="
echo ""
echo "Installed to: $DEST_DIR"
echo ""
echo "Phase 1 - Self-Knowledge Layer:"
echo "  knowledge/BOOTSTRAP.md  - Core context (~500 tokens)"
echo "  knowledge/tools/        - Tool routing decision tree"
echo "  knowledge/agents/       - Agent roster"
echo "  knowledge/cost/         - Model cost optimization"
echo ""
echo "Phase 2 - Memory Layer:"
echo "  memory/procedural/      - Voyager-style skill library ($(wc -l < "$DEST_DIR/memory/procedural/skills.jsonl" 2>/dev/null || echo 0) skills)"
echo "  memory/episodic/        - Session outcomes"
echo "  memory/semantic/        - User preferences & domain knowledge"
echo "  memory/working/         - Session context buffer"
echo ""
echo "Phase 3 - Guardrails Layer:"
echo "  hooks/pre-flight.py     - Tool routing optimizer"
echo "  hooks/validate-bash.py  - Security guardrail"
echo "  scripts/token-budget.py - Token usage tracker"
echo ""
echo "Phase 4 - Meta-Learning Layer:"
echo "  scripts/session-metrics.py    - Performance metrics collector"
echo "  scripts/performance-analyzer.py - Multi-perspective analysis"
echo "  scripts/harness-evolve.py     - Self-improvement system"
echo "  metrics/evolution/            - Evolution proposals & history"
echo ""
echo "Hooks Active:"
echo "  session-start.sh        - Loads context + memory at start"
echo "  capture-session.py      - Saves learnings at session end"
echo "  pre-flight.py           - Pre-tool routing optimizer"
echo "  validate-bash.py        - Security guardrail"
echo ""
echo "Evolution Commands:"
echo "  python ~/.claude/scripts/harness-evolve.py --propose"
echo "  python ~/.claude/scripts/performance-analyzer.py --analyze"
echo "  python ~/.claude/scripts/session-metrics.py --summary"
echo ""
echo "To verify: Start a new Claude Code session."
echo "To uninstall: ./install.sh --uninstall"
