# Model Costs Reference

> **Purpose**: Guide model selection for cost efficiency
> **Updated**: December 2025

---

## Claude Models

| Model | Input Cost | Output Cost | Best For |
|-------|-----------|-------------|----------|
| **Haiku** | $0.25/MTok | $1.25/MTok | Verification, simple tasks |
| **Sonnet** | $3/MTok | $15/MTok | Code generation, analysis |
| **Opus** | $15/MTok | $75/MTok | Complex reasoning, synthesis |

*MTok = Million tokens*

---

## Task-to-Model Mapping

### Use Haiku ($1/MTok effective)
- Simple validation ("does X exist?")
- Single-line fixes
- Format checking
- Simple question answering
- Quick classifications
- Verification steps

### Use Sonnet ($3/MTok effective)
- Code generation
- Multi-file edits
- Test writing
- Documentation generation
- Standard refactoring
- Most everyday tasks

### Use Opus ($15/MTok effective)
- Complex architectural decisions
- Multi-step reasoning chains
- Novel problem solving
- Cross-cutting refactors
- Security analysis
- Performance optimization design

---

## Cost Decision Tree

```
Is this a simple yes/no or lookup?
├─ YES → Haiku
└─ NO ↓

Does it require code generation?
├─ YES ↓
│   Is it a complex architectural change?
│   ├─ YES → Opus
│   └─ NO → Sonnet
└─ NO ↓

Does it require multi-step reasoning?
├─ YES → Opus
└─ NO → Sonnet
```

---

## Token Estimation by Operation

| Operation | Typical Input | Typical Output |
|-----------|---------------|----------------|
| Read small file | 200-500 | - |
| Read large file | 1000-5000 | - |
| Glob search | 50-100 | 100-500 |
| Grep search | 100-200 | 200-2000 |
| Edit (single) | 500-1000 | 200-500 |
| Write (new file) | 200-500 | 500-2000 |
| WebFetch | 200-500 | 500-3000 |
| Task (Explore) | 500-1000 | 2000-10000 |

---

## Cost Optimization Rules

1. **Batch similar operations**
   - Multiple Glob in one message
   - Multiple Read in one message
   - Chain independent operations

2. **Minimize exploration**
   - Glob before Read
   - Grep before full file reads
   - Use Task(Explore) for discovery

3. **Model downgrade opportunities**
   - Verification after generation → Haiku
   - Simple tests → Haiku
   - Format checks → Haiku

4. **Delegation savings**
   - Task(Explore) for codebase discovery
   - Task(Plan) before complex implementations
   - Saves main context tokens

---

## Real-World Examples

### Expensive Pattern (avoid)
```
1. Read file1.ts (1000 tokens)
2. Read file2.ts (1000 tokens)
3. Read file3.ts (1000 tokens)
4. Decide to edit file2.ts
5. Edit file2.ts
Total: ~4000+ tokens
```

### Efficient Pattern (prefer)
```
1. Grep for pattern (200 tokens)
2. Read only file2.ts (1000 tokens)
3. Edit file2.ts
Total: ~1500 tokens (62% savings)
```

---

**Version**: 1.0.0
