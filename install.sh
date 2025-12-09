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
touch "$DEST_DIR/memory/procedural/skills.jsonl"
touch "$DEST_DIR/memory/episodic/outcomes/successes.jsonl"
touch "$DEST_DIR/memory/episodic/outcomes/failures.jsonl"

# Initialize user profile if it doesn't exist
if [[ ! -f "$DEST_DIR/memory/semantic/user-profile.json" ]]; then
    echo '{"version": "1.0", "preferences": {}, "context": {}}' > "$DEST_DIR/memory/semantic/user-profile.json"
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
echo "=== Claude Code Harness v1.0 Installed ==="
echo ""
echo "Installed to: $DEST_DIR"
echo ""
echo "Structure:"
echo "  knowledge/    - Self-knowledge layer (BOOTSTRAP.md, routing, costs)"
echo "  memory/       - Persistent memory (episodic, semantic, procedural)"
echo "  hooks/        - Lifecycle hooks (security validation)"
echo "  scripts/      - Utility scripts"
echo "  metrics/      - Session metrics (Phase 4)"
echo ""
echo "What happens now:"
echo "  1. BOOTSTRAP.md provides self-knowledge context"
echo "  2. validate-bash.py blocks dangerous commands"
echo "  3. Memory directories ready for Phase 2"
echo ""
echo "To verify: Start a new Claude Code session and check if"
echo "the routing rules influence tool selection."
echo ""
echo "To uninstall: ./install.sh --uninstall"
