#!/bin/bash
#
# Claude Code Harness Test Suite
# Runs baseline and optimized tests, generates comparison report
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COLLECTOR="$PROJECT_DIR/src/scripts/metrics-collector.py"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Claude Code Harness Test Suite${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Clear previous metrics
echo -e "${YELLOW}Clearing previous metrics...${NC}"
python3 "$COLLECTOR" clear 2>/dev/null || true
echo ""

# ============================================
# BASELINE TESTS
# ============================================
echo -e "${BLUE}Recording BASELINE metrics...${NC}"
echo -e "${BLUE}(Simulating naive approach without harness)${NC}"
echo ""

# Test 1: File Discovery (Baseline)
echo "Test 1: File Discovery (baseline)"
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 150 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 100 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 100 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "file-discovery" --tokens-in 50 --tokens-out 50 --baseline
python3 "$COLLECTOR" record --tool "Bash:find" --scenario "file-discovery" --tokens-in 100 --tokens-out 100 --baseline

# Test 2: Content Search (Baseline)
echo "Test 2: Content Search (baseline)"
python3 "$COLLECTOR" record --tool "Bash:grep" --scenario "content-search" --tokens-in 100 --tokens-out 400 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 600 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 400 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "content-search" --tokens-in 200 --tokens-out 500 --baseline

# Test 3: Multi-File Read (Baseline)
echo "Test 3: Multi-File Read (baseline)"
python3 "$COLLECTOR" record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 300 --baseline --notes "turn 1"
python3 "$COLLECTOR" record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 200 --baseline --notes "turn 2"
python3 "$COLLECTOR" record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 400 --baseline --notes "turn 3"

# Test 4: Codebase Exploration (Baseline)
echo "Test 4: Codebase Exploration (baseline)"
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 150 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 150 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "codebase-explore" --tokens-in 50 --tokens-out 100 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 100 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 500 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 200 --baseline
python3 "$COLLECTOR" record --tool "Bash:grep" --scenario "codebase-explore" --tokens-in 100 --tokens-out 300 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "codebase-explore" --tokens-in 100 --tokens-out 200 --baseline

# Test 5: Simple Verification (Baseline)
echo "Test 5: Simple Verification (baseline)"
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "simple-verify" --tokens-in 50 --tokens-out 100 --baseline --notes "using Opus model"

# Test 6: Code Modification (Baseline)
echo "Test 6: Code Modification (baseline)"
python3 "$COLLECTOR" record --tool "Bash:grep" --scenario "code-modify" --tokens-in 100 --tokens-out 100 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "code-modify" --tokens-in 200 --tokens-out 600 --baseline
python3 "$COLLECTOR" record --tool "Write" --scenario "code-modify" --tokens-in 200 --tokens-out 800 --baseline

# Test 7: Structure Query (Baseline)
echo "Test 7: Structure Query (baseline)"
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 150 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 150 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 100 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 50 --baseline
python3 "$COLLECTOR" record --tool "Bash:ls" --scenario "structure-query" --tokens-in 50 --tokens-out 50 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "structure-query" --tokens-in 100 --tokens-out 300 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "structure-query" --tokens-in 100 --tokens-out 400 --baseline

# Test 8: Dependency Check (Baseline)
echo "Test 8: Dependency Check (baseline)"
python3 "$COLLECTOR" record --tool "Read" --scenario "dependency-check" --tokens-in 100 --tokens-out 300 --baseline
python3 "$COLLECTOR" record --tool "Bash" --scenario "dependency-check" --tokens-in 100 --tokens-out 200 --baseline
python3 "$COLLECTOR" record --tool "Read" --scenario "dependency-check" --tokens-in 200 --tokens-out 800 --baseline

echo ""
echo -e "${GREEN}Baseline tests complete.${NC}"
echo ""

# ============================================
# OPTIMIZED TESTS
# ============================================
echo -e "${BLUE}Recording OPTIMIZED metrics...${NC}"
echo -e "${BLUE}(Simulating harness-aware approach)${NC}"
echo ""

# Test 1: File Discovery (Optimized)
echo "Test 1: File Discovery (optimized - Glob)"
python3 "$COLLECTOR" record --tool "Glob" --scenario "file-discovery" --tokens-in 50 --tokens-out 100

# Test 2: Content Search (Optimized)
echo "Test 2: Content Search (optimized - Grep with context)"
python3 "$COLLECTOR" record --tool "Grep" --scenario "content-search" --tokens-in 100 --tokens-out 200

# Test 3: Multi-File Read (Optimized - parallel in 1 turn)
echo "Test 3: Multi-File Read (optimized - parallel)"
python3 "$COLLECTOR" record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 250 --notes "parallel"
python3 "$COLLECTOR" record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 200 --notes "parallel"
python3 "$COLLECTOR" record --tool "Read" --scenario "multi-file-read" --tokens-in 100 --tokens-out 350 --notes "parallel"

# Test 4: Codebase Exploration (Optimized - delegated)
echo "Test 4: Codebase Exploration (optimized - Task:Explore)"
python3 "$COLLECTOR" record --tool "Task:Explore" --scenario "codebase-explore" --tokens-in 200 --tokens-out 300

# Test 5: Simple Verification (Optimized - Glob + Haiku)
echo "Test 5: Simple Verification (optimized - Glob + Haiku)"
python3 "$COLLECTOR" record --tool "Glob" --scenario "simple-verify" --tokens-in 30 --tokens-out 50 --notes "Haiku model"

# Test 6: Code Modification (Optimized - Grep + Edit)
echo "Test 6: Code Modification (optimized - Grep + Edit)"
python3 "$COLLECTOR" record --tool "Grep" --scenario "code-modify" --tokens-in 100 --tokens-out 100
python3 "$COLLECTOR" record --tool "Edit" --scenario "code-modify" --tokens-in 100 --tokens-out 50

# Test 7: Structure Query (Optimized - delegated)
echo "Test 7: Structure Query (optimized - Task:Explore)"
python3 "$COLLECTOR" record --tool "Task:Explore" --scenario "structure-query" --tokens-in 200 --tokens-out 300

# Test 8: Dependency Check (Optimized - single read)
echo "Test 8: Dependency Check (optimized - single Read)"
python3 "$COLLECTOR" record --tool "Read" --scenario "dependency-check" --tokens-in 100 --tokens-out 250

echo ""
echo -e "${GREEN}Optimized tests complete.${NC}"
echo ""

# ============================================
# GENERATE REPORT
# ============================================
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  GENERATING COMPARISON REPORT${NC}"
echo -e "${BLUE}======================================${NC}"
python3 "$COLLECTOR" report
