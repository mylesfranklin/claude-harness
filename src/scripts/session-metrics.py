#!/usr/bin/env python3
"""
Session Metrics Collector for Claude Code Harness
Implements Darwin Godel Machine pattern for self-improvement metrics.

Collects:
1. Token usage efficiency (input vs output)
2. Tool usage patterns and routing accuracy
3. Task completion rates and times
4. Memory retrieval hit rates
5. Error frequency and types

Usage:
  # Record a metric
  python session-metrics.py --record tool_use --data '{"tool":"Grep","duration_ms":150}'

  # Get session summary
  python session-metrics.py --summary

  # Export for analysis
  python session-metrics.py --export
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from collections import defaultdict
import argparse

METRICS_DIR = Path.home() / '.claude' / 'metrics'
DAILY_FILE = METRICS_DIR / f"daily_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
AGGREGATE_FILE = METRICS_DIR / 'aggregate.json'

# Metric types
METRIC_TYPES = [
    'tool_use',           # Tool calls and durations
    'token_count',        # Input/output token tracking
    'memory_retrieval',   # Memory query hits/misses
    'task_outcome',       # Success/failure of tasks
    'routing_decision',   # Tool routing accuracy
    'error',              # Errors encountered
    'session_start',      # Session initialization
    'session_end',        # Session termination
]


def ensure_dir():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)


def record_metric(metric_type: str, data: dict) -> dict:
    """Record a single metric event."""
    ensure_dir()

    event = {
        'timestamp': datetime.now().isoformat(),
        'type': metric_type,
        'data': data,
    }

    # Append to daily file
    with open(DAILY_FILE, 'a') as f:
        f.write(json.dumps(event) + '\n')

    # Update running aggregates
    update_aggregates(metric_type, data)

    return event


def update_aggregates(metric_type: str, data: dict):
    """Update aggregate statistics."""
    try:
        if AGGREGATE_FILE.exists():
            agg = json.loads(AGGREGATE_FILE.read_text())
        else:
            agg = initialize_aggregates()

        today = datetime.now().strftime('%Y-%m-%d')
        if agg.get('date') != today:
            # New day, rotate aggregates
            agg = rotate_aggregates(agg)
            agg['date'] = today

        # Update based on metric type
        if metric_type == 'tool_use':
            tool = data.get('tool', 'unknown')
            agg['tools'][tool] = agg.get('tools', {}).get(tool, 0) + 1
            agg['total_tool_calls'] = agg.get('total_tool_calls', 0) + 1

            # Track routing compliance
            if data.get('was_recommended'):
                agg['routing_followed'] = agg.get('routing_followed', 0) + 1
            if data.get('had_alternative'):
                agg['routing_alternatives'] = agg.get('routing_alternatives', 0) + 1

        elif metric_type == 'token_count':
            agg['tokens_input'] = agg.get('tokens_input', 0) + data.get('input', 0)
            agg['tokens_output'] = agg.get('tokens_output', 0) + data.get('output', 0)

        elif metric_type == 'memory_retrieval':
            if data.get('hit'):
                agg['memory_hits'] = agg.get('memory_hits', 0) + 1
            else:
                agg['memory_misses'] = agg.get('memory_misses', 0) + 1

        elif metric_type == 'task_outcome':
            if data.get('success'):
                agg['tasks_succeeded'] = agg.get('tasks_succeeded', 0) + 1
            else:
                agg['tasks_failed'] = agg.get('tasks_failed', 0) + 1

        elif metric_type == 'error':
            error_type = data.get('error_type', 'unknown')
            agg['errors'][error_type] = agg.get('errors', {}).get(error_type, 0) + 1
            agg['total_errors'] = agg.get('total_errors', 0) + 1

        elif metric_type == 'session_start':
            agg['sessions_today'] = agg.get('sessions_today', 0) + 1

        AGGREGATE_FILE.write_text(json.dumps(agg, indent=2))

    except Exception as e:
        # Don't fail on aggregate errors
        pass


def initialize_aggregates() -> dict:
    """Initialize fresh aggregate structure."""
    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'sessions_today': 0,
        'total_tool_calls': 0,
        'tools': {},
        'tokens_input': 0,
        'tokens_output': 0,
        'memory_hits': 0,
        'memory_misses': 0,
        'tasks_succeeded': 0,
        'tasks_failed': 0,
        'routing_followed': 0,
        'routing_alternatives': 0,
        'total_errors': 0,
        'errors': {},
        'history': [],  # Rolling 7-day history
    }


def rotate_aggregates(old_agg: dict) -> dict:
    """Rotate aggregates at day boundary."""
    new_agg = initialize_aggregates()

    # Save yesterday's summary to history
    history = old_agg.get('history', [])
    history.append({
        'date': old_agg.get('date'),
        'sessions': old_agg.get('sessions_today', 0),
        'tool_calls': old_agg.get('total_tool_calls', 0),
        'tokens_input': old_agg.get('tokens_input', 0),
        'tokens_output': old_agg.get('tokens_output', 0),
        'success_rate': calculate_success_rate(old_agg),
        'memory_hit_rate': calculate_memory_hit_rate(old_agg),
    })

    # Keep only last 7 days
    new_agg['history'] = history[-7:]

    return new_agg


def calculate_success_rate(agg: dict) -> float:
    """Calculate task success rate."""
    total = agg.get('tasks_succeeded', 0) + agg.get('tasks_failed', 0)
    if total == 0:
        return 0.0
    return round(agg.get('tasks_succeeded', 0) / total * 100, 1)


def calculate_memory_hit_rate(agg: dict) -> float:
    """Calculate memory retrieval hit rate."""
    total = agg.get('memory_hits', 0) + agg.get('memory_misses', 0)
    if total == 0:
        return 0.0
    return round(agg.get('memory_hits', 0) / total * 100, 1)


def calculate_routing_compliance(agg: dict) -> float:
    """Calculate how often routing recommendations were followed."""
    alternatives = agg.get('routing_alternatives', 0)
    if alternatives == 0:
        return 100.0  # No recommendations means 100% compliance
    followed = agg.get('routing_followed', 0)
    return round(followed / alternatives * 100, 1)


def get_summary() -> dict:
    """Get current session/day summary."""
    ensure_dir()

    if not AGGREGATE_FILE.exists():
        return {'message': 'No metrics collected yet'}

    agg = json.loads(AGGREGATE_FILE.read_text())

    # Calculate derived metrics
    token_ratio = 0
    if agg.get('tokens_input', 0) > 0:
        token_ratio = round(agg.get('tokens_output', 0) / agg.get('tokens_input', 1), 2)

    summary = {
        'date': agg.get('date'),
        'sessions': agg.get('sessions_today', 0),
        'tool_calls': agg.get('total_tool_calls', 0),
        'top_tools': sorted(
            agg.get('tools', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5],
        'tokens': {
            'input': agg.get('tokens_input', 0),
            'output': agg.get('tokens_output', 0),
            'ratio': token_ratio,
        },
        'task_success_rate': calculate_success_rate(agg),
        'memory_hit_rate': calculate_memory_hit_rate(agg),
        'routing_compliance': calculate_routing_compliance(agg),
        'errors': agg.get('total_errors', 0),
        'top_errors': sorted(
            agg.get('errors', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:3],
    }

    # Add 7-day trend if available
    history = agg.get('history', [])
    if history:
        summary['week_trend'] = {
            'avg_sessions': round(sum(h.get('sessions', 0) for h in history) / len(history), 1),
            'avg_success_rate': round(sum(h.get('success_rate', 0) for h in history) / len(history), 1),
            'total_tokens': sum(h.get('tokens_input', 0) + h.get('tokens_output', 0) for h in history),
        }

    return summary


def format_summary(summary: dict) -> str:
    """Format summary for display."""
    lines = [
        "## Session Metrics Summary",
        "",
        f"**Date**: {summary.get('date', 'Unknown')}",
        f"**Sessions Today**: {summary.get('sessions', 0)}",
        f"**Total Tool Calls**: {summary.get('tool_calls', 0)}",
        "",
        "### Tool Usage",
    ]

    for tool, count in summary.get('top_tools', []):
        lines.append(f"  - {tool}: {count}")

    lines.extend([
        "",
        "### Tokens",
        f"  - Input: {summary.get('tokens', {}).get('input', 0):,}",
        f"  - Output: {summary.get('tokens', {}).get('output', 0):,}",
        f"  - Ratio (out/in): {summary.get('tokens', {}).get('ratio', 0)}",
        "",
        "### Performance",
        f"  - Task Success Rate: {summary.get('task_success_rate', 0)}%",
        f"  - Memory Hit Rate: {summary.get('memory_hit_rate', 0)}%",
        f"  - Routing Compliance: {summary.get('routing_compliance', 0)}%",
        f"  - Errors: {summary.get('errors', 0)}",
    ])

    if summary.get('week_trend'):
        trend = summary['week_trend']
        lines.extend([
            "",
            "### 7-Day Trend",
            f"  - Avg Sessions/Day: {trend.get('avg_sessions', 0)}",
            f"  - Avg Success Rate: {trend.get('avg_success_rate', 0)}%",
            f"  - Total Tokens: {trend.get('total_tokens', 0):,}",
        ])

    return '\n'.join(lines)


def export_metrics(days: int = 7) -> List[dict]:
    """Export metrics for external analysis."""
    ensure_dir()

    events = []
    cutoff = datetime.now() - timedelta(days=days)

    for file in sorted(METRICS_DIR.glob('daily_*.jsonl')):
        try:
            # Parse date from filename
            date_str = file.stem.replace('daily_', '')
            file_date = datetime.strptime(date_str, '%Y-%m-%d')

            if file_date >= cutoff:
                for line in file.read_text().splitlines():
                    if line.strip():
                        events.append(json.loads(line))
        except:
            continue

    return events


def main():
    parser = argparse.ArgumentParser(description='Session metrics collector')
    parser.add_argument('--record', '-r', choices=METRIC_TYPES, help='Record a metric')
    parser.add_argument('--data', '-d', help='JSON data for the metric')
    parser.add_argument('--summary', '-s', action='store_true', help='Show summary')
    parser.add_argument('--export', '-e', action='store_true', help='Export metrics')
    parser.add_argument('--days', type=int, default=7, help='Days to export')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if args.record:
        data = {}
        if args.data:
            try:
                data = json.loads(args.data)
            except:
                print(f"Invalid JSON data: {args.data}", file=sys.stderr)
                sys.exit(1)

        event = record_metric(args.record, data)
        if args.json:
            print(json.dumps(event, indent=2))
        else:
            print(f"Recorded {args.record} metric")

    elif args.export:
        events = export_metrics(args.days)
        print(json.dumps(events, indent=2))

    else:  # Default: show summary
        summary = get_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(format_summary(summary))


if __name__ == '__main__':
    main()
