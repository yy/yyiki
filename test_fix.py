#!/usr/bin/env python3
"""Quick test to verify security fix."""

from utils import path2filename, is_safe_path
from unittest.mock import Mock

# Test is_safe_path
print("Testing is_safe_path...")
test_cases = {
    # Valid paths
    "page": True,
    "folder/page": True,
    "page-name": True,
    "page_name": True,
    "page name": True,
    
    # Invalid paths
    "../etc/passwd": False,
    "../../etc": False,
    "/etc/passwd": False,
    "page/../../../etc": False,
    "page;rm -rf": False,
    "": False,
}

for path, expected in test_cases.items():
    result = is_safe_path(path)
    status = "PASS" if result == expected else "FAIL"
    print(f"{status}: is_safe_path('{path}') = {result} (expected {expected})")

# Test path2filename
print("\nTesting path2filename...")
pages = Mock()
pages.root = "/tmp/test_pages"

# Test that attacks are blocked
attacks = [
    "../etc/passwd",
    "../../etc/passwd", 
    "page/../../../etc/passwd",
    "/etc/passwd",
]

for attack in attacks:
    try:
        result = path2filename(pages, attack)
        print(f"FAIL: path2filename('{attack}') should have raised ValueError but returned '{result}'")
    except ValueError as e:
        print(f"PASS: path2filename('{attack}') blocked with: {e}")
    except Exception as e:
        print(f"ERROR: path2filename('{attack}') raised unexpected {type(e).__name__}: {e}")

# Test valid paths work
try:
    result = path2filename(pages, "valid/page")
    print(f"\nPASS: Valid path 'valid/page' -> '{result}'")
except Exception as e:
    print(f"\nFAIL: Valid path raised error: {e}")

print("\nTest completed!")