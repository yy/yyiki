#!/usr/bin/env python3
"""Test security fixes for path traversal vulnerability."""

import os
import sys
import tempfile
from unittest.mock import Mock

# Add current directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import path2filename, is_safe_path


def test_path_validation():
    """Test the is_safe_path function."""
    print("Testing path validation...")
    
    # Valid paths
    valid_paths = [
        "page",
        "folder/page",
        "folder/subfolder/page",
        "page-with-dashes",
        "page_with_underscores",
        "page with spaces",
        "CamelCase",
        "123numbers",
    ]
    
    # Invalid paths
    invalid_paths = [
        "../etc/passwd",
        "../../secret",
        "/etc/passwd",
        "page/../../../etc/passwd",
        "page/../../etc/passwd",
        "",
        "page!@#$%",
        "page;rm -rf /",
        "page&command",
        "page|pipe",
        "page`backtick`",
        "page$(command)",
        "page\x00null",
        "..",
        "....",
        "folder/../../../etc",
    ]
    
    print("\nTesting valid paths:")
    for path in valid_paths:
        result = is_safe_path(path)
        status = "✓" if result else "✗"
        print(f"  {status} '{path}' -> {result}")
        if not result:
            print(f"    ERROR: Expected True for valid path '{path}'")
    
    print("\nTesting invalid paths:")
    for path in invalid_paths:
        result = is_safe_path(path)
        status = "✓" if not result else "✗"
        print(f"  {status} '{path}' -> {result}")
        if result:
            print(f"    ERROR: Expected False for invalid path '{path}'")


def test_path2filename():
    """Test the path2filename function with various attack vectors."""
    print("\n\nTesting path2filename function...")
    
    # Create a mock pages object with a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        pages = Mock()
        pages.root = tmpdir
        
        print(f"\nUsing test directory: {tmpdir}")
        
        # Test valid paths
        print("\nTesting valid paths:")
        valid_tests = [
            ("page", os.path.join(tmpdir, "page.md")),
            ("folder/page", os.path.join(tmpdir, "folder", "page.md")),
            ("a/b/c", os.path.join(tmpdir, "a", "b", "c.md")),
        ]
        
        for input_path, expected in valid_tests:
            try:
                result = path2filename(pages, input_path)
                # Normalize both paths for comparison
                result_norm = os.path.normpath(result)
                expected_norm = os.path.normpath(expected)
                status = "✓" if result_norm == expected_norm else "✗"
                print(f"  {status} '{input_path}' -> '{result}'")
                if result_norm != expected_norm:
                    print(f"    Expected: '{expected}'")
            except Exception as e:
                print(f"  ✗ '{input_path}' -> ERROR: {e}")
        
        # Test attack vectors
        print("\nTesting attack vectors (should all raise ValueError):")
        attack_vectors = [
            "../etc/passwd",
            "../../etc/passwd",
            "../../../etc/passwd",
            "page/../../../etc/passwd",
            "/etc/passwd",
            "//etc/passwd",
            "page/../../sensitive",
            ".\\.\\..\\..\\windows\\system32",
            "page\x00.md",
            "page|command",
            "page;rm -rf /",
            "page`whoami`",
            "page$(id)",
            "..",
            "...",
            "....",
            "folder/../../../etc/passwd",
            "a/b/../../../etc/passwd",
            " ../etc/passwd",
            "../etc/passwd ",
            "\t../etc/passwd",
        ]
        
        for attack in attack_vectors:
            try:
                result = path2filename(pages, attack)
                print(f"  ✗ '{attack}' -> '{result}' (ERROR: Should have raised ValueError!)")
            except ValueError as e:
                print(f"  ✓ '{attack}' -> Blocked: {e}")
            except Exception as e:
                print(f"  ? '{attack}' -> Unexpected error: {type(e).__name__}: {e}")
        
        # Test that resolved paths stay within pages.root
        print("\nTesting boundary checks:")
        
        # Create a file outside the pages directory
        outside_file = os.path.join(os.path.dirname(tmpdir), "outside.txt")
        
        # Try to access it through path manipulation
        tricky_paths = [
            f"../{os.path.basename(outside_file)[:-4]}",  # Try to go up one level
            f"subfolder/../../{os.path.basename(outside_file)[:-4]}",  # Go down then up
        ]
        
        for tricky in tricky_paths:
            try:
                result = path2filename(pages, tricky)
                print(f"  ✗ '{tricky}' -> '{result}' (ERROR: Should have been blocked!)")
            except ValueError as e:
                print(f"  ✓ '{tricky}' -> Blocked: {e}")


if __name__ == "__main__":
    print("Security Test Suite for yyiki")
    print("=" * 50)
    
    test_path_validation()
    test_path2filename()
    
    print("\n" + "=" * 50)
    print("Security tests completed!")