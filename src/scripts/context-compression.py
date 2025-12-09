#!/usr/bin/env python3
"""
Context Compression Utility for Claude Code Harness
Based on Acon research (arXiv:2510.00615) - 95% accuracy with 60-80% token reduction.

Strategy:
1. Preserve head (first N messages) - initial setup/context
2. Preserve tail (last M messages) - recent relevant context
3. Summarize middle section - compress without losing key info
4. Maintain persistent summary that grows incrementally

Usage:
  # Compress a session transcript
  python context-compression.py --input session.json --output compressed.json

  # Generate summary of current working memory
  python context-compression.py --summarize
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse
import re

MEMORY_DIR = Path.home() / '.claude' / 'memory'
WORKING_DIR = MEMORY_DIR / 'working'
SUMMARY_FILE = WORKING_DIR / 'persistent-summary.json'


def estimate_tokens(text: str) -> int:
    """Rough token estimate (chars / 4)."""
    return len(text) // 4


def extract_key_points(messages: List[Dict]) -> List[str]:
    """
    Extract key points from a list of messages.
    Identifies: decisions, actions taken, errors, important findings.
    """
    key_points = []

    keywords = {
        'decision': ['decided', 'chose', 'using', 'will use', 'going with'],
        'action': ['created', 'modified', 'deleted', 'added', 'removed', 'fixed'],
        'error': ['error', 'failed', 'issue', 'problem', 'bug'],
        'finding': ['found', 'discovered', 'noticed', 'identified'],
    }

    for msg in messages:
        content = msg.get('content', '')
        if isinstance(content, list):
            # Handle structured content
            content = ' '.join(str(c) for c in content if isinstance(c, str))

        content_lower = content.lower()

        for category, kws in keywords.items():
            for kw in kws:
                if kw in content_lower:
                    # Extract the sentence containing the keyword
                    sentences = re.split(r'[.!?]', content)
                    for sent in sentences:
                        if kw in sent.lower() and len(sent.strip()) > 20:
                            key_points.append(f"[{category}] {sent.strip()[:100]}")
                            break
                    break

    return list(set(key_points))[:10]  # Dedupe and limit


def compress_messages(
    messages: List[Dict],
    head_count: int = 5,
    tail_count: int = 10,
    max_tokens: int = 4000
) -> Dict:
    """
    Compress a message list while preserving important context.

    Returns:
        {
            'head': [...],      # First N messages (setup)
            'summary': '...',   # Compressed middle section
            'tail': [...],      # Last M messages (recent)
            'key_points': [...], # Extracted key points
            'original_count': N,
            'compressed_count': M,
            'token_reduction': X%
        }
    """
    if not messages:
        return {'head': [], 'summary': '', 'tail': [], 'key_points': []}

    total_messages = len(messages)

    # If small enough, don't compress
    total_tokens = sum(estimate_tokens(str(m)) for m in messages)
    if total_tokens <= max_tokens:
        return {
            'head': messages,
            'summary': '',
            'tail': [],
            'key_points': [],
            'original_count': total_messages,
            'compressed_count': total_messages,
            'token_reduction': 0,
        }

    # Split into head, middle, tail
    head = messages[:head_count]
    tail = messages[-tail_count:] if len(messages) > head_count + tail_count else []
    middle = messages[head_count:-tail_count] if tail else messages[head_count:]

    # Extract key points from middle
    key_points = extract_key_points(middle)

    # Create summary of middle section
    middle_summary_parts = []

    # Count tool uses
    tool_counts = {}
    for msg in middle:
        content = str(msg.get('content', ''))
        for tool in ['Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash', 'Task']:
            if tool in content:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1

    if tool_counts:
        tools_str = ', '.join(f"{t}: {c}" for t, c in tool_counts.items())
        middle_summary_parts.append(f"Tools used: {tools_str}")

    # Count file operations
    file_patterns = re.findall(r'["\']([^"\']+\.[a-z]+)["\']', str(middle))
    if file_patterns:
        unique_files = list(set(file_patterns))[:5]
        middle_summary_parts.append(f"Files touched: {', '.join(unique_files)}")

    # Add key points
    if key_points:
        middle_summary_parts.append("Key points:")
        middle_summary_parts.extend(f"  - {kp}" for kp in key_points[:5])

    summary = '\n'.join(middle_summary_parts) if middle_summary_parts else f"({len(middle)} messages summarized)"

    # Calculate compression
    compressed_tokens = (
        sum(estimate_tokens(str(m)) for m in head) +
        estimate_tokens(summary) +
        sum(estimate_tokens(str(m)) for m in tail)
    )
    reduction = ((total_tokens - compressed_tokens) / total_tokens) * 100 if total_tokens > 0 else 0

    return {
        'head': head,
        'summary': summary,
        'tail': tail,
        'key_points': key_points,
        'original_count': total_messages,
        'compressed_count': head_count + 1 + len(tail),
        'token_reduction': round(reduction, 1),
    }


def load_persistent_summary() -> Dict:
    """Load the persistent summary from previous compressions."""
    if SUMMARY_FILE.exists():
        try:
            return json.loads(SUMMARY_FILE.read_text())
        except:
            pass
    return {
        'summaries': [],
        'accumulated_key_points': [],
        'last_updated': None,
    }


def save_persistent_summary(summary: Dict):
    """Save the persistent summary."""
    WORKING_DIR.mkdir(parents=True, exist_ok=True)
    summary['last_updated'] = datetime.now().isoformat()
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2, default=str))


def update_persistent_summary(new_summary: str, new_key_points: List[str]):
    """Add to the persistent summary."""
    persistent = load_persistent_summary()

    # Add new summary
    persistent['summaries'].append({
        'timestamp': datetime.now().isoformat(),
        'summary': new_summary,
    })

    # Keep only last 5 summaries
    persistent['summaries'] = persistent['summaries'][-5:]

    # Accumulate key points (deduped)
    existing_points = set(persistent['accumulated_key_points'])
    for point in new_key_points:
        existing_points.add(point)
    persistent['accumulated_key_points'] = list(existing_points)[-20:]

    save_persistent_summary(persistent)


def summarize_working_memory() -> str:
    """Generate a summary of current working memory state."""
    buffer_file = WORKING_DIR / 'context-buffer.json'

    if not buffer_file.exists():
        return "No working memory found."

    buffer = json.loads(buffer_file.read_text())

    lines = [
        "## Working Memory Summary",
        "",
        f"**Session started**: {buffer.get('started_at', 'Unknown')}",
        f"**Project**: {buffer.get('project_path', 'Unknown')}",
        f"**Current task**: {buffer.get('current_task', 'Not set')}",
        "",
    ]

    tools = buffer.get('tools_used', [])
    if tools:
        lines.append(f"**Tools used**: {', '.join(tools)}")

    files = buffer.get('files_modified', [])
    if files:
        lines.append(f"**Files modified**: {len(files)}")
        for f in files[:5]:
            lines.append(f"  - {f}")

    decisions = buffer.get('decisions_made', [])
    if decisions:
        lines.append("")
        lines.append("**Decisions**:")
        for d in decisions[-5:]:
            dec = d.get('decision', d) if isinstance(d, dict) else d
            lines.append(f"  - {dec}")

    tokens = buffer.get('accumulated_context_tokens', 0)
    if tokens:
        lines.append("")
        lines.append(f"**Estimated tokens used**: {tokens:,}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Context compression utility')
    parser.add_argument('--input', '-i', help='Input JSON file with messages')
    parser.add_argument('--output', '-o', help='Output JSON file for compressed result')
    parser.add_argument('--summarize', '-s', action='store_true', help='Summarize working memory')
    parser.add_argument('--head', type=int, default=5, help='Messages to keep at head')
    parser.add_argument('--tail', type=int, default=10, help='Messages to keep at tail')
    parser.add_argument('--max-tokens', type=int, default=4000, help='Max tokens after compression')

    args = parser.parse_args()

    if args.summarize:
        print(summarize_working_memory())
        return

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        messages = json.loads(input_path.read_text())
        if not isinstance(messages, list):
            messages = messages.get('messages', [])

        result = compress_messages(
            messages,
            head_count=args.head,
            tail_count=args.tail,
            max_tokens=args.max_tokens
        )

        # Update persistent summary
        if result['summary']:
            update_persistent_summary(result['summary'], result['key_points'])

        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2, default=str))
            print(f"Compressed output written to {args.output}")
        else:
            print(json.dumps(result, indent=2, default=str))

        print(f"\nCompression: {result['original_count']} -> {result['compressed_count']} messages")
        print(f"Token reduction: {result['token_reduction']}%")
    else:
        # Default: show working memory summary
        print(summarize_working_memory())


if __name__ == '__main__':
    main()
