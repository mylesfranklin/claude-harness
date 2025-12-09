# Baseline Test Execution Guide

> **Purpose**: Record "naive" approach metrics for comparison
> **Location**: Run from `~/projects/claude-harness/tests/fixture-project/`

---

## Setup

```bash
# Navigate to fixture project
cd ~/projects/claude-harness/tests/fixture-project

# Ensure metrics collector is available
chmod +x ~/projects/claude-harness/src/scripts/metrics-collector.py

# Clear previous metrics (optional)
python3 ~/projects/claude-harness/src/scripts/metrics-collector.py clear
```

---

## Test 1: File Discovery (Baseline)

**Task**: Find all TypeScript test files

### Naive execution (simulate):
```bash
# What a naive approach would do:
ls -la                          # ~200 tokens
ls src/                         # ~150 tokens
ls src/components/              # ~150 tokens
ls src/components/__tests__/    # ~100 tokens
find . -name "*.test.ts"        # ~200 tokens
# Total: ~800 tokens, 5 tool calls
```

### Record baseline metrics:
```bash
COLLECTOR=~/projects/claude-harness/src/scripts/metrics-collector.py
python3 $COLLECTOR record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 50 --baseline
python3 $COLLECTOR record --tool "Bash:find" --scenario "file-discovery" --tokens-in 100 --tokens-out 100 --baseline
```

---

## Test 2: Content Search (Baseline)

**Task**: Find where `authenticateUser` function is defined

### Naive execution (simulate):
```bash
# What a naive approach would do:
grep -r "authenticateUser" .    # ~500 tokens (many results)
cat src/auth/handler.ts         # ~800 tokens (full file read, wrong file)
cat src/auth/utils.ts           # ~600 tokens (wrong file)
cat src/auth/jwt.ts             # ~700 tokens (found it, but read whole file)
# Total: ~2600 tokens, 4 tool calls
```

### Record baseline metrics:
```bash
python3 $COLLECTOR record --tool "Bash:grep" --scenario "content-search" --tokens-in 100 --tokens-out 400 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 600 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 400 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 500 --baseline
```

---

## Test 3: Multi-File Read (Baseline)

**Task**: Read package.json, tsconfig.json, and README.md

### Naive execution (simulate):
```bash
# What a naive approach would do (sequential):
cat package.json     # ~400 tokens (turn 1)
cat tsconfig.json    # ~300 tokens (turn 2)
cat README.md        # ~500 tokens (turn 3)
# Total: ~1200 tokens, 3 tool calls, 3 TURNS
```

### Record baseline metrics:
```bash
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 300 --baseline --notes "turn 1"
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 200 --baseline --notes "turn 2"
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 400 --baseline --notes "turn 3"
```

---

## Test 4: Codebase Exploration (Baseline)

**Task**: How is authentication implemented?

### Naive execution (simulate):
```bash
# What a naive approach would do:
ls -la                      # ~200 tokens
ls src/                     # ~200 tokens
ls src/auth/                # ~150 tokens
cat src/auth/index.ts       # ~200 tokens
cat src/auth/middleware.ts  # ~600 tokens
cat src/auth/types.ts       # ~300 tokens
grep -r "jwt\|token" src/   # ~400 tokens
cat src/config/auth.ts      # ~300 tokens
# Total: ~2350 tokens, 8 tool calls
```

### Record baseline metrics:
```bash
python3 $COLLECTOR record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 500 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 200 --baseline
python3 $COLLECTOR record --tool "Bash:grep" --scenario "codebase-explore" --tokens-in 100 --tokens-out 300 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 200 --baseline
```

---

## Test 5: Simple Verification (Baseline)

**Task**: Does config.ts exist in src/config/?

### Naive execution (simulate):
```bash
# What a naive approach would do:
ls src/config/    # ~150 tokens
# Total: ~150 tokens, 1 tool call (but using expensive model)
```

### Record baseline metrics:
```bash
python3 $COLLECTOR record --tool "Bash:ls" --scenario "simple-verify" --tokens-in 50 --tokens-out 100 --baseline --notes "using Opus model"
```

---

## Test 6: Code Modification (Baseline)

**Task**: Add console.log at start of handleRequest function

### Naive execution (simulate):
```bash
# What a naive approach would do:
grep -r "handleRequest" .       # ~200 tokens
cat src/api/handler.ts          # ~800 tokens (read full file)
# Then rewrite entire file with Write tool: ~1000 tokens
# Total: ~2000 tokens, 3 tool calls
```

### Record baseline metrics:
```bash
python3 $COLLECTOR record --tool "Bash:grep" --scenario "code-modify" --tokens-in 100 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "code-modify" --tokens-in 200 --tokens-out 600 --baseline
python3 $COLLECTOR record --tool "Write" --scenario "code-modify" --tokens-in 200 --tokens-out 800 --baseline
```

---

## Test 7: Structure Query (Baseline)

**Task**: What is the overall structure of this project?

### Naive execution (simulate):
```bash
# What a naive approach would do:
ls -la                      # ~200 tokens
ls src/                     # ~200 tokens
ls src/components/          # ~150 tokens
ls src/utils/               # ~100 tokens
ls src/api/                 # ~100 tokens
cat package.json            # ~400 tokens
cat README.md               # ~500 tokens
# Total: ~1650 tokens, 7 tool calls
```

### Record baseline metrics:
```bash
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 50 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 50 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "structure-query" --tokens-in 100 --tokens-out 300 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "structure-query" --tokens-in 100 --tokens-out 400 --baseline
```

---

## Test 8: Dependency Check (Baseline)

**Task**: What external packages does this project use?

### Naive execution (simulate):
```bash
# What a naive approach would do:
cat package.json              # ~400 tokens
npm list --depth=0            # ~300 tokens
cat package-lock.json | head  # ~1000 tokens (unnecessarily reading lock file)
# Total: ~1700 tokens, 3 tool calls
```

### Record baseline metrics:
```bash
python3 $COLLECTOR record --tool "Read" --scenario "dependency-check" --tokens-in 100 --tokens-out 300 --baseline
python3 $COLLECTOR record --tool "Bash" --scenario "dependency-check" --tokens-in 100 --tokens-out 200 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "dependency-check" --tokens-in 200 --tokens-out 800 --baseline
```

---

## Run All Baseline Tests

```bash
#!/bin/bash
# Run this script to record all baseline metrics

COLLECTOR=~/projects/claude-harness/src/scripts/metrics-collector.py

echo "Recording baseline metrics..."

# Test 1: File Discovery
python3 $COLLECTOR record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 50 --baseline
python3 $COLLECTOR record --tool "Bash:find" --scenario "file-discovery" --tokens-in 100 --tokens-out 100 --baseline

# Test 2: Content Search
python3 $COLLECTOR record --tool "Bash:grep" --scenario "content-search" --tokens-in 100 --tokens-out 400 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 600 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 400 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 500 --baseline

# Test 3: Multi-File Read
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 300 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 200 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 400 --baseline

# Test 4: Codebase Exploration
python3 $COLLECTOR record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 500 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 200 --baseline
python3 $COLLECTOR record --tool "Bash:grep" --scenario "codebase-explore" --tokens-in 100 --tokens-out 300 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 200 --baseline

# Test 5: Simple Verification
python3 $COLLECTOR record --tool "Bash:ls" --scenario "simple-verify" --tokens-in 50 --tokens-out 100 --baseline

# Test 6: Code Modification
python3 $COLLECTOR record --tool "Bash:grep" --scenario "code-modify" --tokens-in 100 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "code-modify" --tokens-in 200 --tokens-out 600 --baseline
python3 $COLLECTOR record --tool "Write" --scenario "code-modify" --tokens-in 200 --tokens-out 800 --baseline

# Test 7: Structure Query
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 150 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 100 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 50 --baseline
python3 $COLLECTOR record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 50 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "structure-query" --tokens-in 100 --tokens-out 300 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "structure-query" --tokens-in 100 --tokens-out 400 --baseline

# Test 8: Dependency Check
python3 $COLLECTOR record --tool "Read" --scenario "dependency-check" --tokens-in 100 --tokens-out 300 --baseline
python3 $COLLECTOR record --tool "Bash" --scenario "dependency-check" --tokens-in 100 --tokens-out 200 --baseline
python3 $COLLECTOR record --tool "Read" --scenario "dependency-check" --tokens-in 200 --tokens-out 800 --baseline

echo "Baseline metrics recorded."
python3 $COLLECTOR report
```

---

## Baseline Summary

| Scenario | Tool Calls | Est. Tokens |
|----------|------------|-------------|
| File Discovery | 5 | 800 |
| Content Search | 4 | 2600 |
| Multi-File Read | 3 | 1200 |
| Codebase Explore | 8 | 2350 |
| Simple Verify | 1 | 150 |
| Code Modify | 3 | 2000 |
| Structure Query | 7 | 1650 |
| Dependency Check | 3 | 1700 |
| **TOTAL** | **34** | **12,450** |
