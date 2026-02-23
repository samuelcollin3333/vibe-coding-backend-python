---
description: Write minimal code to make tests pass. Run after /specify.
allowed-tools: Read, Write, Edit, Bash, Grep, grepai
---

# Implement

## Step 1: Check Makefile

```bash
cat Makefile 2>/dev/null | head -20 || echo "NO_MAKEFILE"
```

If no Makefile, stop and ask how to run tests.

## Step 2: Read failing tests

```bash
make test 2>&1 | tail -30
```

## Step 3: Read spec for context

```bash
cat .claude/temp/spec.md 2>/dev/null || echo "No spec"
```

## Step 4: Find related code

```bash
grepai search "related concepts" 2>/dev/null | head -10 || true
```

## Step 5: Implement domain + application

**Write ONLY what's needed to make tests pass.**

Follow architecture:
- Entity → `src/domain/{entity}/{entity}.py` (frozen dataclass)
- Rules → `src/domain/{entity}/{entity}_rules.py` (static methods)
- Repository → `src/domain/{entity}/{entity}_repository.py` (Protocol)
- Handler → `src/application/{entity}/{action}_{entity}/handler.py`

## Step 6: Run tests

```bash
make test 2>&1 | tail -30
```

**All tests must pass.**

If tests fail → fix code, not tests.

## Step 7: Implement API endpoint

**Tests don't cover HTTP endpoints, but the frontend needs them to work.**

After tests pass, check if this feature needs an API endpoint. If yes:

1. Find existing routes to follow the same pattern:

```bash
grepai search "API routes or endpoint registration" --json --compact 2>/dev/null || grep -rn "@router\|@app\." src/infrastructure/ --include="*.py" | head -10
```

2. Create or update the endpoint in `src/infrastructure/api/`:
   - Route calls the handler (dependency injection via FastAPI `Depends` or manual wiring)
   - Request/Response models (Pydantic) in the same file or next to it
   - Proper HTTP status codes (201 for creation, 204 for deletion, etc.)

3. Inform the user:
> Endpoint créé : `{METHOD} /api/{resource}`
> Request body / Query params : {describe}
> Response : {describe}

**If unsure whether an endpoint is needed, ask.**

## Step 8: Verify intent

Re-read the spec. Ask yourself:
- Does the code do what the user wanted?
- Or does it just pass the tests by accident?
- Can the frontend actually call this feature?

If doubt:
> Le code fait passer les tests, mais je vérifie :
> [describe what code does]
> C'est bien ça ?

## Step 9: Done

> Implémentation terminée. Tests passent.
>
> Fichiers créés :
> - {list}
>
> Endpoint : `{METHOD} /api/{resource}` (si applicable)
>
> Tu peux `git commit` ou `/clear` puis `/refactor` si besoin.
