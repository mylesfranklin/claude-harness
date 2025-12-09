# Tool Routing Decision Tree

> **Purpose**: Optimal tool selection for any task
> **Rule**: Follow this tree before every action

---

## File Operations

```
TASK: Find files
├─ By name/pattern? → Glob("**/*.ts", "src/**/test*.js")
├─ By content? → Grep("pattern", path="./src")
└─ Specific known path? → Read directly

TASK: Read file
├─ Single file, full content → Read(file_path)
├─ Multiple files → Parallel Read calls in single message
├─ Large file (>2000 lines) → Read with offset/limit
└─ Search within file → Grep(pattern, path="specific/file.ts")

TASK: Modify file
├─ Existing file → Edit(file_path, old_string, new_string)
├─ New file → Write(file_path, content)
├─ Multiple changes same file → Multiple Edit calls, NOT Write
└─ Rename across file → Edit with replace_all=true

TASK: List directory
├─ Simple listing → Bash("ls path/")
├─ Find specific types → Glob("path/**/*.ext")
└─ Recursive structure → Bash("tree path/ -L 2")
```

---

## Code Operations

```
TASK: Run tests
├─ Single test → Bash("npm test -- path/to/test.ts")
├─ Test suite → Bash("npm test")
├─ Watch mode → Bash with run_in_background=true
└─ Coverage → Bash("npm run test:coverage")

TASK: Build project
├─ Standard build → Bash("npm run build")
├─ Type check only → Bash("npm run typecheck" or "tsc --noEmit")
└─ Lint → Bash("npm run lint")

TASK: Install dependencies
├─ Node → Bash("npm install [package]")
├─ Python → Bash("pip install [package]")
└─ Check versions → Bash("npm list" or "pip list")
```

---

## Git Operations

```
TASK: Status/changes
├─ Current status → Bash("git status")
├─ Staged changes → Bash("git diff --staged")
├─ Unstaged changes → Bash("git diff")
└─ Recent commits → Bash("git log --oneline -10")

TASK: Commit workflow
├─ Stage files → Bash("git add <files>")
├─ Commit → Bash("git commit -m 'message'")
└─ Stage + commit → Bash("git add . && git commit -m 'message'")

TASK: Branch operations
├─ List branches → Bash("git branch -a")
├─ Switch branch → Bash("git checkout <branch>")
├─ Create branch → Bash("git checkout -b <branch>")
└─ Delete branch → Bash("git branch -d <branch>")

TASK: Remote operations
├─ Pull changes → Bash("git pull")
├─ Push changes → Bash("git push")
└─ Fetch updates → Bash("git fetch --all")
```

---

## External Data

```
TASK: Web content
├─ Known URL → WebFetch(url, prompt)
├─ Search for info → WebSearch(query)
├─ Scrape website → MCP firecrawl if available
└─ AI-powered search → MCP perplexity if available

TASK: API calls
├─ GitHub operations → MCP github if available
├─ Database queries → MCP supabase if available
├─ Code search → MCP exa if available
└─ Generic HTTP → Bash("curl ...")

TASK: Documentation
├─ Claude Code docs → Task(subagent_type="claude-code-guide")
├─ External docs → WebFetch with extraction prompt
└─ Code context → MCP exa get_code_context
```

---

## Complex Tasks

```
TASK: Codebase exploration
└─ ALWAYS → Task(subagent_type="Explore", prompt="...")
   Reason: Delegated exploration is cheaper than inline exploration

TASK: Implementation planning
└─ Non-trivial changes → Task(subagent_type="Plan", prompt="...")
   Or: EnterPlanMode for user approval workflow

TASK: Multi-file refactor
├─ Design phase → Task(subagent_type="Plan")
├─ Implementation → Sequential Edit calls
└─ Verification → Bash("npm test && npm run build")

TASK: Debugging
├─ Find error source → Grep for error message/stack trace
├─ Read relevant files → Parallel Read calls
├─ Check logs → Bash or MCP (supabase get_logs)
└─ Test fix → Bash("npm test -- specific-test")
```

---

## Decision Shortcuts

### "I need to find something"
- **File by name**: `Glob`
- **Code by content**: `Grep`
- **File by function/class**: `Grep("class MyClass" or "function myFunc")`
- **Unknown location**: `Task(Explore)` to delegate

### "I need to read something"
- **One file**: `Read`
- **Multiple files**: Multiple `Read` in single message
- **Search within**: `Grep` with specific path

### "I need to change something"
- **One file**: `Edit`
- **Multiple files**: Multiple `Edit` calls
- **New file**: `Write` (but prefer Edit for existing)

### "I need external info"
- **Known URL**: `WebFetch`
- **General search**: `WebSearch` or MCP perplexity
- **Code examples**: MCP exa
- **GitHub data**: MCP github

---

## Cost Awareness

| Operation | Typical Tokens | Cost Level |
|-----------|----------------|------------|
| Glob | 50-200 | Low |
| Grep (files_with_matches) | 100-500 | Low |
| Read (small file) | 200-1000 | Medium |
| Read (large file) | 1000-5000 | High |
| WebFetch | 500-3000 | Medium-High |
| Task (Explore) | 2000-10000 | High (but delegated) |
| Manual exploration | 5000-25000 | Very High (avoid) |

**Rule**: If estimated tokens > 1000, consider:
1. Can I narrow the search?
2. Can I delegate to Task agent?
3. Should I ask user for guidance?

---

**Version**: 1.0.0
