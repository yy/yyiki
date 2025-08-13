from utils import is_safe_path

# Quick inline test
print("Testing path validation...")

# Should return True
print(f"is_safe_path('page'): {is_safe_path('page')}")
print(f"is_safe_path('folder/page'): {is_safe_path('folder/page')}")

# Should return False
print(f"is_safe_path('../etc/passwd'): {is_safe_path('../etc/passwd')}")
print(f"is_safe_path('/etc/passwd'): {is_safe_path('/etc/passwd')}")
print(f"is_safe_path('page;rm -rf'): {is_safe_path('page;rm -rf')}")

# Now test path2filename
from utils import path2filename
class MockPages:
    root = "/tmp/pages"

pages = MockPages()

print("\nTesting path2filename...")
try:
    result = path2filename(pages, "../etc/passwd")
    print(f"ERROR: Should have raised ValueError but got: {result}")
except ValueError as e:
    print(f"SUCCESS: Blocked '../etc/passwd' with error: {e}")

try:
    result = path2filename(pages, "valid/page") 
    print(f"SUCCESS: Valid path returned: {result}")
except Exception as e:
    print(f"ERROR: Valid path failed: {e}")