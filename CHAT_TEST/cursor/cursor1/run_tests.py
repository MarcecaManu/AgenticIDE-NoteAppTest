#!/usr/bin/env python3
"""
Test runner script for the Real-time Chat System
"""

import pytest
import sys
import os

if __name__ == "__main__":
    print("=" * 60)
    print("Real-time Chat System - Test Suite")
    print("=" * 60)
    print("\nRunning tests...\n")
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        "tests/test_chat_system.py",
        "-v",
        "--tb=short",
        "-s"
    ])
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Please check the output above.")
    print("=" * 60)
    
    sys.exit(exit_code)

