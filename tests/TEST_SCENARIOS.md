# Harness Test Scenarios

> **Purpose**: Measure token efficiency improvements from the self-knowledge layer
> **Target**: >40% token reduction on comparable tasks

---

## Test Methodology

### Metrics Captured
1. **Tool calls**: Number of tool invocations
2. **Input tokens**: Estimated tokens sent to model
3. **Output tokens**: Estimated tokens generated
4. **Routing accuracy**: Did it follow optimal path?
5. **Time to solution**: Turns to complete task

### Baseline Definition
"Naive" approach = what Claude Code does without harness guidance:
- Sequential exploration
- No tool routing awareness
- No cost optimization
- Inline exploration instead of delegation

### Token Estimation Formula
```
Input tokens ≈ (prompt_chars / 4) + (file_content_chars / 4) + (tool_schema_chars / 4)
Output tokens ≈ (response_chars / 4) + (tool_call_chars / 4)
```

---

## Scenario 1: File Discovery

**Task**: "Find all TypeScript test files in the project"

### Naive Approach (baseline)
```
1. Bash("ls -la")                    → ~200 tokens
2. Bash("ls src/")                   → ~150 tokens
3. Bash("ls src/components/")        → ~150 tokens
4. Bash("find . -name '*.test.ts'")  → ~300 tokens
Total: ~800 tokens, 4 tool calls
```

### Optimized Approach (with harness)
```
1. Glob("**/*.test.ts")              → ~200 tokens
Total: ~200 tokens, 1 tool call
```

**Expected improvement**: 75% token reduction

---

## Scenario 2: Content Search

**Task**: "Find where the `authenticateUser` function is defined"

### Naive Approach (baseline)
```
1. Bash("grep -r 'authenticateUser' .")  → ~500 tokens (if many results)
2. Read("src/auth/handler.ts")           → ~800 tokens
3. Read("src/auth/utils.ts")             → ~600 tokens
4. Read("src/middleware/auth.ts")        → ~700 tokens
Total: ~2600 tokens, 4 tool calls
```

### Optimized Approach (with harness)
```
1. Grep("function authenticateUser|authenticateUser\\s*=", type="ts", output_mode="content", -C=3)
   → ~400 tokens (targeted results with context)
Total: ~400 tokens, 1 tool call
```

**Expected improvement**: 85% token reduction

---

## Scenario 3: Multi-File Reading

**Task**: "Read the package.json, tsconfig.json, and README.md files"

### Naive Approach (baseline)
```
1. Read("package.json")    → ~400 tokens
2. Read("tsconfig.json")   → ~300 tokens
3. Read("README.md")       → ~500 tokens
Total: ~1200 tokens, 3 sequential tool calls (3 turns)
```

### Optimized Approach (with harness)
```
1. Parallel Read calls in single message:
   - Read("package.json")
   - Read("tsconfig.json")
   - Read("README.md")
Total: ~1200 tokens, 3 tool calls (1 turn)
```

**Expected improvement**: 66% turn reduction (same tokens, faster)

---

## Scenario 4: Codebase Exploration

**Task**: "How is authentication implemented in this project?"

### Naive Approach (baseline)
```
1. Bash("ls -la")                        → ~200 tokens
2. Bash("ls src/")                       → ~200 tokens
3. Bash("ls src/auth/")                  → ~150 tokens
4. Read("src/auth/index.ts")             → ~500 tokens
5. Read("src/auth/middleware.ts")        → ~600 tokens
6. Read("src/auth/types.ts")             → ~300 tokens
7. Grep("jwt|token", path="src/")        → ~400 tokens
8. Read("src/config/auth.ts")            → ~400 tokens
Total: ~2750 tokens, 8 tool calls
```

### Optimized Approach (with harness)
```
1. Task(subagent_type="Explore", prompt="How is authentication implemented?")
   → Delegated exploration, ~500 tokens in main context
   → Agent handles exploration internally
Total: ~500 tokens main context, 1 tool call (delegated work)
```

**Expected improvement**: 82% main context token reduction

---

## Scenario 5: Simple Verification

**Task**: "Does a file called config.ts exist in src/?"

### Naive Approach (baseline)
```
1. Bash("ls src/")                       → ~200 tokens
2. Parse output looking for config.ts
Total: ~200 tokens, 1 tool call (Opus at $15/MTok)
```

### Optimized Approach (with harness)
```
1. Glob("src/config.ts")                 → ~100 tokens
   (Also: should use Haiku model for verification)
Total: ~100 tokens, 1 tool call (Haiku at $1/MTok)
```

**Expected improvement**: 50% token reduction + 93% cost reduction (model selection)

---

## Scenario 6: Code Modification

**Task**: "Add a console.log at the start of the handleRequest function"

### Naive Approach (baseline)
```
1. Grep("handleRequest")                 → ~200 tokens
2. Read("src/api/handler.ts")            → ~800 tokens (full file)
3. Write("src/api/handler.ts")           → ~1000 tokens (full file rewrite)
Total: ~2000 tokens, 3 tool calls
```

### Optimized Approach (with harness)
```
1. Grep("function handleRequest", output_mode="content", -A=2)  → ~150 tokens
2. Edit("src/api/handler.ts", old="function handleRequest() {",
        new="function handleRequest() {\n  console.log('handleRequest called');")
   → ~200 tokens
Total: ~350 tokens, 2 tool calls
```

**Expected improvement**: 82% token reduction

---

## Scenario 7: Understanding Codebase Structure

**Task**: "What is the overall structure of this project?"

### Naive Approach (baseline)
```
1. Bash("ls -la")                        → ~200 tokens
2. Bash("ls src/")                       → ~200 tokens
3. Bash("ls src/components/")            → ~200 tokens
4. Bash("ls src/utils/")                 → ~150 tokens
5. Bash("ls src/api/")                   → ~150 tokens
6. Read("package.json")                  → ~400 tokens
7. Read("README.md")                     → ~500 tokens
Total: ~1800 tokens, 7 tool calls
```

### Optimized Approach (with harness)
```
1. Task(subagent_type="Explore", prompt="What is the overall structure?")
   → ~500 tokens main context
Total: ~500 tokens, 1 tool call
```

**Expected improvement**: 72% token reduction

---

## Scenario 8: Dependency Analysis

**Task**: "What external packages does this project use?"

### Naive Approach (baseline)
```
1. Read("package.json")                  → ~400 tokens
2. Bash("npm list --depth=0")            → ~300 tokens
3. Read("package-lock.json") [partial]   → ~1000 tokens
Total: ~1700 tokens, 3 tool calls
```

### Optimized Approach (with harness)
```
1. Read("package.json")                  → ~400 tokens
   (Recognize: dependencies field has the answer, no need for more)
Total: ~400 tokens, 1 tool call
```

**Expected improvement**: 76% token reduction

---

## Summary: Expected Improvements

| Scenario | Naive Tokens | Optimized Tokens | Reduction |
|----------|--------------|------------------|-----------|
| 1. File Discovery | 800 | 200 | 75% |
| 2. Content Search | 2600 | 400 | 85% |
| 3. Multi-File Read | 1200 (3 turns) | 1200 (1 turn) | 66% turns |
| 4. Codebase Explore | 2750 | 500 | 82% |
| 5. Simple Verify | 200 | 100 | 50% + cost |
| 6. Code Modify | 2000 | 350 | 82% |
| 7. Structure Query | 1800 | 500 | 72% |
| 8. Dependency Check | 1700 | 400 | 76% |

**Average token reduction**: ~75%
**Target**: >40%

---

## Test Execution Protocol

1. Create test project with known structure
2. Run each scenario with "naive" prompt (no routing hints)
3. Record actual tool calls and token usage
4. Run each scenario with harness-aware prompt
5. Compare metrics
6. Document routing decision accuracy

---

## Validation Criteria

Phase 1 is validated when:
- [ ] Average token reduction >40% across scenarios
- [ ] Routing accuracy >80% (follows decision tree)
- [ ] No regressions (optimized never worse than naive)
- [ ] Model selection recommendations applied (Haiku for verification)
