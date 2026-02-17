#!/usr/bin/env python3
"""Fix recursive safe_datetime_now() calls"""

import re
from pathlib import Path

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Find and fix the function definition
    pattern = r'(def safe_datetime_now.*?:\s*""".*?"""\s*try:\s*)return safe_datetime_now\(\)'
    replacement = r'\1return datetime.now()'

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed: {filepath}")
        return True
    return False

# Fix all Python files
for py_file in Path('.').rglob('*.py'):
    if any(skip in str(py_file) for skip in ['.git', 'venv', '__pycache__']):
        continue
    try:
        fix_file(py_file)
    except Exception as e:
        pass
