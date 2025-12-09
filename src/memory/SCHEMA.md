# Memory Layer Schema

> **Purpose**: Define data structures for persistent memory across sessions
> **Research Base**: Voyager (skill library), MemGPT (tiered memory), CoALA (cognitive architecture)

---

## Memory Tiers

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKING MEMORY                                │
│  Current context, active reasoning, in-progress state           │
│  Storage: In-context window (ephemeral)                         │
│  Retrieval: Immediate                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓↑
┌─────────────────────────────────────────────────────────────────┐
│                    EPISODIC MEMORY                               │
│  Past sessions, outcomes, decisions, what worked/failed         │
│  Storage: ~/.claude/memory/episodic/                            │
│  Retrieval: Semantic search on task similarity                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓↑
┌─────────────────────────────────────────────────────────────────┐
│                   PROCEDURAL MEMORY                              │
│  Skills, successful workflows, reusable solutions               │
│  Storage: ~/.claude/memory/procedural/                          │
│  Retrieval: Description matching + keyword triggers             │
└─────────────────────────────────────────────────────────────────┘
                              ↓↑
┌─────────────────────────────────────────────────────────────────┐
│                    SEMANTIC MEMORY                               │
│  Domain knowledge, user preferences, project context            │
│  Storage: ~/.claude/memory/semantic/                            │
│  Retrieval: Domain/project matching                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structures

### Episodic Memory: Session Records

**Location**: `~/.claude/memory/episodic/sessions/`
**Format**: JSON files named `{date}_{sequence}.json`

```json
{
  "session_id": "2025-12-09_001",
  "timestamp_start": "2025-12-09T10:30:00Z",
  "timestamp_end": "2025-12-09T11:45:00Z",
  "project_path": "/Users/myles/projects/my-app",
  "initial_task": "Add user authentication to the API",
  "task_type": "feature",
  "outcome": "success",
  "summary": "Implemented JWT-based auth with middleware, tests passing",
  "key_decisions": [
    "Used JWT over sessions for stateless auth",
    "Added refresh token rotation",
    "Stored tokens in httpOnly cookies"
  ],
  "tools_used": ["Grep", "Read", "Edit", "Bash"],
  "files_modified": [
    "src/auth/jwt.ts",
    "src/middleware/auth.ts",
    "src/api/routes.ts"
  ],
  "tokens_used": 8500,
  "turns": 12,
  "errors_encountered": [],
  "lessons_learned": [
    "Check for existing auth patterns before implementing",
    "Run tests after each middleware change"
  ]
}
```

### Episodic Memory: Outcomes Index

**Location**: `~/.claude/memory/episodic/outcomes/`

**successes.jsonl** - Patterns that worked:
```jsonl
{"timestamp": "2025-12-09T11:45:00Z", "task": "Add JWT auth", "pattern": "Use existing auth config, add middleware to routes", "tokens": 8500, "project": "/Users/myles/projects/my-app"}
{"timestamp": "2025-12-08T15:30:00Z", "task": "Fix type errors", "pattern": "Run tsc --noEmit first, fix in dependency order", "tokens": 2200, "project": "/Users/myles/projects/other-app"}
```

**failures.jsonl** - Anti-patterns to avoid:
```jsonl
{"timestamp": "2025-12-07T09:00:00Z", "task": "Refactor database", "mistake": "Changed schema without running migrations", "consequence": "All tests failed", "fix": "Always check migration status first"}
{"timestamp": "2025-12-06T14:00:00Z", "task": "Update dependencies", "mistake": "Updated all at once", "consequence": "Breaking changes cascaded", "fix": "Update one major dep at a time"}
```

### Procedural Memory: Skill Library

**Location**: `~/.claude/memory/procedural/skills.jsonl`
**Format**: Voyager-style skill records

```jsonl
{
  "skill_id": "skill_001",
  "name": "jwt-auth-implementation",
  "description": "Implement JWT-based authentication with refresh tokens",
  "triggers": ["add auth", "jwt", "authentication", "login system"],
  "prerequisites": ["express or similar framework", "database for users"],
  "steps": [
    "1. Check for existing auth config in project",
    "2. Install jsonwebtoken and bcrypt if not present",
    "3. Create auth types (AuthPayload, TokenPair)",
    "4. Implement token generation and verification",
    "5. Create auth middleware",
    "6. Add to routes",
    "7. Test with curl or jest"
  ],
  "tools_typically_used": ["Grep", "Read", "Edit", "Bash"],
  "estimated_tokens": 3000,
  "success_rate": 0.9,
  "times_used": 5,
  "last_used": "2025-12-09T11:45:00Z",
  "created_from_session": "2025-12-09_001"
}
```

### Semantic Memory: User Profile

**Location**: `~/.claude/memory/semantic/user-profile.json`

```json
{
  "version": "1.0",
  "user_id": "myles",
  "preferences": {
    "code_style": {
      "indent": "spaces",
      "indent_size": 2,
      "quotes": "single",
      "semicolons": false,
      "trailing_commas": "es5"
    },
    "commit_style": {
      "conventional": true,
      "emoji": false,
      "sign_commits": false
    },
    "testing": {
      "framework": "jest",
      "coverage_threshold": 80,
      "run_before_commit": true
    },
    "communication": {
      "verbosity": "concise",
      "explain_changes": true,
      "ask_before_major_changes": true
    }
  },
  "context": {
    "primary_languages": ["typescript", "python"],
    "frameworks": ["express", "react", "next.js"],
    "databases": ["postgres", "redis"],
    "cloud": ["aws", "vercel"]
  },
  "learned_preferences": [
    {"date": "2025-12-09", "preference": "prefers Edit over Write for existing files"},
    {"date": "2025-12-08", "preference": "wants tests run after each change"}
  ]
}
```

### Semantic Memory: Domain Knowledge

**Location**: `~/.claude/memory/semantic/domain-knowledge/`
**Format**: Per-domain JSON files

**auth.json**:
```json
{
  "domain": "authentication",
  "facts": [
    {"fact": "JWT tokens should expire in 15 minutes for security", "source": "session_2025-12-09_001"},
    {"fact": "Refresh tokens should be rotated on use", "source": "session_2025-12-09_001"},
    {"fact": "Store tokens in httpOnly cookies to prevent XSS", "source": "external"}
  ],
  "common_patterns": [
    "Most Express apps use passport.js or custom middleware",
    "React apps typically store tokens in memory or cookies"
  ],
  "anti_patterns": [
    "Don't store tokens in localStorage (XSS vulnerable)",
    "Don't use synchronous bcrypt in request handlers"
  ]
}
```

### Working Memory: Context Buffer

**Location**: `~/.claude/memory/working/context-buffer.json`
**Purpose**: Cache for current session, cleared on session end

```json
{
  "session_id": "current",
  "started_at": "2025-12-09T14:00:00Z",
  "project_path": "/Users/myles/projects/current-project",
  "current_task": "Implementing user dashboard",
  "files_read": ["src/components/Dashboard.tsx", "src/api/user.ts"],
  "decisions_made": [
    "Using React Query for data fetching",
    "Dashboard will have 3 widgets"
  ],
  "pending_actions": [],
  "accumulated_context_tokens": 12000
}
```

---

## Retrieval Logic

### At Session Start

1. Load BOOTSTRAP.md (always)
2. Check project path → Load project-specific memory if exists
3. Parse initial task → Match against procedural skills
4. Load relevant domain knowledge based on task keywords
5. Load recent successes/failures from episodic memory (last 5)

### During Session

1. Update working memory buffer
2. Track tools used, files modified
3. Note any errors or corrections

### At Session End

1. Evaluate outcome (success/failure based on user feedback or task completion)
2. Extract reusable patterns → Add to procedural memory if success
3. Record lessons learned → Add to episodic memory
4. Update domain knowledge if new facts learned
5. Clear working memory buffer

---

## Token Budget for Memory Loading

| Memory Type | Max Tokens | When to Load |
|-------------|------------|--------------|
| BOOTSTRAP.md | 500 | Always |
| Procedural (matched skill) | 300 | If task matches skill |
| Episodic (recent) | 200 | Always (summary only) |
| Semantic (domain) | 200 | If domain matches |
| User preferences | 100 | Always |
| **Total max** | **1300** | |

---

## Version History

- v1.0 (2025-12-09): Initial schema
