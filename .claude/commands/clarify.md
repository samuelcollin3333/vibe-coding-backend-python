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
> Tell me what you want, in your own words.

Then ask what's missing:
- **Who?** - Who triggers this action?
- **What?** - Concretely, what happens?
- **When?** - Under what conditions does it work?
- **Otherwise?** - What happens if the conditions aren't met?

**Don't ask questions already answered.**

## Step 3: Reformulate and confirm

> If I understand correctly:
> - [Who] does [What]
> - It works if [conditions]
> - Otherwise [error behavior]
>
> Is that correct?

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

> Spec written in `.claude/temp/spec.md`
>
> Next step: `/clear` then `/specify`
