#!/usr/bin/env python3
"""
Pre-write hook: Check for architecture violations.

Exit codes:
- 0: OK (possibly with warnings)
- 2: BLOCK - critical violation detected

BLOCKING RULES (exit 2):
1. Domain cannot import from infrastructure
2. Domain cannot import from application
3. Application handlers cannot import infrastructure directly
4. Domain entities must be frozen dataclass

WARNING RULES (exit 0 with message):
1. Domain class without Rules/Repository suffix
2. File over 200 lines
3. Handler missing standard steps
"""

import json
import re
import sys


# =============================================================================
# BLOCKING RULES - These MUST NOT be violated
# =============================================================================

FORBIDDEN_IMPORTS = {
    "domain_imports_infra": (
        r"src/domain/",
        r"from src\.infrastructure|from infrastructure",
        "Domain cannot import from infrastructure"
    ),
    "domain_imports_app": (
        r"src/domain/",
        r"from src\.application|from application",
        "Domain cannot import from application"
    ),
    "handler_imports_infra": (
        r"src/application/.*handler\.py",
        r"from src\.infrastructure\.|from infrastructure\.",
        "Handlers must receive dependencies via __init__, not import directly"
    ),
}


def check_forbidden_imports(file_path: str, content: str) -> tuple[bool, str]:
    """Check for forbidden import patterns. Returns (is_valid, error_message)."""
    for rule_name, (path_pattern, import_pattern, error_msg) in FORBIDDEN_IMPORTS.items():
        if re.search(path_pattern, file_path):
            if re.search(import_pattern, content):
                return False, f"❌ BLOCKED: {error_msg}\n   File: {file_path}\n   Fix: Use dependency injection"
    return True, ""


def check_frozen_dataclass(file_path: str, content: str) -> tuple[bool, str]:
    """Domain entities must be frozen dataclass."""
    if not re.search(r"src/domain/", file_path):
        return True, ""

    # Skip rules and repository files
    if "_rules.py" in file_path or "_repository.py" in file_path:
        return True, ""

    # Look for dataclass without frozen=True
    # Pattern: @dataclass followed by class definition, without frozen=True
    dataclass_pattern = r"@dataclass\s*(?!\(.*frozen\s*=\s*True)(\(.*?\))?\s*\nclass"

    if re.search(dataclass_pattern, content):
        return False, f"❌ BLOCKED: Domain entities must be immutable\n   File: {file_path}\n   Fix: Use @dataclass(frozen=True)"

    return True, ""


def check_domain_test_exists(file_path: str, content: str) -> tuple[bool, str]:
    """Domain files should have corresponding tests."""
    if not re.search(r"src/domain/", file_path):
        return True, ""

    if file_path.endswith("__init__.py"):
        return True, ""

    # This is informational - we can't check if test exists from content alone
    # This would need to be a post-commit hook checking filesystem
    return True, ""


# =============================================================================
# WARNING RULES - Alert but don't block
# =============================================================================

def warn_file_size(file_path: str, content: str) -> str | None:
    """Warn if file is getting large."""
    line_count = content.count('\n')
    if line_count > 200:
        return f"⚠️  File has {line_count} lines (>200). Consider splitting."
    return None


def warn_domain_naming(file_path: str, content: str) -> str | None:
    """Warn if domain class doesn't follow naming convention."""
    if not re.search(r"src/domain/", file_path):
        return None

    if file_path.endswith("__init__.py"):
        return None

    # Check for classes that aren't Entity, Rules, or Repository
    classes = re.findall(r"class (\w+)", content)

    for cls in classes:
        # Valid patterns
        if cls.endswith("Rules"):
            continue
        if cls.endswith("Repository"):
            continue
        if cls.endswith("Error") or cls.endswith("Exception"):
            continue
        # Entity names are flexible (Order, User, etc.) - don't warn
        # Only warn for obviously wrong patterns
        if cls.endswith("Service") or cls.endswith("Manager") or cls.endswith("Helper"):
            return f"⚠️  Class '{cls}' in domain looks like infrastructure. Domain should only have Entities, Rules, and Repositories."

    return None


def warn_handler_structure(file_path: str, content: str) -> str | None:
    """Warn if handler doesn't follow 5-step pattern."""
    if not re.search(r"handler\.py$", file_path):
        return None

    # Check for handle method
    if "def handle(" not in content and "async def handle(" not in content:
        return f"⚠️  Handler without handle() method"

    # Light check: should have some key operations
    expected_patterns = [
        (r"# ?(1|validate|validation)", "validate"),
        (r"# ?(2|fetch|get|load)", "fetch"),
        (r"# ?(3|rule|business|check)", "apply rules"),
        (r"# ?(4|save|persist|store)", "persist"),
    ]

    missing = []
    for pattern, step in expected_patterns:
        if not re.search(pattern, content, re.IGNORECASE):
            missing.append(step)

    if len(missing) >= 3:  # Most steps missing
        return f"⚠️  Handler may be missing standard steps. Expected: validate → fetch → rules → persist → events"

    return None


# =============================================================================
# MAIN
# =============================================================================

def main():
    try:
        input_data = json.load(sys.stdin)

        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path") or tool_input.get("path", "")
        content = tool_input.get("content") or tool_input.get("file_text", "")

        # Only check Python files
        if not file_path.endswith(".py"):
            sys.exit(0)

        # Skip if no content (edit operations)
        if not content:
            sys.exit(0)

        # --- BLOCKING CHECKS ---

        is_valid, error = check_forbidden_imports(file_path, content)
        if not is_valid:
            print(error, file=sys.stderr)
            sys.exit(2)

        is_valid, error = check_frozen_dataclass(file_path, content)
        if not is_valid:
            print(error, file=sys.stderr)
            sys.exit(2)

        # --- WARNING CHECKS ---

        warnings = []

        warn = warn_file_size(file_path, content)
        if warn:
            warnings.append(warn)

        warn = warn_domain_naming(file_path, content)
        if warn:
            warnings.append(warn)

        warn = warn_handler_structure(file_path, content)
        if warn:
            warnings.append(warn)

        # Print warnings but don't block
        if warnings:
            print(f"\n{'='*50}", file=sys.stderr)
            print(f"Architecture warnings for: {file_path}", file=sys.stderr)
            for w in warnings:
                print(f"  {w}", file=sys.stderr)
            print(f"{'='*50}\n", file=sys.stderr)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
