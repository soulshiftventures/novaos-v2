#!/usr/bin/env python3
"""Test if cryptography imports successfully"""

import sys

print("Python version:", sys.version)
print("=" * 60)

try:
    print("Attempting to import cryptography...")
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    print("✓ SUCCESS: cryptography imported successfully")
    print(f"  Fernet: {Fernet}")
    print(f"  hashes: {hashes}")
    print(f"  PBKDF2HMAC: {PBKDF2HMAC}")
except ImportError as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
