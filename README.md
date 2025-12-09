# Claude Code Harness

A self-improving wrapper for Claude Code that adds self-knowledge, persistent memory, guardrails, and meta-learning capabilities.

## Quick Start

```bash
cd ~/projects/claude-harness
./install.sh
```

## Architecture

```
Phase 1: Self-Knowledge    ← YOU ARE HERE
Phase 2: Memory Layer      (next)
Phase 3: Guardrails
Phase 4: Meta-Learning
```

### Phase 1: Self-Knowledge Layer

Eliminates exploration waste by providing immediate access to:
- Tool routing decisions
- Skill catalog
- Agent roster
- Cost optimization guidance

**Key Files:**
- `BOOTSTRAP.md` - Loaded at session start (~500 tokens)
- `tools/routing-tree.md` - Decision tree for tool selection
- `skills/index.json` - Skill catalog (grows over time)
- `agents/roster.json` - Available agents and when to use them
- `cost/model-costs.md` - Haiku/Sonnet/Opus selection guide

## Directory Structure

```
~/.claude/
├── knowledge/           # Phase 1: Self-Knowledge
│   ├── BOOTSTRAP.md     # Session start context
│   ├── tools/           # Tool references and routing
│   ├── skills/          # Skill definitions
│   ├── agents/          # Agent roster
│   └── cost/            # Cost optimization
├── memory/              # Phase 2: Persistent Memory
│   ├── episodic/        # Session outcomes
│   ├── semantic/        # Domain knowledge
│   ├── procedural/      # Skills library
│   └── working/         # Session cache
├── hooks/               # Phase 3: Guardrails
│   ├── session-start.sh # Context injection
│   └── validate-bash.py # Security validation
├── scripts/             # Utility scripts
└── metrics/             # Phase 4: Session metrics
```

## Validation

After installation, verify Phase 1 success:

1. Token usage on comparable tasks drops >40%
2. Tool selection follows routing tree
3. Can query capabilities from memory vs exploring

## Uninstall

```bash
./install.sh --uninstall
```

## Research Base

Built on empirical findings from:
- 2,303 real CLAUDE.md files (arXiv:2511.12884)
- 328 Claude Code configurations (arXiv:2511.09268)
- Forest-of-Thought, Voyager, Darwin Godel Machine patterns

## License

MIT
