#!/usr/bin/env python3
"""
Token Budget Manager for Claude Code Harness
Based on TALE framework (ACL 2025) - 68% output token reduction through budgeting.

Features:
1. Track cumulative token usage per session
2. Warn when approaching context limits
3. Suggest model downgrades for simple tasks
4. Estimate remaining budget

Usage:
  # Check current budget status
  python token-budget.py --status

  # Add tokens to the count
  python token-budget.py --add 500

  # Reset budget for new session
  python token-budget.py --reset

  # Get recommendation for a task
  python token-budget.py --task "fix typo in readme"
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

MEMORY_DIR = Path.home() / '.claude' / 'memory'
WORKING_DIR = MEMORY_DIR / 'working'
BUDGET_FILE = WORKING_DIR / 'token-budget.json'

# Context window limits (approximate)
CONTEXT_LIMITS = {
    'haiku': 200000,
    'sonnet': 200000,
    'opus': 200000,
}

# Warning thresholds (percentage of limit)
WARNING_THRESHOLD = 0.7  # 70%
CRITICAL_THRESHOLD = 0.9  # 90%

# Task complexity classification
TASK_PATTERNS = {
    'simple': [
        r'fix typo', r'add comment', r'rename', r'delete',
        r'simple', r'quick', r'minor', r'small change',
        r'update version', r'change string', r'remove unused',
    ],
    'medium': [
        r'add function', r'implement', r'create', r'write test',
        r'refactor', r'update', r'modify', r'fix bug',
    ],
    'complex': [
        r'architect', r'design', r'complex', r'multi-file',
        r'full feature', r'major refactor', r'security audit',
        r'performance optimization', r'migrate',
    ],
}

# Model recommendations by complexity
MODEL_RECOMMENDATIONS = {
    'simple': {
        'model': 'haiku',
        'reason': 'Simple task - Haiku is 15x cheaper and sufficient',
        'max_tokens': 500,
    },
    'medium': {
        'model': 'sonnet',
        'reason': 'Standard task - Sonnet provides good balance',
        'max_tokens': 2000,
    },
    'complex': {
        'model': 'opus',
        'reason': 'Complex task - Opus provides best reasoning',
        'max_tokens': 8000,
    },
}


def ensure_dir():
    WORKING_DIR.mkdir(parents=True, exist_ok=True)


def load_budget() -> dict:
    """Load current budget state."""
    if BUDGET_FILE.exists():
        try:
            return json.loads(BUDGET_FILE.read_text())
        except:
            pass

    return {
        'session_start': datetime.now().isoformat(),
        'tokens_used': 0,
        'tool_calls': 0,
        'model': 'sonnet',  # Default assumption
        'warnings_issued': 0,
    }


def save_budget(budget: dict):
    """Save budget state."""
    ensure_dir()
    BUDGET_FILE.write_text(json.dumps(budget, indent=2, default=str))


def classify_task(task: str) -> str:
    """Classify task complexity."""
    import re
    task_lower = task.lower()

    for complexity, patterns in TASK_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, task_lower):
                return complexity

    return 'medium'  # Default


def get_status() -> dict:
    """Get current budget status."""
    budget = load_budget()
    model = budget.get('model', 'sonnet')
    limit = CONTEXT_LIMITS.get(model, 200000)
    used = budget.get('tokens_used', 0)
    remaining = limit - used
    percentage = (used / limit) * 100 if limit > 0 else 0

    status = {
        'model': model,
        'tokens_used': used,
        'tokens_remaining': remaining,
        'context_limit': limit,
        'percentage_used': round(percentage, 1),
        'tool_calls': budget.get('tool_calls', 0),
        'session_start': budget.get('session_start'),
    }

    # Determine status level
    if percentage >= CRITICAL_THRESHOLD * 100:
        status['level'] = 'CRITICAL'
        status['message'] = 'Context nearly full - consider summarizing or starting new session'
    elif percentage >= WARNING_THRESHOLD * 100:
        status['level'] = 'WARNING'
        status['message'] = 'Context usage high - be mindful of token usage'
    else:
        status['level'] = 'OK'
        status['message'] = 'Context usage normal'

    return status


def add_tokens(count: int) -> dict:
    """Add tokens to the budget."""
    budget = load_budget()
    budget['tokens_used'] = budget.get('tokens_used', 0) + count
    budget['tool_calls'] = budget.get('tool_calls', 0) + 1
    save_budget(budget)
    return get_status()


def reset_budget(model: str = 'sonnet') -> dict:
    """Reset budget for a new session."""
    budget = {
        'session_start': datetime.now().isoformat(),
        'tokens_used': 0,
        'tool_calls': 0,
        'model': model,
        'warnings_issued': 0,
    }
    save_budget(budget)
    return get_status()


def get_recommendation(task: str) -> dict:
    """Get model and budget recommendation for a task."""
    complexity = classify_task(task)
    rec = MODEL_RECOMMENDATIONS[complexity]

    return {
        'task': task,
        'complexity': complexity,
        'recommended_model': rec['model'],
        'reason': rec['reason'],
        'suggested_max_tokens': rec['max_tokens'],
    }


def format_status(status: dict) -> str:
    """Format status for display."""
    lines = [
        "## Token Budget Status",
        "",
        f"**Model**: {status['model']}",
        f"**Used**: {status['tokens_used']:,} / {status['context_limit']:,} ({status['percentage_used']}%)",
        f"**Remaining**: {status['tokens_remaining']:,}",
        f"**Tool calls**: {status['tool_calls']}",
        "",
        f"**Status**: {status['level']}",
        f"**Message**: {status['message']}",
    ]

    if status['level'] == 'CRITICAL':
        lines.extend([
            "",
            "### Recommendations:",
            "1. Use context compression to summarize earlier context",
            "2. Consider starting a new session",
            "3. Focus on completing current task efficiently",
        ])
    elif status['level'] == 'WARNING':
        lines.extend([
            "",
            "### Recommendations:",
            "1. Prioritize essential operations",
            "2. Use Grep over Read where possible",
            "3. Delegate exploration to Task agents",
        ])

    return '\n'.join(lines)


def format_recommendation(rec: dict) -> str:
    """Format recommendation for display."""
    lines = [
        "## Task Analysis",
        "",
        f"**Task**: {rec['task']}",
        f"**Complexity**: {rec['complexity'].upper()}",
        "",
        f"**Recommended Model**: {rec['recommended_model']}",
        f"**Reason**: {rec['reason']}",
        f"**Suggested Token Limit**: {rec['suggested_max_tokens']:,}",
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Token budget manager')
    parser.add_argument('--status', '-s', action='store_true', help='Show budget status')
    parser.add_argument('--add', '-a', type=int, help='Add tokens to count')
    parser.add_argument('--reset', '-r', action='store_true', help='Reset budget')
    parser.add_argument('--model', '-m', default='sonnet', help='Model for reset')
    parser.add_argument('--task', '-t', help='Get recommendation for task')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if args.add:
        status = add_tokens(args.add)
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"Added {args.add} tokens")
            print(format_status(status))

    elif args.reset:
        status = reset_budget(args.model)
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("Budget reset")
            print(format_status(status))

    elif args.task:
        rec = get_recommendation(args.task)
        if args.json:
            print(json.dumps(rec, indent=2))
        else:
            print(format_recommendation(rec))

    else:  # Default: show status
        status = get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(format_status(status))


if __name__ == '__main__':
    main()
