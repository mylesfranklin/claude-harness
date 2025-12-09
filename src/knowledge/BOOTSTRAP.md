# Claude Code Harness v1.0

> **Load Time**: ~500 tokens | **Purpose**: Eliminate exploration waste

---

## Quick Reference

### Built-in Tools (always available)
| Tool | Purpose | When to Use |
|------|---------|-------------|
| `Read` | Read file contents | Single file, need full content |
| `Write` | Create new file | New file only (prefer Edit for existing) |
| `Edit` | Modify existing file | Any file modification |
| `Glob` | Find files by pattern | `**/*.ts`, `src/**/*.md` |
| `Grep` | Search file contents | Find text/regex across files |
| `Bash` | Run shell commands | git, npm, system commands |
| `Task` | Spawn sub-agents | Complex multi-step work |
| `WebFetch` | Fetch URL content | Documentation, external data |
| `WebSearch` | Search the web | Current events, external info |

### MCP Servers (check availability first)
Run `claude mcp list` to see active servers. Common ones:
- **firecrawl**: Web scraping, search
- **perplexity**: AI-powered search
- **github**: Repository operations
- **supabase**: Database operations
- **exa**: Code-aware web search

### Available Skills
<!-- Auto-populated from skills/index.json -->
*No skills registered yet. Add skills to `~/.claude/knowledge/skills/`*

### Available Agents
<!-- Auto-populated from agents/roster.json -->
| Agent | Use For | Model |
|-------|---------|-------|
| `Explore` | Codebase discovery | Sonnet |
| `Plan` | Implementation design | Sonnet |
| `claude-code-guide` | Claude Code questions | Haiku |

---

## Routing Rules (follow in order)

```
1. SKILL CHECK
   └─ Is there a skill for this task?
      └─ YES → Load skill from ~/.claude/knowledge/skills/[name]/SKILL.md
      └─ NO → Continue to step 2

2. MCP CHECK
   └─ Is there an MCP tool that does this directly?
      └─ YES → Use MCP tool (cheaper than exploration)
      └─ NO → Continue to step 3

3. MEMORY CHECK
   └─ Have I solved similar before?
      └─ YES → Check ~/.claude/memory/procedural/
      └─ NO → Continue to step 4

4. BUILTIN CHECK
   └─ Can a builtin tool do this?
      └─ Glob for file finding
      └─ Grep for content search
      └─ Read for file contents
      └─ NO → Continue to step 5

5. EXPLORATION (last resort)
   └─ Estimate tokens before proceeding
   └─ If estimate > 1000 tokens, consider asking user first
   └─ Flag exploration in response
```

---

## Cost Optimization

### Model Selection
| Task Type | Model | Cost | Example |
|-----------|-------|------|---------|
| Verification | Haiku | $1/MTok | "Does this file exist?" |
| Simple generation | Haiku | $1/MTok | "Add a console.log" |
| Code generation | Sonnet | $3/MTok | "Implement this function" |
| Complex reasoning | Opus | $15/MTok | "Design architecture" |
| Multi-step synthesis | Opus | $15/MTok | "Refactor entire module" |

### Token Efficiency Rules
1. **Parallel calls**: Make independent tool calls in same message
2. **Glob before Read**: Find files first, then read only what's needed
3. **Grep over Read**: Search content instead of reading entire files
4. **Batch operations**: Combine related edits into fewer Edit calls
5. **Agent delegation**: Use Task tool for exploration-heavy work

---

## Anti-Patterns (NEVER do these)

| Anti-Pattern | Why It's Bad | Do This Instead |
|--------------|--------------|-----------------|
| `ls` then `cat` each file | O(n) tool calls | `Glob` then selective `Read` |
| Read entire codebase | Token explosion | `Grep` for specific patterns |
| Generate from scratch | Ignores existing code | Check for templates/patterns first |
| Sequential file reads | Slow, expensive | Parallel `Read` calls |
| Opus for simple tasks | 15x cost overhead | Use Haiku for verification |
| Exploring without estimate | Unbounded cost | Estimate tokens first |
| Ignoring skill catalog | Reinventing solutions | Check skills/index.json |

---

## Session Protocol

### On Session Start
1. This file is automatically loaded
2. Check for relevant memory in `~/.claude/memory/`
3. Identify task type for model selection
4. Check skill catalog for existing solutions

### During Session
1. Follow routing rules for every action
2. Track tool usage for metrics
3. Flag when exploring (for later optimization)
4. Capture successful patterns

### On Session End
1. Log session metrics to `~/.claude/metrics/`
2. Save successful patterns to procedural memory
3. Note failures for review

---

## Quick Commands

```bash
# Check available MCP servers
claude mcp list

# View skill catalog
cat ~/.claude/knowledge/skills/index.json

# View recent successful patterns
tail -5 ~/.claude/memory/procedural/skills.jsonl

# Analyze session metrics
python3 ~/.claude/scripts/analyze-metrics.py
```

---

**Version**: 1.0.0
**Last Updated**: 2025-12-09
