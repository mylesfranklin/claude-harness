#!/usr/bin/env python3
"""
Pre-Flight Routing Hook for Claude Code Harness
Runs before tool execution (PreToolUse hook) to optimize routing.

Functions:
1. Check if a skill matches the intended action
2. Suggest better tool alternatives
3. Estimate token cost
4. Warn on expensive operations
5. Block redundant operations

Exit codes:
  0 - Allow (continue with tool)
  2 - Block (prevent tool execution)

Output to stderr is shown to user as warnings/recommendations.
"""

import json
import sys
import os
from pathlib import Path
from typing import Optional, List, Tuple
import re

MEMORY_DIR = Path.home() / '.claude' / 'memory'
KNOWLEDGE_DIR = Path.home() / '.claude' / 'knowledge'
METRICS_DIR = Path.home() / '.claude' / 'metrics'

# Token estimates by tool type
TOOL_COSTS = {
    'Read': {'base': 200, 'per_file': 500},
    'Write': {'base': 200, 'per_file': 300},
    'Edit': {'base': 150, 'per_file': 200},
    'Glob': {'base': 50, 'output': 100},
    'Grep': {'base': 100, 'output': 200},
    'Bash': {'base': 100, 'output': 200},
    'Task': {'base': 500, 'output': 3000},
    'WebFetch': {'base': 300, 'output': 1000},
    'WebSearch': {'base': 200, 'output': 500},
}

# Tool routing recommendations
TOOL_ALTERNATIVES = {
    # If using Bash for these, suggest native tools
    ('Bash', r'\bls\b'): ('Glob', 'Use Glob instead of ls for file discovery'),
    ('Bash', r'\bfind\b'): ('Glob', 'Use Glob instead of find for file patterns'),
    ('Bash', r'\bgrep\b'): ('Grep', 'Use native Grep tool instead of bash grep'),
    ('Bash', r'\bcat\b'): ('Read', 'Use Read tool instead of cat'),
    ('Bash', r'\bhead\b'): ('Read', 'Use Read with limit instead of head'),
    ('Bash', r'\btail\b'): ('Read', 'Use Read with offset instead of tail'),
    ('Bash', r'\bsed\b'): ('Edit', 'Use Edit tool instead of sed'),
    ('Bash', r'\bawk\b'): ('Edit/Grep', 'Use Edit or Grep instead of awk'),

    # If using Write when Edit would work
    ('Write', r'.*'): ('Edit', 'Consider Edit for existing files (preserves unchanged content)'),
}


def load_skills() -> List[dict]:
    """Load procedural skills for matching."""
    skills_file = MEMORY_DIR / 'procedural' / 'skills.jsonl'
    skills = []
    if skills_file.exists():
        for line in skills_file.read_text().splitlines():
            if line.strip():
                try:
                    skills.append(json.loads(line))
                except:
                    pass
    return skills


def match_skill(action: str, skills: List[dict]) -> Optional[dict]:
    """Check if action matches any known skill."""
    action_lower = action.lower()
    for skill in skills:
        triggers = skill.get('triggers', [])
        for trigger in triggers:
            if trigger.lower() in action_lower:
                return skill
    return None


def estimate_tokens(tool: str, tool_input: dict) -> int:
    """Estimate token cost for a tool call."""
    costs = TOOL_COSTS.get(tool, {'base': 100, 'output': 200})
    base = costs.get('base', 100)
    output = costs.get('output', 200)

    # Adjust based on input size
    input_str = json.dumps(tool_input)
    input_tokens = len(input_str) // 4

    return base + input_tokens + output


def check_alternatives(tool: str, tool_input: dict) -> List[str]:
    """Check if there's a better tool for this action."""
    recommendations = []

    # Get the command or content being processed
    content = ''
    if tool == 'Bash':
        content = tool_input.get('command', '')
    elif tool == 'Write':
        content = tool_input.get('file_path', '')

    for (check_tool, pattern), (alt_tool, message) in TOOL_ALTERNATIVES.items():
        if tool == check_tool:
            if re.search(pattern, content, re.IGNORECASE):
                recommendations.append(f"RECOMMEND: {message}")
                break

    return recommendations


def check_expensive_operation(tool: str, tool_input: dict) -> Optional[str]:
    """Warn about expensive operations."""
    estimated = estimate_tokens(tool, tool_input)

    if estimated > 2000:
        return f"WARNING: Estimated {estimated} tokens - consider if this is necessary"

    # Check for broad searches
    if tool == 'Grep':
        path = tool_input.get('path', '.')
        if path in ['.', './', ''] and not tool_input.get('glob') and not tool_input.get('type'):
            return "WARNING: Broad grep without filters - consider adding glob or type filter"

    if tool == 'Read':
        file_path = tool_input.get('file_path', '')
        if any(ext in file_path for ext in ['.lock', 'node_modules', '.min.js', '.min.css']):
            return "WARNING: Reading generated/lock file - usually unnecessary"

    return None


def check_redundant_operation(tool: str, tool_input: dict) -> Optional[str]:
    """Check for potentially redundant operations."""
    # Load working memory to see what's already been done
    working_file = MEMORY_DIR / 'working' / 'context-buffer.json'
    if not working_file.exists():
        return None

    try:
        working = json.loads(working_file.read_text())
    except:
        return None

    files_modified = working.get('files_modified', [])

    if tool == 'Read':
        file_path = tool_input.get('file_path', '')
        # Check if we recently read this file (would need to track reads too)
        pass

    if tool == 'Write':
        file_path = tool_input.get('file_path', '')
        if file_path in files_modified:
            return f"NOTE: {file_path} was already modified this session"

    return None


def update_working_memory(tool: str, tool_input: dict):
    """Update working memory with this tool use."""
    working_file = MEMORY_DIR / 'working' / 'context-buffer.json'

    try:
        if working_file.exists():
            working = json.loads(working_file.read_text())
        else:
            working = {
                'session_id': 'current',
                'tools_used': [],
                'files_modified': [],
                'accumulated_context_tokens': 0
            }

        # Track tool use
        if tool not in working.get('tools_used', []):
            working.setdefault('tools_used', []).append(tool)

        # Track file modifications
        if tool in ['Write', 'Edit']:
            file_path = tool_input.get('file_path', '')
            if file_path and file_path not in working.get('files_modified', []):
                working.setdefault('files_modified', []).append(file_path)

        # Accumulate tokens
        estimated = estimate_tokens(tool, tool_input)
        working['accumulated_context_tokens'] = working.get('accumulated_context_tokens', 0) + estimated

        working_file.parent.mkdir(parents=True, exist_ok=True)
        working_file.write_text(json.dumps(working, indent=2))

    except Exception as e:
        pass  # Don't fail the hook on tracking errors


def pre_flight_check(tool: str, tool_input: dict) -> Tuple[bool, List[str]]:
    """
    Main pre-flight check.
    Returns (allow: bool, messages: list)
    """
    messages = []

    # 1. Check for skill match (informational)
    skills = load_skills()
    # For skill matching, we'd need the broader task context, not just tool input
    # This is more useful at session start than per-tool

    # 2. Check for better alternatives
    alternatives = check_alternatives(tool, tool_input)
    messages.extend(alternatives)

    # 3. Check for expensive operations
    expensive_warning = check_expensive_operation(tool, tool_input)
    if expensive_warning:
        messages.append(expensive_warning)

    # 4. Check for redundant operations
    redundant_note = check_redundant_operation(tool, tool_input)
    if redundant_note:
        messages.append(redundant_note)

    # 5. Estimate tokens
    estimated = estimate_tokens(tool, tool_input)
    if estimated > 500:
        messages.append(f"TOKEN ESTIMATE: ~{estimated} tokens")

    # 6. Update working memory
    update_working_memory(tool, tool_input)

    # Decision: block or allow
    # Currently we only recommend, not block (except validate-bash.py handles dangerous commands)
    allow = True

    return allow, messages


def main():
    """Entry point for PreToolUse hook."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        tool = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        if not tool:
            sys.exit(0)

        allow, messages = pre_flight_check(tool, tool_input)

        # Output messages to stderr (shown to user)
        for msg in messages:
            print(msg, file=sys.stderr)

        if allow:
            sys.exit(0)
        else:
            sys.exit(2)  # Block

    except json.JSONDecodeError:
        # No input or invalid JSON - allow
        sys.exit(0)
    except Exception as e:
        # Don't block on errors
        print(f"Pre-flight error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
