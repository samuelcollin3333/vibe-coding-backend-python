---
description: Improve code without changing behavior. Tests must stay green. Optional.
allowed-tools: Read, Write, Edit, Bash, Grep, grepai
---

# Refactor

## Step 1: Verify tests pass

```bash
make test 2>&1 | tail -20
```

**Do not proceed if tests are red.**

## Step 2: Analyze and present observations

Look for:
- Duplicated **logic** → extract to Rules (see warning below)
- Long functions → split
- Unclear names → rename
- Missing types → add hints
- Complex conditions → simplify

Check impact of each observation:

```bash
grepai trace callers "{function}" 2>/dev/null || grep -rn "{function}" src/ --include="*.py" | head -10
```

### Duplicate code vs duplicate logic

**Two different business logics that happen to have the same code today MUST stay separate.** They will evolve independently. Only factorize when it's truly the **same business logic** used in multiple places.

Ask yourself: "If the business rule changes for one case, should it change for the other?" If no → keep duplicated.

## Step 3: Present to user for validation

**Do NOT start coding. Present your observations first.**

> Here's what I identified:
>
> 1. {observation} → {proposed change}
> 2. {observation} → {proposed change}
>
> Do you approve? Want me to modify or remove anything?

**Wait for explicit validation before touching any code.**

## Step 4: Refactor incrementally

**One change at a time. Run tests after each.**

```bash
make test
```

If tests fail → revert and try differently.

## Step 5: Final verification

```bash
make test
```

All tests must still pass.

## Step 6: Done

> Refactoring complete. Tests still green.
>
> Changes:
> - {list}
>
> You can `git commit`.
