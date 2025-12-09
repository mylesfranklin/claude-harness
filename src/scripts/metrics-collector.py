#!/usr/bin/env python3
"""
Metrics Collector for Claude Code Harness
Tracks tool usage, token costs, and routing efficiency.

Usage:
  # Record a tool call
  python metrics-collector.py record --tool "Glob" --tokens 150 --scenario "file-discovery"

  # Generate report
  python metrics-collector.py report

  # Clear metrics
  python metrics-collector.py clear
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import argparse

METRICS_DIR = Path.home() / '.claude' / 'metrics'
METRICS_FILE = METRICS_DIR / 'test-metrics.jsonl'

# Token cost estimates by tool
TOOL_TOKEN_ESTIMATES = {
    # File operations
    'Glob': {'input': 50, 'output': 100},
    'Grep': {'input': 100, 'output': 200},
    'Read': {'input': 200, 'output': 500},  # varies by file size
    'Write': {'input': 200, 'output': 100},
    'Edit': {'input': 300, 'output': 200},

    # Shell operations
    'Bash': {'input': 100, 'output': 200},
    'Bash:ls': {'input': 50, 'output': 150},
    'Bash:find': {'input': 100, 'output': 300},
    'Bash:grep': {'input': 100, 'output': 400},

    # Agent operations
    'Task': {'input': 500, 'output': 2000},
    'Task:Explore': {'input': 500, 'output': 3000},
    'Task:Plan': {'input': 500, 'output': 4000},

    # Web operations
    'WebFetch': {'input': 300, 'output': 1000},
    'WebSearch': {'input': 200, 'output': 500},
}

# Optimal routing for each scenario
OPTIMAL_ROUTES = {
    'file-discovery': ['Glob'],
    'content-search': ['Grep'],
    'multi-file-read': ['Read', 'Read', 'Read'],  # Parallel
    'codebase-explore': ['Task:Explore'],
    'simple-verify': ['Glob'],
    'code-modify': ['Grep', 'Edit'],
    'structure-query': ['Task:Explore'],
    'dependency-check': ['Read'],
}


def ensure_metrics_dir():
    """Ensure metrics directory exists."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)


def record_metric(
    tool: str,
    scenario: str,
    tokens_input: int = 0,
    tokens_output: int = 0,
    is_baseline: bool = False,
    notes: Optional[str] = None
):
    """Record a tool call metric."""
    ensure_metrics_dir()

    # Use estimates if not provided
    if tokens_input == 0 and tool in TOOL_TOKEN_ESTIMATES:
        tokens_input = TOOL_TOKEN_ESTIMATES[tool]['input']
    if tokens_output == 0 and tool in TOOL_TOKEN_ESTIMATES:
        tokens_output = TOOL_TOKEN_ESTIMATES[tool]['output']

    metric = {
        'timestamp': datetime.now().isoformat(),
        'tool': tool,
        'scenario': scenario,
        'tokens_input': tokens_input,
        'tokens_output': tokens_output,
        'tokens_total': tokens_input + tokens_output,
        'is_baseline': is_baseline,
        'notes': notes,
    }

    with open(METRICS_FILE, 'a') as f:
        f.write(json.dumps(metric) + '\n')

    print(f"Recorded: {tool} ({tokens_input + tokens_output} tokens) for {scenario}")


def load_metrics() -> list[dict]:
    """Load all recorded metrics."""
    if not METRICS_FILE.exists():
        return []

    metrics = []
    with open(METRICS_FILE) as f:
        for line in f:
            if line.strip():
                metrics.append(json.loads(line))
    return metrics


def generate_report():
    """Generate a comparison report."""
    metrics = load_metrics()

    if not metrics:
        print("No metrics recorded yet.")
        return

    # Group by scenario and baseline flag
    scenarios = {}
    for m in metrics:
        scenario = m['scenario']
        is_baseline = m['is_baseline']

        if scenario not in scenarios:
            scenarios[scenario] = {'baseline': [], 'optimized': []}

        key = 'baseline' if is_baseline else 'optimized'
        scenarios[scenario][key].append(m)

    print("\n" + "=" * 70)
    print("HARNESS EFFICIENCY REPORT")
    print("=" * 70)

    total_baseline = 0
    total_optimized = 0
    improvements = []

    for scenario, data in scenarios.items():
        baseline_tokens = sum(m['tokens_total'] for m in data['baseline'])
        optimized_tokens = sum(m['tokens_total'] for m in data['optimized'])
        baseline_calls = len(data['baseline'])
        optimized_calls = len(data['optimized'])

        total_baseline += baseline_tokens
        total_optimized += optimized_tokens

        if baseline_tokens > 0 and optimized_tokens > 0:
            improvement = ((baseline_tokens - optimized_tokens) / baseline_tokens) * 100
            improvements.append(improvement)

            print(f"\n{scenario.upper()}")
            print("-" * 40)
            print(f"  Baseline:  {baseline_tokens:>6} tokens ({baseline_calls} calls)")
            print(f"  Optimized: {optimized_tokens:>6} tokens ({optimized_calls} calls)")
            print(f"  Improvement: {improvement:>5.1f}%")

            # Check routing accuracy
            if scenario in OPTIMAL_ROUTES:
                optimal = OPTIMAL_ROUTES[scenario]
                actual = [m['tool'] for m in data['optimized']]

                # Simple check: did we use the optimal tools?
                optimal_set = set(optimal)
                actual_set = set(actual)

                if actual_set.issubset(optimal_set) or actual_set == optimal_set:
                    print(f"  Routing: OPTIMAL")
                else:
                    print(f"  Routing: SUBOPTIMAL (used: {actual}, optimal: {optimal})")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if improvements:
        avg_improvement = sum(improvements) / len(improvements)
        print(f"\n  Total baseline tokens:  {total_baseline:>8}")
        print(f"  Total optimized tokens: {total_optimized:>8}")
        print(f"  Average improvement:    {avg_improvement:>7.1f}%")

        if avg_improvement >= 40:
            print(f"\n  STATUS: PASS (target: >40%)")
        else:
            print(f"\n  STATUS: FAIL (target: >40%, got: {avg_improvement:.1f}%)")
    else:
        print("\n  Insufficient data for comparison.")
        print("  Run both baseline and optimized tests for each scenario.")

    print()


def clear_metrics():
    """Clear all recorded metrics."""
    if METRICS_FILE.exists():
        METRICS_FILE.unlink()
        print("Metrics cleared.")
    else:
        print("No metrics file to clear.")


def main():
    parser = argparse.ArgumentParser(description='Metrics collector for Claude Code Harness')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Record command
    record_parser = subparsers.add_parser('record', help='Record a tool call metric')
    record_parser.add_argument('--tool', required=True, help='Tool name')
    record_parser.add_argument('--scenario', required=True, help='Test scenario name')
    record_parser.add_argument('--tokens-in', type=int, default=0, help='Input tokens')
    record_parser.add_argument('--tokens-out', type=int, default=0, help='Output tokens')
    record_parser.add_argument('--baseline', action='store_true', help='Mark as baseline test')
    record_parser.add_argument('--notes', help='Additional notes')

    # Report command
    subparsers.add_parser('report', help='Generate comparison report')

    # Clear command
    subparsers.add_parser('clear', help='Clear all metrics')

    args = parser.parse_args()

    if args.command == 'record':
        record_metric(
            tool=args.tool,
            scenario=args.scenario,
            tokens_input=args.tokens_in,
            tokens_output=args.tokens_out,
            is_baseline=args.baseline,
            notes=args.notes,
        )
    elif args.command == 'report':
        generate_report()
    elif args.command == 'clear':
        clear_metrics()


if __name__ == '__main__':
    main()
