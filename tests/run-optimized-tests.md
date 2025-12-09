# Optimized Test Execution Guide

> **Purpose**: Record "harness-aware" approach metrics for comparison
> **Location**: Run from `~/projects/claude-harness/tests/fixture-project/`

---

## Setup

```bash
# Navigate to fixture project
cd ~/projects/claude-harness/tests/fixture-project

# Ensure harness is installed
ls ~/.claude/knowledge/BOOTSTRAP.md

# Ensure metrics collector is available
chmod +x ~/projects/claude-harness/src/scripts/metrics-collector.py
COLLECTOR=~/projects/claude-harness/src/scripts/metrics-collector.py
```

---

## Test 1: File Discovery (Optimized)

**Task**: Find all TypeScript test files

### Optimized execution:
Following BOOTSTRAP.md routing: "Find files by pattern → Glob"

```bash
# Single Glob call:
# Glob("**/*.test.ts")
# Returns: src/components/__tests__/user.test.ts, src/components/__tests__/session.test.ts
# Total: ~150 tokens, 1 tool call
```

### Record optimized metrics:
```bash
python3 $COLLECTOR record --tool "Glob" --scenario "file-discovery" --tokens-in 50 --tokens-out 100
```

---

## Test 2: Content Search (Optimized)

**Task**: Find where `authenticateUser` function is defined

### Optimized execution:
Following routing tree: "Search content in files → Grep"

```bash
# Single Grep call with context:
# Grep("function authenticateUser", type="ts", output_mode="content", -C=3)
# Directly shows the function definition with context
# Total: ~300 tokens, 1 tool call
```

### Record optimized metrics:
```bash
python3 $COLLECTOR record --tool "Grep" --scenario "content-search" --tokens-in 100 --tokens-out 200
```

---

## Test 3: Multi-File Read (Optimized)

**Task**: Read package.json, tsconfig.json, and README.md

### Optimized execution:
Following BOOTSTRAP.md: "Multiple files → Parallel Read calls in single message"

```bash
# Three parallel Read calls in ONE message:
# Read("package.json") + Read("tsconfig.json") + Read("README.md")
# Same tokens but 1 TURN instead of 3
# Total: ~1000 tokens, 3 tool calls, 1 TURN
```

### Record optimized metrics:
```bash
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 250 --notes "parallel call 1"
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 200 --notes "parallel call 2"
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 350 --notes "parallel call 3"
```

---

## Test 4: Codebase Exploration (Optimized)

**Task**: How is authentication implemented?

### Optimized execution:
Following routing tree: "Codebase exploration → Task(subagent_type=Explore)"

```bash
# Single Task delegation:
# Task(subagent_type="Explore", prompt="How is authentication implemented in this project?")
# Agent handles all exploration internally
# Main context only sees summary result
# Total: ~500 tokens in main context, 1 tool call
```

### Record optimized metrics:
```bash
python3 $COLLECTOR record --tool "Task:Explore" --scenario "codebase-explore" --tokens-in 200 --tokens-out 300
```

---

## Test 5: Simple Verification (Optimized)

**Task**: Does config.ts exist in src/config/?

### Optimized execution:
Following routing tree: "Find files by pattern → Glob"
Following cost guide: "Verification tasks → Haiku"

```bash
# Single Glob call:
# Glob("src/config/config.ts")
# Returns empty if not exists, or path if exists
# Using Haiku model for simple verification
# Total: ~80 tokens, 1 tool call (Haiku at $1/MTok)
```

### Record optimized metrics:
```bash
python3 $COLLECTOR record --tool "Glob" --scenario "simple-verify" --tokens-in 30 --tokens-out 50 --notes "using Haiku model"
```

---

## Test 6: Code Modification (Optimized)

**Task**: Add console.log at start of handleRequest function

### Optimized execution:
Following routing tree: "Search content → Grep, Modify existing → Edit"

```bash
# Step 1: Find function with context
# Grep("function handleRequest", output_mode="content", -A=2, path="src/api/")
# Returns just the function signature and a few lines (~150 tokens)

# Step 2: Edit (not Write!)
# Edit("src/api/handler.ts", old="function handleRequest(", new="function handleRequest(\n  console.log('handleRequest called');")
# Surgical change, not full file rewrite (~200 tokens)
# Total: ~350 tokens, 2 tool calls
```

### Record optimized metrics:
```bash
python3 $COLLECTOR record --tool "Grep" --scenario "code-modify" --tokens-in 100 --tokens-out 100
python3 $COLLECTOR record --tool "Edit" --scenario "code-modify" --tokens-in 100 --tokens-out 50
```

---

## Test 7: Structure Query (Optimized)

**Task**: What is the overall structure of this project?

### Optimized execution:
Following routing tree: "Codebase exploration → Task(Explore)"

```bash
# Single Task delegation:
# Task(subagent_type="Explore", prompt="What is the overall structure of this project?")
# Agent explores and summarizes
# Total: ~500 tokens in main context, 1 tool call
```

### Record optimized metrics:
```bash
python3 $COLLECTOR record --tool "Task:Explore" --scenario "structure-query" --tokens-in 200 --tokens-out 300
```

---

## Test 8: Dependency Check (Optimized)

**Task**: What external packages does this project use?

### Optimized execution:
Following routing tree: "Read file contents → Read"
Recognizing: dependencies are in package.json, no need for more

```bash
# Single Read:
# Read("package.json")
# Dependencies are right there, no need for npm list or lock file
# Total: ~350 tokens, 1 tool call
```

### Record optimized metrics:
```bash
python3 $COLLECTOR record --tool "Read" --scenario "dependency-check" --tokens-in 100 --tokens-out 250
```

---

## Run All Optimized Tests

```bash
#!/bin/bash
# Run this script to record all optimized metrics

COLLECTOR=~/projects/claude-harness/src/scripts/metrics-collector.py

echo "Recording optimized metrics..."

# Test 1: File Discovery
python3 $COLLECTOR record --tool "Glob" --scenario "file-discovery" --tokens-in 50 --tokens-out 100

# Test 2: Content Search
python3 $COLLECTOR record --tool "Grep" --scenario "content-search" --tokens-in 100 --tokens-out 200

# Test 3: Multi-File Read (parallel calls count as separate but in 1 turn)
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 250
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 200
python3 $COLLECTOR record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 350

# Test 4: Codebase Exploration
python3 $COLLECTOR record --tool "Task:Explore" --scenario "codebase-explore" --tokens-in 200 --tokens-out 300

# Test 5: Simple Verification
python3 $COLLECTOR record --tool "Glob" --scenario "simple-verify" --tokens-in 30 --tokens-out 50

# Test 6: Code Modification
python3 $COLLECTOR record --tool "Grep" --scenario "code-modify" --tokens-in 100 --tokens-out 100
python3 $COLLECTOR record --tool "Edit" --scenario "code-modify" --tokens-in 100 --tokens-out 50

# Test 7: Structure Query
python3 $COLLECTOR record --tool "Task:Explore" --scenario "structure-query" --tokens-in 200 --tokens-out 300

# Test 8: Dependency Check
python3 $COLLECTOR record --tool "Read" --scenario "dependency-check" --tokens-in 100 --tokens-out 250

echo "Optimized metrics recorded."
python3 $COLLECTOR report
```

---

## Optimized Summary

| Scenario | Tool Calls | Est. Tokens | Routing |
|----------|------------|-------------|---------|
| File Discovery | 1 | 150 | Glob |
| Content Search | 1 | 300 | Grep |
| Multi-File Read | 3 (1 turn) | 1100 | Parallel Read |
| Codebase Explore | 1 | 500 | Task:Explore |
| Simple Verify | 1 | 80 | Glob + Haiku |
| Code Modify | 2 | 350 | Grep + Edit |
| Structure Query | 1 | 500 | Task:Explore |
| Dependency Check | 1 | 350 | Read |
| **TOTAL** | **11** | **3,330** | |

---

## Expected Comparison

| Scenario | Baseline | Optimized | Improvement |
|----------|----------|-----------|-------------|
| File Discovery | 800 | 150 | **81%** |
| Content Search | 2600 | 300 | **88%** |
| Multi-File Read | 1200 | 1100 | **8%** (turn savings) |
| Codebase Explore | 2350 | 500 | **79%** |
| Simple Verify | 150 | 80 | **47%** + cost |
| Code Modify | 2000 | 350 | **82%** |
| Structure Query | 1650 | 500 | **70%** |
| Dependency Check | 1700 | 350 | **79%** |
| **TOTAL** | **12,450** | **3,330** | **73%** |

**Target**: >40% improvement
**Expected**: ~73% improvement
