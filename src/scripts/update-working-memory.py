#!/usr/bin/env python3
"""
Update Working Memory during a session.
Used to track progress and context for later capture.

Usage:
  # Set current task
  python update-working-memory.py --task "Implement user auth"

  # Record a tool use
  python update-working-memory.py --tool "Grep"

  # Record a file modification
  python update-working-memory.py --file "src/auth/jwt.ts"

  # Record a decision
  python update-working-memory.py --decision "Using JWT over sessions"

  # Show current working memory
  python update-working-memory.py --show
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

WORKING_DIR = Path.home() / '.claude' / 'memory' / 'working'
BUFFER_FILE = WORKING_DIR / 'context-buffer.json'


def ensure_dir():
    WORKING_DIR.mkdir(parents=True, exist_ok=True)


def load_buffer() -> dict:
    """Load current working memory buffer."""
    if BUFFER_FILE.exists():
        try:
            return json.loads(BUFFER_FILE.read_text())
        except:
            pass

    # Return default structure
    return {
        'session_id': 'current',
        'started_at': datetime.now().isoformat(),
        'project_path': str(Path.cwd()),
        'current_task': '',
        'tools_used': [],
        'files_modified': [],
        'decisions_made': [],
        'accumulated_context_tokens': 0,
    }


def save_buffer(buffer: dict):
    """Save working memory buffer."""
    ensure_dir()
    BUFFER_FILE.write_text(json.dumps(buffer, indent=2, default=str))


def update_task(task: str):
    """Set or update the current task."""
    buffer = load_buffer()
    buffer['current_task'] = task
    save_buffer(buffer)
    print(f"Task set: {task}")


def add_tool(tool: str):
    """Record a tool use."""
    buffer = load_buffer()
    if tool not in buffer['tools_used']:
        buffer['tools_used'].append(tool)
    save_buffer(buffer)
    print(f"Tool recorded: {tool}")


def add_file(file_path: str):
    """Record a file modification."""
    buffer = load_buffer()
    if file_path not in buffer['files_modified']:
        buffer['files_modified'].append(file_path)
    save_buffer(buffer)
    print(f"File recorded: {file_path}")


def add_decision(decision: str):
    """Record a decision made."""
    buffer = load_buffer()
    buffer['decisions_made'].append({
        'decision': decision,
        'timestamp': datetime.now().isoformat()
    })
    save_buffer(buffer)
    print(f"Decision recorded: {decision}")


def add_tokens(count: int):
    """Add to accumulated token count."""
    buffer = load_buffer()
    buffer['accumulated_context_tokens'] += count
    save_buffer(buffer)
    print(f"Tokens added: {count} (total: {buffer['accumulated_context_tokens']})")


def show_buffer():
    """Display current working memory."""
    buffer = load_buffer()
    print(json.dumps(buffer, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(description='Update working memory')
    parser.add_argument('--task', '-t', help='Set current task')
    parser.add_argument('--tool', help='Record tool use')
    parser.add_argument('--file', '-f', help='Record file modification')
    parser.add_argument('--decision', '-d', help='Record a decision')
    parser.add_argument('--tokens', type=int, help='Add token count')
    parser.add_argument('--show', '-s', action='store_true', help='Show current buffer')

    args = parser.parse_args()

    if args.show:
        show_buffer()
    elif args.task:
        update_task(args.task)
    elif args.tool:
        add_tool(args.tool)
    elif args.file:
        add_file(args.file)
    elif args.decision:
        add_decision(args.decision)
    elif args.tokens:
        add_tokens(args.tokens)
    else:
        show_buffer()


if __name__ == '__main__':
    main()
