#!/usr/bin/env python3
"""
Session Capture Hook for Claude Code Harness
Runs at session end (Stop hook) to capture learnings.

This hook:
1. Records session outcome to episodic memory
2. Extracts successful patterns to procedural memory (Voyager-style)
3. Updates domain knowledge with new facts

Exit codes:
  0 - Success (continue)
  1 - Error (but don't block)
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import hashlib

MEMORY_DIR = Path.home() / '.claude' / 'memory'
EPISODIC_DIR = MEMORY_DIR / 'episodic'
PROCEDURAL_DIR = MEMORY_DIR / 'procedural'
SEMANTIC_DIR = MEMORY_DIR / 'semantic'
WORKING_DIR = MEMORY_DIR / 'working'


def ensure_dirs():
    """Ensure all memory directories exist."""
    for dir_path in [EPISODIC_DIR / 'sessions', EPISODIC_DIR / 'outcomes',
                     PROCEDURAL_DIR, SEMANTIC_DIR / 'domain-knowledge', WORKING_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_session_id() -> str:
    """Generate a unique session ID."""
    today = datetime.now().strftime('%Y-%m-%d')
    sessions_dir = EPISODIC_DIR / 'sessions'

    # Count existing sessions today
    existing = list(sessions_dir.glob(f'{today}_*.json'))
    sequence = len(existing) + 1

    return f'{today}_{sequence:03d}'


def load_working_memory() -> dict:
    """Load current working memory buffer."""
    buffer_file = WORKING_DIR / 'context-buffer.json'
    if buffer_file.exists():
        try:
            return json.loads(buffer_file.read_text())
        except:
            pass
    return {}


def save_session_record(session_data: dict):
    """Save session record to episodic memory."""
    session_id = session_data.get('session_id', get_session_id())
    session_file = EPISODIC_DIR / 'sessions' / f'{session_id}.json'
    session_file.write_text(json.dumps(session_data, indent=2, default=str))
    return session_id


def append_outcome(outcome_type: str, record: dict):
    """Append to success or failure outcomes file."""
    outcome_file = EPISODIC_DIR / 'outcomes' / f'{outcome_type}.jsonl'
    with open(outcome_file, 'a') as f:
        f.write(json.dumps(record, default=str) + '\n')


def extract_skill(session_data: dict) -> Optional[dict]:
    """
    Extract a reusable skill from a successful session.
    Voyager-style: if the session was successful and efficient, create a skill.
    """
    if session_data.get('outcome') != 'success':
        return None

    # Only extract skills from sessions with clear patterns
    task = session_data.get('initial_task', '')
    if not task or len(task) < 10:
        return None

    # Generate skill ID from task hash
    skill_id = f"skill_{hashlib.md5(task.encode()).hexdigest()[:8]}"

    # Extract keywords for triggers
    task_lower = task.lower()
    triggers = []
    keywords = ['auth', 'test', 'api', 'database', 'fix', 'add', 'create',
                'implement', 'refactor', 'update', 'delete', 'remove',
                'component', 'hook', 'middleware', 'config', 'deploy']
    for kw in keywords:
        if kw in task_lower:
            triggers.append(kw)

    if not triggers:
        # Extract first few words as triggers
        triggers = task_lower.split()[:3]

    skill = {
        'skill_id': skill_id,
        'name': task[:50].replace(' ', '-').lower(),
        'description': task,
        'triggers': triggers,
        'tools_typically_used': session_data.get('tools_used', []),
        'estimated_tokens': session_data.get('tokens_used', 0),
        'success_rate': 1.0,
        'times_used': 1,
        'last_used': datetime.now().isoformat(),
        'created_from_session': session_data.get('session_id', ''),
        'key_steps': session_data.get('key_decisions', []),
    }

    return skill


def save_skill(skill: dict):
    """Save or update skill in procedural memory."""
    skills_file = PROCEDURAL_DIR / 'skills.jsonl'

    # Check if skill with similar ID exists
    existing_skills = []
    if skills_file.exists():
        for line in skills_file.read_text().splitlines():
            if line.strip():
                try:
                    existing_skills.append(json.loads(line))
                except:
                    pass

    # Update existing or append new
    updated = False
    for i, existing in enumerate(existing_skills):
        if existing.get('skill_id') == skill['skill_id']:
            # Update existing skill
            existing['times_used'] = existing.get('times_used', 0) + 1
            existing['last_used'] = skill['last_used']
            existing['success_rate'] = (
                (existing.get('success_rate', 1.0) * existing.get('times_used', 1) + 1.0) /
                (existing.get('times_used', 1) + 1)
            )
            existing_skills[i] = existing
            updated = True
            break

    if not updated:
        existing_skills.append(skill)

    # Write all skills back
    with open(skills_file, 'w') as f:
        for s in existing_skills:
            f.write(json.dumps(s, default=str) + '\n')


def clear_working_memory():
    """Clear the working memory buffer."""
    buffer_file = WORKING_DIR / 'context-buffer.json'
    if buffer_file.exists():
        buffer_file.unlink()


def capture_session(input_data: dict):
    """Main capture logic."""
    ensure_dirs()

    # Load any existing working memory
    working = load_working_memory()

    # Create session record
    session_id = get_session_id()
    now = datetime.now()

    session_data = {
        'session_id': session_id,
        'timestamp_start': working.get('started_at', now.isoformat()),
        'timestamp_end': now.isoformat(),
        'project_path': working.get('project_path', os.getcwd()),
        'initial_task': working.get('current_task', 'Unknown task'),
        'outcome': 'success',  # Default assumption; could be enhanced
        'tools_used': working.get('tools_used', []),
        'files_modified': working.get('files_modified', []),
        'decisions_made': working.get('decisions_made', []),
        'tokens_used': working.get('accumulated_context_tokens', 0),
    }

    # Save session record
    save_session_record(session_data)

    # Record outcome
    outcome_record = {
        'timestamp': now.isoformat(),
        'session_id': session_id,
        'task': session_data['initial_task'],
        'outcome': session_data['outcome'],
        'tokens': session_data['tokens_used'],
        'project': session_data['project_path'],
    }

    if session_data['outcome'] == 'success':
        append_outcome('successes', outcome_record)

        # Extract and save skill
        skill = extract_skill(session_data)
        if skill:
            save_skill(skill)
            print(f"Skill extracted: {skill['name']}", file=sys.stderr)
    else:
        append_outcome('failures', outcome_record)

    # Clear working memory
    clear_working_memory()

    print(f"Session captured: {session_id}", file=sys.stderr)


def main():
    """Entry point for hook."""
    try:
        # Try to read input from stdin (hook data)
        input_data = {}
        if not sys.stdin.isatty():
            try:
                input_data = json.load(sys.stdin)
            except:
                pass

        capture_session(input_data)
        sys.exit(0)

    except Exception as e:
        print(f"Session capture error: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block on errors


if __name__ == '__main__':
    main()
