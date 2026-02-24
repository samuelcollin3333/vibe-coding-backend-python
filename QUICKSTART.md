# Quickstart

## Setup (5 min)

```bash
# Install git hooks (blocks if tests fail, lint fails or types fail)
./scripts/install-hooks.sh

# Semantic search (optional but recommended)
curl -sSL https://raw.githubusercontent.com/yoanbernabeu/grepai/main/install.sh | sh
grepai init
grepai watch  # Launches continuous indexing in the background

# Start Claude
claude
```

## grepai

`grepai` continuously indexes the code and allows Claude to perform semantic search (by intent) rather than exact text matching. It saves tokens and gives better results.

- `grepai init` : creates the initial project index
- `grepai watch` : monitors changes and continuously updates the index (run in a dedicated terminal or in background with `grepai watch &`)

## Philosophy

> **Human intent is the contract. Tests prove it.**

4 specialized commands, each with its own isolated context.

## The 4 Commands

| Command | Role |
|---------|------|
| `/clarify` | Clarifies the need → spec |
| `/specify` | Generates tests (must fail) |
| `/implement` | Writes the code (tests pass) |
| `/refactor` | Improves code (tests stay green) |

## Usage

**Option 1: Let Claude choose**

```
> I want to allow order cancellation

Claude: [automatically uses clarify]
        What's the expected behavior?
```

**Option 2: Ask explicitly**

```
> /clarify order cancellation
> /specify
> /implement
```

## Full Example

```
> /clarify order cancellation

Claude: What's the expected behavior?

> The customer can cancel if < 24h and not shipped

Claude: And if the conditions aren't met?

> Error with the reason

Claude: OK, let me summarize:
- Customer cancels their order
- OK if < 24h AND not shipped
- Otherwise error "Too late" or "Already shipped"
Correct?

> Yes

Claude: Spec written. /clear then /specify

> /specify

Claude: Tests generated. They fail. /clear then /implement

> /implement

Claude: Code written. Tests pass.

> git commit -m "[domain/order] add cancellation rule"

✅ Commit OK (pre-commit verifies tests + lint + types)
```

## Infrastructure and other tasks

For anything that's not business logic code (Docker, CI, config...), just ask directly:

```
> Dockerize the project
```

No need for specialized commands for that.

## Automatic Protection

- **Pre-commit hook**: Blocks if tests fail, lint fails or types fail
- **Claude hook**: Blocks if architecture is violated (forbidden imports, non-frozen dataclass)
