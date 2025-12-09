#!/usr/bin/env python3
"""
Memory Retrieval System for Claude Code Harness
Retrieves relevant memory at session start based on task/context.

Usage:
  # Retrieve memory for a task
  python memory-retrieval.py --task "implement user authentication"

  # Retrieve memory for current project
  python memory-retrieval.py --project "/path/to/project"

  # Get recent outcomes
  python memory-retrieval.py --recent 5

Output: Formatted markdown suitable for context injection
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
import argparse
import re

MEMORY_DIR = Path.home() / '.claude' / 'memory'
EPISODIC_DIR = MEMORY_DIR / 'episodic'
PROCEDURAL_DIR = MEMORY_DIR / 'procedural'
SEMANTIC_DIR = MEMORY_DIR / 'semantic'


def load_skills() -> List[dict]:
    """Load all skills from procedural memory."""
    skills_file = PROCEDURAL_DIR / 'skills.jsonl'
    skills = []

    if skills_file.exists():
        for line in skills_file.read_text().splitlines():
            if line.strip():
                try:
                    skills.append(json.loads(line))
                except:
                    pass

    return skills


def load_user_profile() -> dict:
    """Load user profile from semantic memory."""
    profile_file = SEMANTIC_DIR / 'user-profile.json'

    if profile_file.exists():
        try:
            return json.loads(profile_file.read_text())
        except:
            pass

    return {'preferences': {}, 'context': {}}


def load_domain_knowledge(domain: str) -> dict:
    """Load domain-specific knowledge."""
    domain_file = SEMANTIC_DIR / 'domain-knowledge' / f'{domain}.json'

    if domain_file.exists():
        try:
            return json.loads(domain_file.read_text())
        except:
            pass

    return {'facts': [], 'common_patterns': [], 'anti_patterns': []}


def load_recent_outcomes(n: int = 5, outcome_type: str = 'successes') -> List[dict]:
    """Load recent outcomes from episodic memory."""
    outcome_file = EPISODIC_DIR / 'outcomes' / f'{outcome_type}.jsonl'
    outcomes = []

    if outcome_file.exists():
        lines = outcome_file.read_text().splitlines()
        for line in lines[-n:]:  # Last n entries
            if line.strip():
                try:
                    outcomes.append(json.loads(line))
                except:
                    pass

    return outcomes


def match_skills(task: str, skills: List[dict]) -> List[dict]:
    """
    Match task against skills using keyword triggers.
    Returns skills sorted by relevance score.
    """
    if not task:
        return []

    task_lower = task.lower()
    task_words = set(re.findall(r'\w+', task_lower))

    scored_skills = []

    for skill in skills:
        triggers = skill.get('triggers', [])
        description = skill.get('description', '').lower()

        # Calculate match score
        trigger_matches = sum(1 for t in triggers if t.lower() in task_lower)
        word_matches = sum(1 for w in task_words if w in description)

        score = trigger_matches * 2 + word_matches

        if score > 0:
            scored_skills.append((score, skill))

    # Sort by score descending
    scored_skills.sort(key=lambda x: x[0], reverse=True)

    return [skill for _, skill in scored_skills[:3]]  # Top 3


def detect_domains(task: str) -> List[str]:
    """Detect relevant domains from task description."""
    task_lower = task.lower()

    domain_keywords = {
        'auth': ['auth', 'login', 'jwt', 'token', 'session', 'password', 'user'],
        'api': ['api', 'endpoint', 'route', 'rest', 'graphql', 'request', 'response'],
        'database': ['database', 'db', 'sql', 'query', 'postgres', 'mysql', 'mongo', 'migration'],
        'testing': ['test', 'jest', 'coverage', 'mock', 'spec', 'unit', 'integration'],
        'frontend': ['react', 'component', 'ui', 'css', 'html', 'dom', 'render'],
        'deployment': ['deploy', 'docker', 'ci', 'cd', 'pipeline', 'build', 'release'],
    }

    detected = []
    for domain, keywords in domain_keywords.items():
        if any(kw in task_lower for kw in keywords):
            detected.append(domain)

    return detected


def format_skill(skill: dict) -> str:
    """Format a skill for context injection."""
    lines = [
        f"### Skill: {skill.get('name', 'Unknown')}",
        f"**Description**: {skill.get('description', '')}",
        f"**Success Rate**: {skill.get('success_rate', 0):.0%} ({skill.get('times_used', 0)} uses)",
        "",
    ]

    steps = skill.get('key_steps', [])
    if steps:
        lines.append("**Steps**:")
        for step in steps[:5]:  # Limit to 5 steps
            lines.append(f"- {step}")
        lines.append("")

    tools = skill.get('tools_typically_used', [])
    if tools:
        lines.append(f"**Tools**: {', '.join(tools)}")

    return '\n'.join(lines)


def format_outcomes(outcomes: List[dict], outcome_type: str) -> str:
    """Format recent outcomes for context injection."""
    if not outcomes:
        return ""

    lines = [f"### Recent {outcome_type.title()}"]

    for o in outcomes[-3:]:  # Last 3
        task = o.get('task', 'Unknown')[:50]
        date = o.get('timestamp', '')[:10]
        lines.append(f"- [{date}] {task}")

    return '\n'.join(lines)


def format_domain_knowledge(domain: str, knowledge: dict) -> str:
    """Format domain knowledge for context injection."""
    if not knowledge.get('facts') and not knowledge.get('common_patterns'):
        return ""

    lines = [f"### Domain: {domain.title()}"]

    facts = knowledge.get('facts', [])[:3]
    if facts:
        for f in facts:
            fact_text = f.get('fact', f) if isinstance(f, dict) else f
            lines.append(f"- {fact_text}")

    anti = knowledge.get('anti_patterns', [])[:2]
    if anti:
        lines.append("")
        lines.append("**Avoid**:")
        for a in anti:
            lines.append(f"- {a}")

    return '\n'.join(lines)


def retrieve_memory(task: str = None, project: str = None, recent: int = 5) -> str:
    """
    Main retrieval function. Returns formatted markdown context.
    """
    sections = []

    # Header
    sections.append("## Relevant Memory Context")
    sections.append("")

    # 1. Load and match skills if task provided
    if task:
        skills = load_skills()
        matched = match_skills(task, skills)

        if matched:
            sections.append("### Matched Skills")
            sections.append("")
            for skill in matched:
                sections.append(format_skill(skill))
            sections.append("")

    # 2. Load domain knowledge
    if task:
        domains = detect_domains(task)
        for domain in domains[:2]:  # Limit to 2 domains
            knowledge = load_domain_knowledge(domain)
            formatted = format_domain_knowledge(domain, knowledge)
            if formatted:
                sections.append(formatted)
                sections.append("")

    # 3. Load recent outcomes
    successes = load_recent_outcomes(recent, 'successes')
    if successes:
        sections.append(format_outcomes(successes, 'successes'))
        sections.append("")

    failures = load_recent_outcomes(3, 'failures')
    if failures:
        sections.append(format_outcomes(failures, 'failures'))
        sections.append("")

    # 4. Load user preferences summary
    profile = load_user_profile()
    prefs = profile.get('preferences', {})
    if prefs:
        sections.append("### User Preferences")
        code_style = prefs.get('code_style', {})
        if code_style:
            indent = code_style.get('indent', 'spaces')
            size = code_style.get('indent_size', 2)
            sections.append(f"- Code style: {size} {indent}")
        comm = prefs.get('communication', {})
        if comm.get('ask_before_major_changes'):
            sections.append("- Ask before major changes: Yes")
        sections.append("")

    # If nothing found, return minimal message
    if len(sections) <= 2:
        return "## Memory Context\n\nNo relevant memory found for this task.\n"

    return '\n'.join(sections)


def main():
    parser = argparse.ArgumentParser(description='Retrieve relevant memory')
    parser.add_argument('--task', '-t', help='Task description to match against')
    parser.add_argument('--project', '-p', help='Project path for context')
    parser.add_argument('--recent', '-r', type=int, default=5, help='Number of recent outcomes')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON instead of markdown')

    args = parser.parse_args()

    result = retrieve_memory(
        task=args.task,
        project=args.project,
        recent=args.recent
    )

    if args.json:
        # Output structured data
        output = {
            'task': args.task,
            'matched_skills': [s for s in match_skills(args.task or '', load_skills())],
            'domains': detect_domains(args.task or ''),
            'recent_successes': load_recent_outcomes(args.recent, 'successes'),
            'recent_failures': load_recent_outcomes(3, 'failures'),
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print(result)


if __name__ == '__main__':
    main()
