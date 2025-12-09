#!/usr/bin/env python3
"""
Claude Code Harness - Bash Validation Hook
Pre-flight security check for bash commands.

Blocks dangerous patterns and warns about high-risk operations.
Exit codes:
  0 - Allow command
  1 - Error (not a block)
  2 - Block command (dangerous)
"""

import json
import sys
import re

# Patterns that should ALWAYS be blocked
BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/(?!\w)",          # rm -rf / (not rm -rf /some/path)
    r"rm\s+-rf\s+~\s*$",            # rm -rf ~ (entire home)
    r"rm\s+-rf\s+\$HOME\s*$",       # rm -rf $HOME
    r"mkfs\.",                       # Format filesystem
    r"dd\s+if=.*of=/dev/[sh]d",     # Disk write operations
    r">\s*/dev/[sh]d",              # Redirect to disk
    r"curl.*\|\s*(?:bash|sh|zsh)",  # Pipe URL to shell
    r"wget.*\|\s*(?:bash|sh|zsh)", # Pipe URL to shell
    r"chmod\s+777\s+/",             # World-writable root paths
    r"chown.*:.*\s+/(?!\w)",        # Change ownership of root
    r">\s*/etc/passwd",             # Overwrite passwd
    r">\s*/etc/shadow",             # Overwrite shadow
    r":\(\)\s*\{",                  # Fork bomb pattern
]

# Patterns that warrant warnings (allow but notify)
WARNING_PATTERNS = [
    (r"rm\s+-rf", "Recursive delete - verify path is correct"),
    (r"chmod\s+777", "World-writable permissions - consider 755 or 644"),
    (r"sudo", "Elevated privileges requested"),
    (r">\s*/etc/", "Writing to /etc - system config modification"),
    (r"pip.*--break-system-packages", "Breaking system packages"),
    (r"npm.*--force", "Forcing npm operation"),
]


def check_command(command: str) -> tuple[bool, str]:
    """
    Check if command is safe to execute.
    Returns (allowed: bool, message: str)
    """
    # Check blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"BLOCKED: Matches dangerous pattern '{pattern}'"

    # Check warning patterns
    warnings = []
    for pattern, message in WARNING_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            warnings.append(f"WARNING: {message}")

    if warnings:
        return True, "\n".join(warnings)

    return True, ""


def main():
    try:
        # Read input from stdin (hook receives JSON)
        input_data = json.load(sys.stdin)

        # Extract command from tool input
        tool_input = input_data.get("tool_input", {})
        command = tool_input.get("command", "")

        if not command:
            # No command to validate
            sys.exit(0)

        allowed, message = check_command(command)

        if not allowed:
            print(message, file=sys.stderr)
            sys.exit(2)  # Block

        if message:
            # Warnings - print but allow
            print(message, file=sys.stderr)

        sys.exit(0)  # Allow

    except json.JSONDecodeError:
        print("ERROR: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
