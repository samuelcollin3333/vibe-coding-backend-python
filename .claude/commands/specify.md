---
description: Generate tests from spec. Tests MUST fail. Run after /clarify.
allowed-tools: Read, Write, Bash, grepai
---

# Specify

## Step 1: Check Makefile exists

```bash
cat Makefile 2>/dev/null | head -20 || echo "NO_MAKEFILE"
```

If no Makefile, stop and ask:
> Pas de Makefile trouvé. Comment lances-tu les tests ?
> Je peux générer un Makefile si tu me dis quelle commande utiliser (docker, python, etc.)

## Step 2: Read spec

```bash
cat .claude/temp/spec.md
```

If no spec, stop: "Pas de spec. Lance `/clarify` d'abord."

## Step 3: List test cases

From the spec, identify:
- **Success cases** - conditions met → expected outcome
- **Failure cases** - conditions not met → expected error

## Step 4: Verify with user

> D'après la spec, voici les cas que je vais tester :
>
> ✓ Succès :
> - {case 1}
> - {case 2}
>
> ✗ Échec :
> - {case 3} → {error}
>
> Il manque des cas ?

**Wait for confirmation.**

## Step 5: Write tests

Location:
- Rules → `tests/unit/domain/{entity}/test_{entity}_rules.py`
- Handlers → `tests/integration/application/{entity}/test_{action}_{entity}_handler.py`

### NEVER mock repositories

**Do not use `Mock()`, `MagicMock()`, or `patch()` for repositories.** Mocked repos hide real bugs (wrong queries, missing saves, broken constraints).

Tests run against a **real database** (Postgres via docker-compose.test.yml). The DB is reset at each run (`alembic downgrade base && alembic upgrade head`). Use the real repository implementations and rely on fixtures/builders to set up test data.

Before writing tests, check existing fixtures and builders:

```bash
grepai search "test fixtures or builders" --json --compact 2>/dev/null || grep -rn "fixture\|Builder\|factory" tests/ --include="*.py" | head -10
```

Reuse existing fixtures. Create new builders in `tests/helpers/` if needed.

### Prefer testing behavior over implementation

When possible, assert on **observable behavior** (results, side effects, errors) rather than internal details (which method was called, in what order). This makes tests more resilient to refactors.

That said, complex business logic sometimes requires detailed unit tests that are tightly coupled to implementation — that's fine when the logic justifies it.

### Test template

```python
"""
Tests for {feature}.

Intent (user's words):
{paste from spec}
"""

import pytest

class Test{Feature}:

    # --- SUCCESS CASES ---

    def test_should_{outcome}_when_{condition}(self):
        # Arrange — use fixtures/builders to insert test data
        ...
        # Act
        ...
        # Assert
        assert ...

    # --- FAILURE CASES ---

    def test_should_fail_when_{condition}(self):
        # Arrange
        ...
        # Act & Assert
        with pytest.raises({Error}) as exc:
            ...
        assert "{message}" in str(exc.value)
```

## Step 6: Verify tests fail

```bash
make test 2>&1 | tail -20
```

**Tests MUST fail.** If they pass, something is wrong.

## Step 7: Next step

> Tests créés. Ils échouent (normal).
>
> Prochaine étape : `/clear` puis `/implement`
