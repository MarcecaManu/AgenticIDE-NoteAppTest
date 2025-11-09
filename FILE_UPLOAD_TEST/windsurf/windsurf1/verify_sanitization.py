"""
Quick verification script for filename sanitization
"""
import re

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other security issues"""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove path traversal sequences (..)
    filename = filename.replace('..', '_')
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    return filename

# Test cases from the failing tests
test_cases = [
    "../../../etc/passwd.txt",
    "..\\..\\..\\windows\\system32\\config\\sam.txt",
    "....//....//....//etc//passwd.txt",
    "/etc/passwd.txt",
    "C:\\Windows\\System32\\config\\sam.txt",
    'test<>:"/\\|?*file.txt'
]

print("Testing filename sanitization:\n")
for test_file in test_cases:
    sanitized = sanitize_filename(test_file)
    has_dots = ".." in sanitized
    has_slash = "/" in sanitized
    has_backslash = "\\" in sanitized
    
    print(f"Original:  {test_file}")
    print(f"Sanitized: {sanitized}")
    print(f"  Contains '..' : {has_dots}")
    print(f"  Contains '/'  : {has_slash}")
    print(f"  Contains '\\' : {has_backslash}")
    print(f"  ✓ PASS" if not (has_dots or has_slash or has_backslash) else "  ✗ FAIL")
    print()
