#!/usr/bin/env python3
"""
Harness Evolution System for Claude Code Harness
Implements Darwin Godel Machine pattern for self-improvement.

Capabilities:
1. Analyze performance metrics
2. Propose improvements to harness components
3. Apply safe, validated updates
4. Track evolution history
5. Rollback if needed

Safety:
- All changes are proposed first, not auto-applied
- Changes backed up before application
- Validation required before activation
- Rollback always available

Usage:
  # Analyze and propose improvements
  python harness-evolve.py --propose

  # Apply approved changes
  python harness-evolve.py --apply <proposal_id>

  # View evolution history
  python harness-evolve.py --history

  # Rollback to previous state
  python harness-evolve.py --rollback
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import argparse
import hashlib
import re

CLAUDE_DIR = Path.home() / '.claude'
MEMORY_DIR = CLAUDE_DIR / 'memory'
KNOWLEDGE_DIR = CLAUDE_DIR / 'knowledge'
METRICS_DIR = CLAUDE_DIR / 'metrics'
EVOLUTION_DIR = METRICS_DIR / 'evolution'
PROPOSALS_FILE = EVOLUTION_DIR / 'proposals.jsonl'
HISTORY_FILE = EVOLUTION_DIR / 'history.jsonl'
BACKUP_DIR = EVOLUTION_DIR / 'backups'

# Evolution types
EVOLUTION_TYPES = {
    'skill_add': 'Add new skill to procedural memory',
    'skill_update': 'Update existing skill triggers or steps',
    'routing_update': 'Update tool routing recommendations',
    'threshold_adjust': 'Adjust warning/error thresholds',
    'knowledge_add': 'Add to domain knowledge',
    'preference_learn': 'Learn user preference',
}


def ensure_dirs():
    """Ensure evolution directories exist."""
    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def generate_proposal_id() -> str:
    """Generate unique proposal ID."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"prop_{timestamp}"


def load_analysis() -> dict:
    """Load latest performance analysis."""
    analysis_file = METRICS_DIR / 'latest_analysis.json'
    if analysis_file.exists():
        return json.loads(analysis_file.read_text())
    return {}


def load_skills() -> List[dict]:
    """Load current skills."""
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


def load_proposals() -> List[dict]:
    """Load pending proposals."""
    proposals = []
    if PROPOSALS_FILE.exists():
        for line in PROPOSALS_FILE.read_text().splitlines():
            if line.strip():
                try:
                    proposals.append(json.loads(line))
                except:
                    pass
    return proposals


def save_proposal(proposal: dict):
    """Save a proposal."""
    ensure_dirs()
    with open(PROPOSALS_FILE, 'a') as f:
        f.write(json.dumps(proposal) + '\n')


def load_history() -> List[dict]:
    """Load evolution history."""
    history = []
    if HISTORY_FILE.exists():
        for line in HISTORY_FILE.read_text().splitlines():
            if line.strip():
                try:
                    history.append(json.loads(line))
                except:
                    pass
    return history


def save_history(entry: dict):
    """Save history entry."""
    ensure_dirs()
    with open(HISTORY_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')


def backup_file(file_path: Path) -> Optional[str]:
    """Backup a file before modification."""
    if not file_path.exists():
        return None

    ensure_dirs()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{file_path.name}.{timestamp}.bak"
    backup_path = BACKUP_DIR / backup_name

    shutil.copy(file_path, backup_path)
    return str(backup_path)


def propose_skill_from_pattern(pattern: str, count: int) -> Optional[dict]:
    """Propose a new skill based on common pattern."""
    # Generate skill from pattern
    skill_id = f"skill_auto_{hashlib.md5(pattern.encode()).hexdigest()[:8]}"

    # Check if similar skill exists
    skills = load_skills()
    for skill in skills:
        for trigger in skill.get('triggers', []):
            if pattern.lower() in trigger.lower():
                return None  # Similar skill exists

    return {
        'type': 'skill_add',
        'data': {
            'skill_id': skill_id,
            'name': f"auto-{pattern.replace(' ', '-')}",
            'description': f"Auto-generated skill for: {pattern}",
            'triggers': [pattern, pattern.replace('-', ' ')],
            'prerequisites': [],
            'key_steps': ['Step 1: TBD - Fill in based on successful patterns'],
            'tools_typically_used': ['Read', 'Edit', 'Bash'],
            'estimated_tokens': 2000,
            'success_rate': 0.0,
            'times_used': 0,
            'last_used': None,
            'created_from_session': 'auto_evolution',
        },
        'reason': f'Pattern "{pattern}" appeared {count} times without matching skill',
    }


def propose_routing_update(tool: str, alternative: str, count: int) -> dict:
    """Propose routing update based on frequent alternatives."""
    return {
        'type': 'routing_update',
        'data': {
            'from_tool': tool,
            'to_tool': alternative,
            'pattern': f'auto-detected from {count} occurrences',
        },
        'reason': f'{alternative} was suggested {count} times when {tool} was used',
    }


def propose_threshold_adjustment(metric: str, current: float, suggested: float, reason: str) -> dict:
    """Propose threshold adjustment."""
    return {
        'type': 'threshold_adjust',
        'data': {
            'metric': metric,
            'current_value': current,
            'suggested_value': suggested,
        },
        'reason': reason,
    }


def generate_proposals() -> List[dict]:
    """Generate improvement proposals from analysis."""
    analysis = load_analysis()
    proposals = []

    if not analysis or analysis.get('status') == 'no_data':
        return [{
            'id': generate_proposal_id(),
            'type': 'info',
            'message': 'Insufficient data for proposals. Continue using the harness.',
        }]

    # 1. Propose skills for missed patterns
    memory = analysis.get('memory', {})
    missed_patterns = memory.get('common_missed_patterns', [])

    for pattern, count in missed_patterns:
        if count >= 3:
            skill_proposal = propose_skill_from_pattern(pattern, count)
            if skill_proposal:
                skill_proposal['id'] = generate_proposal_id()
                skill_proposal['timestamp'] = datetime.now().isoformat()
                skill_proposal['status'] = 'pending'
                proposals.append(skill_proposal)

    # 2. Propose routing updates
    routing = analysis.get('routing', {})
    for issue in routing.get('efficiency_issues', []):
        if 'pattern' in issue.get('issue', '').lower():
            # Extract tool pair from issue
            match = re.search(r'(\w+)->(\w+)', issue.get('issue', ''))
            if match:
                from_tool, to_tool = match.groups()
                proposal = propose_routing_update(from_tool, to_tool, issue.get('count', 0))
                proposal['id'] = generate_proposal_id()
                proposal['timestamp'] = datetime.now().isoformat()
                proposal['status'] = 'pending'
                proposals.append(proposal)

    # 3. Check for threshold adjustments needed
    sessions = analysis.get('sessions', {})
    success_rate = sessions.get('success_rate', 100)

    if success_rate < 60:
        # Very low success rate - suggest lowering expectations or adding skills
        proposals.append({
            'id': generate_proposal_id(),
            'timestamp': datetime.now().isoformat(),
            'status': 'pending',
            'type': 'threshold_adjust',
            'data': {
                'metric': 'success_rate_low',
                'current_value': 70,
                'suggested_value': 60,
            },
            'reason': f'Current success rate ({success_rate}%) is below threshold',
        })

    # 4. Add proposals for high-value recommendations
    for rec in analysis.get('recommendations', []):
        if rec.get('severity') == 'high':
            proposals.append({
                'id': generate_proposal_id(),
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',
                'type': 'manual_review',
                'data': rec,
                'reason': 'High severity issue requiring manual review',
            })

    return proposals


def apply_proposal(proposal_id: str, dry_run: bool = True) -> Tuple[bool, str]:
    """Apply a specific proposal."""
    proposals = load_proposals()

    # Find the proposal
    proposal = None
    for p in proposals:
        if p.get('id') == proposal_id:
            proposal = p
            break

    if not proposal:
        return False, f"Proposal {proposal_id} not found"

    if proposal.get('status') == 'applied':
        return False, f"Proposal {proposal_id} already applied"

    prop_type = proposal.get('type')

    if dry_run:
        return True, f"[DRY RUN] Would apply {prop_type}: {proposal.get('reason')}"

    # Apply based on type
    if prop_type == 'skill_add':
        return apply_skill_add(proposal)
    elif prop_type == 'routing_update':
        return apply_routing_update(proposal)
    elif prop_type == 'threshold_adjust':
        return apply_threshold_adjust(proposal)
    elif prop_type == 'manual_review':
        return False, "Manual review items cannot be auto-applied"
    else:
        return False, f"Unknown proposal type: {prop_type}"


def apply_skill_add(proposal: dict) -> Tuple[bool, str]:
    """Apply skill addition."""
    skills_file = MEMORY_DIR / 'procedural' / 'skills.jsonl'

    # Backup
    backup_path = backup_file(skills_file)

    # Add skill
    skill = proposal.get('data', {})
    skills_file.parent.mkdir(parents=True, exist_ok=True)

    with open(skills_file, 'a') as f:
        f.write(json.dumps(skill) + '\n')

    # Record in history
    save_history({
        'timestamp': datetime.now().isoformat(),
        'proposal_id': proposal.get('id'),
        'type': 'skill_add',
        'skill_id': skill.get('skill_id'),
        'backup': backup_path,
    })

    # Update proposal status
    update_proposal_status(proposal.get('id'), 'applied')

    return True, f"Added skill: {skill.get('name')}"


def apply_routing_update(proposal: dict) -> Tuple[bool, str]:
    """Apply routing update."""
    # This would update pre-flight.py or routing config
    # For safety, we just record the recommendation

    save_history({
        'timestamp': datetime.now().isoformat(),
        'proposal_id': proposal.get('id'),
        'type': 'routing_update',
        'data': proposal.get('data'),
        'note': 'Routing update recorded - manual review recommended',
    })

    update_proposal_status(proposal.get('id'), 'recorded')

    return True, f"Routing update recorded: {proposal.get('data', {}).get('from_tool')} -> {proposal.get('data', {}).get('to_tool')}"


def apply_threshold_adjust(proposal: dict) -> Tuple[bool, str]:
    """Apply threshold adjustment."""
    # Record for manual application
    save_history({
        'timestamp': datetime.now().isoformat(),
        'proposal_id': proposal.get('id'),
        'type': 'threshold_adjust',
        'data': proposal.get('data'),
        'note': 'Threshold adjustment recorded - manual update recommended',
    })

    update_proposal_status(proposal.get('id'), 'recorded')

    return True, f"Threshold adjustment recorded: {proposal.get('data', {}).get('metric')}"


def update_proposal_status(proposal_id: str, status: str):
    """Update status of a proposal."""
    proposals = load_proposals()

    # Rewrite file with updated status
    updated = []
    for p in proposals:
        if p.get('id') == proposal_id:
            p['status'] = status
            p['updated_at'] = datetime.now().isoformat()
        updated.append(p)

    with open(PROPOSALS_FILE, 'w') as f:
        for p in updated:
            f.write(json.dumps(p) + '\n')


def rollback_last() -> Tuple[bool, str]:
    """Rollback last applied change."""
    history = load_history()

    if not history:
        return False, "No history to rollback"

    last = history[-1]
    backup_path = last.get('backup')

    if not backup_path or not Path(backup_path).exists():
        return False, "No backup available for rollback"

    # Determine original file
    if last.get('type') == 'skill_add':
        original_file = MEMORY_DIR / 'procedural' / 'skills.jsonl'
    else:
        return False, f"Rollback not supported for type: {last.get('type')}"

    # Restore from backup
    shutil.copy(backup_path, original_file)

    # Record rollback
    save_history({
        'timestamp': datetime.now().isoformat(),
        'type': 'rollback',
        'rolled_back': last.get('proposal_id'),
        'restored_from': backup_path,
    })

    return True, f"Rolled back {last.get('type')} from {last.get('timestamp')}"


def format_proposals(proposals: List[dict]) -> str:
    """Format proposals for display."""
    if not proposals:
        return "No proposals generated. The harness is performing well!"

    lines = [
        "## Evolution Proposals",
        "",
        f"Generated {len(proposals)} proposal(s):",
        "",
    ]

    for p in proposals:
        status_icon = {'pending': '*', 'applied': '+', 'recorded': '>', 'rejected': 'x'}
        icon = status_icon.get(p.get('status', 'pending'), '?')

        lines.append(f"{icon} **{p.get('id')}** [{p.get('type')}]")
        lines.append(f"  Reason: {p.get('reason', 'N/A')}")
        if p.get('data'):
            lines.append(f"  Data: {json.dumps(p.get('data'))[:100]}...")
        lines.append("")

    lines.extend([
        "---",
        "To apply: python harness-evolve.py --apply <proposal_id>",
        "To apply all pending: python harness-evolve.py --apply-all",
    ])

    return '\n'.join(lines)


def format_history(history: List[dict]) -> str:
    """Format history for display."""
    if not history:
        return "No evolution history yet."

    lines = [
        "## Evolution History",
        "",
    ]

    for entry in history[-10:]:  # Last 10 entries
        lines.append(f"- [{entry.get('timestamp', 'unknown')[:10]}] {entry.get('type')}")
        if entry.get('proposal_id'):
            lines.append(f"  Proposal: {entry.get('proposal_id')}")
        if entry.get('note'):
            lines.append(f"  Note: {entry.get('note')}")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Harness evolution system')
    parser.add_argument('--propose', '-p', action='store_true', help='Generate proposals')
    parser.add_argument('--apply', '-a', type=str, help='Apply a proposal')
    parser.add_argument('--apply-all', action='store_true', help='Apply all pending proposals')
    parser.add_argument('--history', '-H', action='store_true', help='Show evolution history')
    parser.add_argument('--rollback', '-r', action='store_true', help='Rollback last change')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Dry run (no changes)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if args.propose:
        proposals = generate_proposals()

        # Save proposals
        for p in proposals:
            if p.get('status') == 'pending':
                save_proposal(p)

        if args.json:
            print(json.dumps(proposals, indent=2))
        else:
            print(format_proposals(proposals))

    elif args.apply:
        success, message = apply_proposal(args.apply, dry_run=args.dry_run)
        if args.json:
            print(json.dumps({'success': success, 'message': message}))
        else:
            print(f"{'Success' if success else 'Failed'}: {message}")

    elif args.apply_all:
        proposals = load_proposals()
        pending = [p for p in proposals if p.get('status') == 'pending']

        results = []
        for p in pending:
            if p.get('type') not in ['manual_review', 'info']:
                success, message = apply_proposal(p.get('id'), dry_run=args.dry_run)
                results.append({'id': p.get('id'), 'success': success, 'message': message})

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                print(f"[{r['id']}] {'Success' if r['success'] else 'Failed'}: {r['message']}")

    elif args.history:
        history = load_history()
        if args.json:
            print(json.dumps(history, indent=2))
        else:
            print(format_history(history))

    elif args.rollback:
        success, message = rollback_last()
        if args.json:
            print(json.dumps({'success': success, 'message': message}))
        else:
            print(f"{'Success' if success else 'Failed'}: {message}")

    else:
        # Default: show current proposals
        proposals = load_proposals()
        pending = [p for p in proposals if p.get('status') == 'pending']

        if args.json:
            print(json.dumps(pending, indent=2))
        else:
            if pending:
                print(format_proposals(pending))
            else:
                print("No pending proposals. Run --propose to generate new proposals.")


if __name__ == '__main__':
    main()
