#!/usr/bin/env python3
"""
Universal fix for all safe_datetime_now() calls in the codebase.
Adds safe_datetime_now() helper and replaces all safe_datetime_now() calls.
"""

import os
import re
from pathlib import Path

# Helper function to inject
SAFE_DATETIME_HELPER = """

def safe_datetime_now():
    \"\"\"Get current datetime with fallback for timestamp overflow\"\"\"
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)
"""

def has_datetime_import(content):
    """Check if file imports datetime"""
    return 'from datetime import' in content or 'import datetime' in content

def already_has_helper(content):
    """Check if safe_datetime_now already exists"""
    return 'def safe_datetime_now' in content

def add_helper_after_imports(content):
    """Add safe_datetime_now helper after imports"""
    lines = content.split('\n')

    # Find last import line
    last_import_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            last_import_idx = i

    # Insert helper after imports
    lines.insert(last_import_idx + 1, SAFE_DATETIME_HELPER)
    return '\n'.join(lines)

def replace_datetime_now_calls(content):
    """Replace safe_datetime_now() with safe_datetime_now()"""
    # Don't replace inside the helper function itself
    if 'def safe_datetime_now' in content:
        # Only replace outside the function
        pattern = r'(?<!def safe_datetime_now.*\n.*return )datetime\.now\(\)'
        content = re.sub(r'datetime\.now\(\)', 'safe_datetime_now()', content)
    else:
        content = content.replace('safe_datetime_now()', 'safe_datetime_now()')

    return content

def fix_file(filepath):
    """Fix safe_datetime_now() calls in a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Skip if no datetime usage
        if 'safe_datetime_now()' not in content:
            return False

        # Skip if no datetime import
        if not has_datetime_import(content):
            return False

        original_content = content

        # Add helper if needed
        if not already_has_helper(content):
            content = add_helper_after_imports(content)

        # Replace all calls
        content = replace_datetime_now_calls(content)

        # Only write if changed
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✓ Fixed: {filepath}")
            return True

        return False

    except Exception as e:
        print(f"✗ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all Python files in the project"""
    base_dir = Path('.')
    files_fixed = 0

    # Find all Python files
    for py_file in base_dir.rglob('*.py'):
        # Skip venv, git, pycache
        if any(skip in str(py_file) for skip in ['venv', '.git', '__pycache__', 'test_']):
            continue

        if fix_file(py_file):
            files_fixed += 1

    print(f"\n{'='*60}")
    print(f"Fixed {files_fixed} files")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
