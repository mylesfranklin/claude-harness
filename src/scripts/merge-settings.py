#!/usr/bin/env python3
"""
Merge harness hooks into existing settings.json
Usage: merge-settings.py <existing_settings_file> <output_file>
"""

import json
import sys
from pathlib import Path


def merge_settings(existing_path: str, output_path: str):
    # Load existing settings
    if Path(existing_path).exists():
        with open(existing_path) as f:
            existing = json.load(f)
    else:
        existing = {}

    # Ensure hooks structure exists
    if "hooks" not in existing:
        existing["hooks"] = {}
    if "PreToolUse" not in existing["hooks"]:
        existing["hooks"]["PreToolUse"] = []

    # Check for existing hooks
    bash_validator_exists = False
    preflight_exists = False

    for hook_config in existing["hooks"]["PreToolUse"]:
        matcher = hook_config.get("matcher", "")
        for h in hook_config.get("hooks", []):
            cmd = h.get("command", "")
            if "validate-bash.py" in cmd:
                bash_validator_exists = True
            if "pre-flight.py" in cmd:
                preflight_exists = True

    # Add pre-flight routing hook for all tools (runs first)
    if not preflight_exists:
        existing["hooks"]["PreToolUse"].insert(0, {
            "matcher": "",  # Empty matcher = all tools
            "hooks": [{
                "type": "command",
                "command": "$HOME/.claude/hooks/pre-flight.py"
            }]
        })

    # Add bash validator if not present
    if not bash_validator_exists:
        existing["hooks"]["PreToolUse"].append({
            "matcher": "Bash",
            "hooks": [{
                "type": "command",
                "command": "$HOME/.claude/hooks/validate-bash.py"
            }]
        })

    # Write output
    with open(output_path, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Settings merged to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: merge-settings.py <existing_settings> <output>")
        sys.exit(1)

    merge_settings(sys.argv[1], sys.argv[2])
