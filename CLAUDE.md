# Project Configuration

## Philosophy

> **Human intent is the contract. Tests prove it.**

Clarify first → Tests next → Minimal code.

## IMPORTANT: Use Makefile

**Never run pytest, black, mypy directly. Always use `make`.**

```bash
make test        # Run all tests
make test-quick  # Quick test (stop on first failure)
make lint        # Check formatting
make typecheck   # Type check
make format      # Auto-format code
```

If no Makefile exists, ask the user how to run tests and propose to generate one.

## Commands

| Command | Role |
|---------|------|
| `/clarify` | Clarify need through conversation → spec |
| `/specify` | Spec → tests (must fail) |
| `/implement` | Tests → minimal code (must pass) |
| `/refactor` | Improve code (tests stay green) |
| `/clear` | Reset context between phases (built-in Claude Code command) |

## Flow

```
/clarify {feature}  →  conversation  →  .claude/temp/spec.md
/clear
/specify            →  read spec     →  tests (red)
/clear
/implement          →  read tests    →  code (green)
git commit          →  hook: make test-quick + lint + typecheck
```

## Git Workflow

A **pre-commit hook** runs automatically and blocks the commit if any check fails:
- `make test-quick` — tests must pass
- `make lint` — code must be properly formatted
- `make typecheck` — no type errors

If you created or modified an API endpoint, run `make openapi` before committing to regenerate the OpenAPI spec.

**You don't need to run all these checks before every commit.** But be aware they will run. Write clean code from the start: correct types, proper formatting, passing tests. When you suspect a check might fail (complex refactor, new types, unfamiliar patterns), run the relevant `make` command proactively to catch issues early rather than discovering them at commit time.

Commit often: after each `/implement` or `/refactor` cycle.

## Architecture

**Read `.claude/skills/hexagonal-arch/SKILL.md` for details.**

```
src/
  domain/{entity}/         → Entity, Rules, Repository (Protocol)
  application/{entity}/    → Use cases (command + handler)
  infrastructure/          → Implementations
tests/
  unit/domain/            → Rules tests
  integration/application/ → Handler tests
```

## Enforced (hooks block)

- Domain cannot import infrastructure/application
- Entities must be `@dataclass(frozen=True)`
- Handlers cannot import implementations directly

## Conventions

| Concept | Pattern |
|---------|---------|
| Entity | `{Entity}` (frozen dataclass) |
| Rules | `{Entity}Rules` (static methods) |
| Repository | `{Entity}Repository` (Protocol) |
| Handler | `{Action}{Entity}Handler` |

## Commit

```
[{layer}/{entity}] {description}

{Context in natural language}
```


## grepai - Semantic Code Search

**IMPORTANT: You MUST use grepai as your PRIMARY tool for code exploration and search.**

### When to Use grepai (REQUIRED)

Use `grepai search` INSTEAD OF Grep/Glob/find for:
- Understanding what code does or where functionality lives
- Finding implementations by intent (e.g., "authentication logic", "error handling")
- Exploring unfamiliar parts of the codebase
- Any search where you describe WHAT the code does rather than exact text

### When to Use Standard Tools

Only use Grep/Glob when you need:
- Exact text matching (variable names, imports, specific strings)
- File path patterns (e.g., `**/*.py`)

### Fallback

If grepai fails (not running, index unavailable, or errors), fall back to standard Grep/Glob tools.

### Usage

```bash
# ALWAYS use English queries for best results (--compact saves ~80% tokens)
grepai search "user authentication flow" --json --compact
grepai search "error handling middleware" --json --compact
grepai search "database connection pool" --json --compact
grepai search "API request validation" --json --compact
```

### Query Tips

- **Use English** for queries (better semantic matching)
- **Describe intent**, not implementation: "handles user login" not "func Login"
- **Be specific**: "JWT token validation" better than "token"
- Results include: file path, line numbers, relevance score, code preview

### Call Graph Tracing

Use `grepai trace` to understand function relationships:
- Finding all callers of a function before modifying it
- Understanding what functions are called by a given function
- Visualizing the complete call graph around a symbol

#### Trace Commands

**IMPORTANT: Always use `--json` flag for optimal AI agent integration.**

```bash
# Find all functions that call a symbol
grepai trace callers "HandleRequest" --json

# Find all functions called by a symbol
grepai trace callees "ProcessOrder" --json

# Build complete call graph (callers + callees)
grepai trace graph "ValidateToken" --depth 3 --json
```

### Workflow

1. Start with `grepai search` to find relevant code
2. Use `grepai trace` to understand function relationships
3. Use `Read` tool to examine files from results
4. Only use Grep for exact string searches if needed
