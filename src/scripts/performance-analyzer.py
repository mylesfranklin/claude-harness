#!/usr/bin/env python3
"""
Performance Analyzer for Claude Code Harness
Implements Forest-of-Thought analysis for multi-perspective evaluation.

Analyzes:
1. Tool routing efficiency - Are we using optimal tools?
2. Token efficiency - Can we reduce token consumption?
3. Memory effectiveness - Is memory helping?
4. Error patterns - What's causing failures?
5. Session patterns - Optimal session structure?

Outputs actionable recommendations for harness evolution.

Usage:
  # Run full analysis
  python performance-analyzer.py --analyze

  # Get specific analysis
  python performance-analyzer.py --analyze routing

  # Generate evolution recommendations
  python performance-analyzer.py --recommend
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import argparse
import re

METRICS_DIR = Path.home() / '.claude' / 'metrics'
MEMORY_DIR = Path.home() / '.claude' / 'memory'
KNOWLEDGE_DIR = Path.home() / '.claude' / 'knowledge'
ANALYSIS_FILE = METRICS_DIR / 'latest_analysis.json'

# Thresholds for recommendations
THRESHOLDS = {
    'success_rate_low': 70,
    'memory_hit_rate_low': 50,
    'routing_compliance_low': 80,
    'token_ratio_high': 3.0,  # Output/Input ratio
    'error_rate_high': 10,    # Percentage of actions with errors
}

# Tool efficiency rankings (lower = more efficient for the task)
TOOL_EFFICIENCY = {
    'file_discovery': ['Glob', 'Bash:ls', 'Bash:find'],
    'content_search': ['Grep', 'Bash:grep', 'Bash:rg'],
    'file_read': ['Read', 'Bash:cat', 'Bash:head'],
    'file_modify': ['Edit', 'Bash:sed', 'Write'],
}


def load_metrics(days: int = 7) -> List[dict]:
    """Load metrics from daily files."""
    events = []
    cutoff = datetime.now() - timedelta(days=days)

    for file in sorted(METRICS_DIR.glob('daily_*.jsonl')):
        try:
            date_str = file.stem.replace('daily_', '')
            file_date = datetime.strptime(date_str, '%Y-%m-%d')

            if file_date >= cutoff:
                for line in file.read_text().splitlines():
                    if line.strip():
                        events.append(json.loads(line))
        except:
            continue

    return events


def load_aggregate() -> dict:
    """Load aggregate metrics."""
    agg_file = METRICS_DIR / 'aggregate.json'
    if agg_file.exists():
        return json.loads(agg_file.read_text())
    return {}


def analyze_routing(events: List[dict]) -> dict:
    """Analyze tool routing patterns and efficiency."""
    tool_use = [e for e in events if e.get('type') == 'tool_use']

    # Count tools used
    tool_counts = defaultdict(int)
    tool_with_alternatives = []
    alternative_suggestions = defaultdict(list)

    for event in tool_use:
        data = event.get('data', {})
        tool = data.get('tool', 'unknown')
        tool_counts[tool] += 1

        if data.get('had_alternative'):
            tool_with_alternatives.append(event)
            alt = data.get('alternative_suggested', 'unknown')
            alternative_suggestions[f"{tool}->{alt}"].append(event)

    # Calculate efficiency opportunities
    efficiency_issues = []

    # Check for suboptimal bash usage
    bash_count = tool_counts.get('Bash', 0)
    grep_count = tool_counts.get('Grep', 0)
    glob_count = tool_counts.get('Glob', 0)
    read_count = tool_counts.get('Read', 0)

    total_tools = sum(tool_counts.values()) or 1

    if bash_count > (grep_count + glob_count + read_count):
        efficiency_issues.append({
            'issue': 'High Bash usage compared to native tools',
            'severity': 'medium',
            'recommendation': 'Review bash patterns - Glob/Grep/Read are often more efficient',
            'data': {
                'bash_count': bash_count,
                'native_count': grep_count + glob_count + read_count,
            }
        })

    # Analyze alternative suggestions frequency
    for alt_key, alt_events in alternative_suggestions.items():
        if len(alt_events) >= 3:
            efficiency_issues.append({
                'issue': f'Repeated suboptimal pattern: {alt_key}',
                'severity': 'low',
                'recommendation': f'Consider updating routing for {alt_key.split("->")[0]}',
                'count': len(alt_events),
            })

    return {
        'total_tool_calls': len(tool_use),
        'tool_distribution': dict(tool_counts),
        'alternatives_suggested': len(tool_with_alternatives),
        'compliance_rate': round(
            (1 - len(tool_with_alternatives) / max(len(tool_use), 1)) * 100, 1
        ),
        'efficiency_issues': efficiency_issues,
    }


def analyze_tokens(events: List[dict]) -> dict:
    """Analyze token usage patterns."""
    token_events = [e for e in events if e.get('type') == 'token_count']

    if not token_events:
        return {'message': 'No token data available'}

    total_input = sum(e.get('data', {}).get('input', 0) for e in token_events)
    total_output = sum(e.get('data', {}).get('output', 0) for e in token_events)

    ratio = total_output / max(total_input, 1)

    issues = []

    if ratio > THRESHOLDS['token_ratio_high']:
        issues.append({
            'issue': 'High output/input token ratio',
            'severity': 'medium',
            'recommendation': 'Consider using more concise prompts or requesting briefer responses',
            'data': {'ratio': round(ratio, 2)},
        })

    # Analyze token usage by tool
    tool_tokens = defaultdict(lambda: {'input': 0, 'output': 0})
    for event in token_events:
        data = event.get('data', {})
        tool = data.get('tool', 'general')
        tool_tokens[tool]['input'] += data.get('input', 0)
        tool_tokens[tool]['output'] += data.get('output', 0)

    # Find highest token consumers
    token_heavy = sorted(
        tool_tokens.items(),
        key=lambda x: x[1]['input'] + x[1]['output'],
        reverse=True
    )[:5]

    return {
        'total_input': total_input,
        'total_output': total_output,
        'ratio': round(ratio, 2),
        'top_consumers': [
            {'tool': t, 'tokens': v['input'] + v['output']}
            for t, v in token_heavy
        ],
        'issues': issues,
    }


def analyze_memory(events: List[dict]) -> dict:
    """Analyze memory retrieval effectiveness."""
    memory_events = [e for e in events if e.get('type') == 'memory_retrieval']

    if not memory_events:
        return {'message': 'No memory retrieval data'}

    hits = sum(1 for e in memory_events if e.get('data', {}).get('hit'))
    misses = len(memory_events) - hits
    hit_rate = hits / max(len(memory_events), 1) * 100

    issues = []

    if hit_rate < THRESHOLDS['memory_hit_rate_low']:
        issues.append({
            'issue': 'Low memory hit rate',
            'severity': 'medium',
            'recommendation': 'Consider adding more skills or improving skill triggers',
            'data': {'hit_rate': round(hit_rate, 1)},
        })

    # Analyze what queries are missing
    missed_queries = [
        e.get('data', {}).get('query', '')
        for e in memory_events
        if not e.get('data', {}).get('hit')
    ]

    # Find common patterns in missed queries
    missed_patterns = defaultdict(int)
    for query in missed_queries:
        words = query.lower().split()
        for word in words:
            if len(word) > 3:
                missed_patterns[word] += 1

    common_misses = sorted(missed_patterns.items(), key=lambda x: x[1], reverse=True)[:5]

    if common_misses and common_misses[0][1] >= 3:
        issues.append({
            'issue': 'Repeated queries not matching skills',
            'severity': 'low',
            'recommendation': f'Consider adding skills for: {", ".join(p[0] for p in common_misses[:3])}',
        })

    return {
        'total_queries': len(memory_events),
        'hits': hits,
        'misses': misses,
        'hit_rate': round(hit_rate, 1),
        'common_missed_patterns': common_misses,
        'issues': issues,
    }


def analyze_errors(events: List[dict]) -> dict:
    """Analyze error patterns."""
    error_events = [e for e in events if e.get('type') == 'error']

    if not error_events:
        return {'total_errors': 0, 'message': 'No errors recorded'}

    error_types = defaultdict(int)
    error_tools = defaultdict(int)

    for event in error_events:
        data = event.get('data', {})
        error_types[data.get('error_type', 'unknown')] += 1
        error_tools[data.get('tool', 'unknown')] += 1

    # Calculate error rate
    tool_events = [e for e in events if e.get('type') == 'tool_use']
    error_rate = len(error_events) / max(len(tool_events), 1) * 100

    issues = []

    if error_rate > THRESHOLDS['error_rate_high']:
        issues.append({
            'issue': 'High error rate',
            'severity': 'high',
            'recommendation': 'Review error patterns - may need guardrail updates',
            'data': {'error_rate': round(error_rate, 1)},
        })

    # Find most error-prone tool
    if error_tools:
        worst_tool = max(error_tools.items(), key=lambda x: x[1])
        if worst_tool[1] >= 3:
            issues.append({
                'issue': f'Tool {worst_tool[0]} has frequent errors',
                'severity': 'medium',
                'recommendation': f'Review usage patterns for {worst_tool[0]}',
                'count': worst_tool[1],
            })

    return {
        'total_errors': len(error_events),
        'error_rate': round(error_rate, 1),
        'by_type': dict(error_types),
        'by_tool': dict(error_tools),
        'issues': issues,
    }


def analyze_sessions(events: List[dict]) -> dict:
    """Analyze session patterns."""
    session_starts = [e for e in events if e.get('type') == 'session_start']
    session_ends = [e for e in events if e.get('type') == 'session_end']
    task_outcomes = [e for e in events if e.get('type') == 'task_outcome']

    successes = sum(1 for e in task_outcomes if e.get('data', {}).get('success'))
    failures = len(task_outcomes) - successes
    success_rate = successes / max(len(task_outcomes), 1) * 100

    issues = []

    if success_rate < THRESHOLDS['success_rate_low'] and len(task_outcomes) >= 5:
        issues.append({
            'issue': 'Low task success rate',
            'severity': 'high',
            'recommendation': 'Review failed task patterns and add recovery skills',
            'data': {'success_rate': round(success_rate, 1)},
        })

    return {
        'total_sessions': len(session_starts),
        'completed_sessions': len(session_ends),
        'tasks_attempted': len(task_outcomes),
        'tasks_succeeded': successes,
        'tasks_failed': failures,
        'success_rate': round(success_rate, 1),
        'issues': issues,
    }


def generate_recommendations(analysis: dict) -> List[dict]:
    """Generate actionable recommendations from analysis."""
    recommendations = []

    # Collect all issues
    all_issues = []
    for category in ['routing', 'tokens', 'memory', 'errors', 'sessions']:
        cat_analysis = analysis.get(category, {})
        issues = cat_analysis.get('issues', [])
        for issue in issues:
            issue['category'] = category
            all_issues.append(issue)

    # Sort by severity
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    all_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))

    # Convert to recommendations
    for i, issue in enumerate(all_issues[:10], 1):  # Top 10 recommendations
        recommendations.append({
            'priority': i,
            'category': issue.get('category'),
            'severity': issue.get('severity'),
            'issue': issue.get('issue'),
            'recommendation': issue.get('recommendation'),
            'data': issue.get('data', {}),
        })

    # Add proactive recommendations if everything looks good
    if not recommendations:
        recommendations.append({
            'priority': 1,
            'category': 'general',
            'severity': 'info',
            'issue': 'No significant issues detected',
            'recommendation': 'Consider adding new skills for frequently performed tasks',
        })

    return recommendations


def run_full_analysis(days: int = 7) -> dict:
    """Run comprehensive analysis."""
    events = load_metrics(days)

    if not events:
        return {
            'status': 'no_data',
            'message': 'No metrics data found. Use the harness for a few sessions first.',
        }

    analysis = {
        'timestamp': datetime.now().isoformat(),
        'period_days': days,
        'total_events': len(events),
        'routing': analyze_routing(events),
        'tokens': analyze_tokens(events),
        'memory': analyze_memory(events),
        'errors': analyze_errors(events),
        'sessions': analyze_sessions(events),
    }

    analysis['recommendations'] = generate_recommendations(analysis)

    # Save analysis
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_FILE.write_text(json.dumps(analysis, indent=2))

    return analysis


def format_analysis(analysis: dict) -> str:
    """Format analysis for display."""
    if analysis.get('status') == 'no_data':
        return f"## Analysis\n\n{analysis.get('message')}"

    lines = [
        "## Performance Analysis",
        "",
        f"**Period**: Last {analysis.get('period_days', 7)} days",
        f"**Events Analyzed**: {analysis.get('total_events', 0):,}",
        "",
    ]

    # Routing summary
    routing = analysis.get('routing', {})
    lines.extend([
        "### Tool Routing",
        f"- Total calls: {routing.get('total_tool_calls', 0)}",
        f"- Compliance rate: {routing.get('compliance_rate', 0)}%",
        "",
    ])

    # Token summary
    tokens = analysis.get('tokens', {})
    if 'total_input' in tokens:
        lines.extend([
            "### Token Usage",
            f"- Input: {tokens.get('total_input', 0):,}",
            f"- Output: {tokens.get('total_output', 0):,}",
            f"- Ratio: {tokens.get('ratio', 0)}",
            "",
        ])

    # Memory summary
    memory = analysis.get('memory', {})
    if 'hit_rate' in memory:
        lines.extend([
            "### Memory Retrieval",
            f"- Queries: {memory.get('total_queries', 0)}",
            f"- Hit rate: {memory.get('hit_rate', 0)}%",
            "",
        ])

    # Session summary
    sessions = analysis.get('sessions', {})
    lines.extend([
        "### Sessions",
        f"- Total: {sessions.get('total_sessions', 0)}",
        f"- Success rate: {sessions.get('success_rate', 0)}%",
        "",
    ])

    # Recommendations
    recs = analysis.get('recommendations', [])
    if recs:
        lines.extend([
            "### Recommendations",
            "",
        ])
        for rec in recs[:5]:
            severity_icon = {'high': '!', 'medium': '*', 'low': '-', 'info': '>'}
            icon = severity_icon.get(rec.get('severity', 'low'), '-')
            lines.append(f"{icon} [{rec.get('category')}] {rec.get('recommendation')}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Performance analyzer')
    parser.add_argument('--analyze', '-a', nargs='?', const='all',
                       help='Run analysis (all, routing, tokens, memory, errors, sessions)')
    parser.add_argument('--recommend', '-r', action='store_true',
                       help='Generate recommendations')
    parser.add_argument('--days', '-d', type=int, default=7,
                       help='Days to analyze')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output as JSON')

    args = parser.parse_args()

    if args.analyze:
        analysis = run_full_analysis(args.days)

        if args.analyze != 'all' and args.analyze in analysis:
            # Show specific analysis
            result = {args.analyze: analysis[args.analyze]}
            if 'recommendations' in analysis:
                result['recommendations'] = [
                    r for r in analysis['recommendations']
                    if r.get('category') == args.analyze
                ]
        else:
            result = analysis

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_analysis(analysis if args.analyze == 'all' else result))

    elif args.recommend:
        analysis = run_full_analysis(args.days)
        recs = analysis.get('recommendations', [])

        if args.json:
            print(json.dumps(recs, indent=2))
        else:
            print("## Recommendations\n")
            for rec in recs:
                print(f"{rec.get('priority')}. [{rec.get('severity').upper()}] {rec.get('recommendation')}")
                if rec.get('data'):
                    print(f"   Data: {rec.get('data')}")
                print()

    else:
        # Default: show quick summary
        analysis = run_full_analysis(args.days)
        if args.json:
            print(json.dumps(analysis, indent=2))
        else:
            print(format_analysis(analysis))


if __name__ == '__main__':
    main()
