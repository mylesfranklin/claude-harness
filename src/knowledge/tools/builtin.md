# Built-in Tools Reference

> Quick reference for all native Claude Code tools

---

## Read

**Purpose**: Read file contents from filesystem

**Parameters**:
- `file_path` (required): Absolute path to file
- `offset` (optional): Line number to start from
- `limit` (optional): Number of lines to read

**Use When**:
- Need to see file contents
- Viewing images, PDFs, notebooks
- Reading configuration files

**Tips**:
- Returns line numbers (cat -n format)
- Lines >2000 chars are truncated
- Can read images (PNG, JPG), PDFs, and .ipynb files
- Make parallel calls for multiple files

---

## Write

**Purpose**: Create or overwrite a file

**Parameters**:
- `file_path` (required): Absolute path for the file
- `content` (required): Content to write

**Use When**:
- Creating new files only
- Must Read file first if it exists

**Tips**:
- Prefer Edit for existing files
- Never create docs/README unless asked
- Avoid emojis unless requested

---

## Edit

**Purpose**: Modify existing files with string replacement

**Parameters**:
- `file_path` (required): Absolute path to file
- `old_string` (required): Exact text to replace
- `new_string` (required): Replacement text
- `replace_all` (optional): Replace all occurrences

**Use When**:
- Any modification to existing file
- Renaming variables (use replace_all=true)
- Adding/removing code sections

**Tips**:
- Must Read file first
- old_string must be unique (or use replace_all)
- Preserve exact indentation from file

---

## Glob

**Purpose**: Find files by name pattern

**Parameters**:
- `pattern` (required): Glob pattern (e.g., `**/*.ts`)
- `path` (optional): Directory to search in

**Use When**:
- Finding files by extension
- Locating files by name pattern
- Discovery before Read

**Patterns**:
- `**/*.ts` - All TypeScript files
- `src/**/*.test.js` - All test files in src
- `**/config.*` - All config files
- `package.json` - Specific file anywhere

---

## Grep

**Purpose**: Search file contents with regex

**Parameters**:
- `pattern` (required): Regex pattern
- `path` (optional): Directory or file to search
- `output_mode`: "files_with_matches" (default), "content", "count"
- `glob` (optional): Filter by file pattern
- `type` (optional): Filter by file type (js, py, etc.)
- `-A`, `-B`, `-C`: Context lines (with output_mode: "content")
- `-i`: Case insensitive
- `multiline`: For patterns spanning lines

**Use When**:
- Finding code by content
- Locating function/class definitions
- Searching for patterns across codebase

**Examples**:
```
# Find files containing "TODO"
Grep(pattern="TODO", output_mode="files_with_matches")

# Search with context
Grep(pattern="function auth", output_mode="content", -C=3)

# Specific file type
Grep(pattern="export default", type="ts")
```

---

## Bash

**Purpose**: Execute shell commands

**Parameters**:
- `command` (required): Shell command to run
- `timeout` (optional): Max time in ms (default 120000)
- `run_in_background` (optional): Run asynchronously

**Use When**:
- Git operations
- npm/pip/build commands
- System operations
- Any command-line tool

**Tips**:
- Quote paths with spaces
- Use `&&` for sequential dependent commands
- Avoid using for file ops (use Read/Write/Edit instead)
- Never use `cat`, `grep`, `find` - use native tools

---

## Task

**Purpose**: Spawn specialized sub-agents

**Parameters**:
- `prompt` (required): Task description
- `subagent_type` (required): Agent type
- `model` (optional): haiku, sonnet, opus
- `run_in_background` (optional): Async execution
- `resume` (optional): Resume previous agent by ID

**Agent Types**:
- `Explore`: Codebase exploration
- `Plan`: Implementation planning
- `claude-code-guide`: Claude Code documentation
- `general-purpose`: Complex multi-step tasks

**Use When**:
- Task matches agent specialty
- Exploration-heavy work
- Multi-step complex operations

---

## WebFetch

**Purpose**: Fetch and analyze URL content

**Parameters**:
- `url` (required): Full URL to fetch
- `prompt` (required): What to extract/analyze

**Use When**:
- Reading documentation
- Fetching external data
- Analyzing web content

**Tips**:
- HTTPS required (HTTP auto-upgraded)
- Results may be summarized if large
- Follow redirects manually if different host

---

## WebSearch

**Purpose**: Search the web

**Parameters**:
- `query` (required): Search query
- `allowed_domains` (optional): Limit to domains
- `blocked_domains` (optional): Exclude domains

**Use When**:
- Finding current information
- Research beyond knowledge cutoff
- Locating documentation

**Tips**:
- Include year (2025) for recent info
- Always cite sources in response

---

## TodoWrite

**Purpose**: Manage task list

**Parameters**:
- `todos` (required): Array of todo objects
  - `content`: Task description (imperative)
  - `activeForm`: Present continuous form
  - `status`: "pending", "in_progress", "completed"

**Use When**:
- Multi-step tasks (3+ steps)
- Complex planning
- Tracking progress

---

## AskUserQuestion

**Purpose**: Get user input/clarification

**Parameters**:
- `questions` (required): Array of questions
  - `question`: The question text
  - `header`: Short label (max 12 chars)
  - `options`: 2-4 choices
  - `multiSelect`: Allow multiple selections

**Use When**:
- Need clarification
- Multiple valid approaches
- User preference required

---

**Version**: 1.0.0
