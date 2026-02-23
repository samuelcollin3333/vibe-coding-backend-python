---
description: Clarify requirements through conversation. Output is a clear spec. FIRST STEP for any new feature.
allowed-tools: Read, Grep, Bash, grepai
---

# Clarify: $ARGUMENTS

## Step 1: Check what exists

```bash
grepai search "$ARGUMENTS" 2>/dev/null | head -10 || grep -rn "$ARGUMENTS" src/ --include="*.py" | head -5
```

## Step 2: Conversation to clarify

**Ask questions until the need is crystal clear.**

Start with:
> Explique-moi ce que tu veux, dans tes mots.

Then ask what's missing:
- **Qui ?** - Qui déclenche cette action ?
- **Quoi ?** - Concrètement, il se passe quoi ?
- **Quand ?** - Dans quelles conditions ça marche ?
- **Sinon ?** - Qu'est-ce qui se passe si les conditions ne sont pas remplies ?

**Don't ask questions already answered.**

## Step 3: Reformulate and confirm

> Si je comprends bien :
> - [Qui] fait [Quoi]
> - Ça marche si [conditions]
> - Sinon [comportement d'erreur]
>
> C'est correct ?

**Wait for explicit confirmation.**

## Step 4: Write spec

```bash
mkdir -p .claude/temp
```

Create `.claude/temp/spec.md`:

```markdown
# Feature: {name}

## Intent
{User's exact words, quoted}

## Behavior
- Actor: {who}
- Action: {what}
- Success when: {conditions}
- Failure when: {conditions} → {error/behavior}

## Confirmed by user
```

## Step 5: Next step

> Spec écrite dans `.claude/temp/spec.md`
>
> Prochaine étape : `/clear` puis `/specify`
