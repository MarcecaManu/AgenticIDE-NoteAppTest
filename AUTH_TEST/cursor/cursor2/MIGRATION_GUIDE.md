# Migration Guide - Dependency Fix

## Issue Fixed

Fixed bcrypt password hashing errors by:
- Splitting `passlib[bcrypt]` into separate `passlib` and `bcrypt` dependencies
- Updated to `bcrypt==4.0.1` for better compatibility
- Added password length validation (max 72 bytes for bcrypt)
- Added better error handling in registration endpoint
- Updated scripts to use `uv` package manager with `.venv` directory

## Steps to Update Your Environment

### Windows

1. **Remove old virtual environment** (if exists):
```cmd
cd backend
rmdir /s /q venv
rmdir /s /q .venv
```

2. **Install new dependencies**:
```cmd
start_backend.bat
```

This will create a new `.venv` and install updated dependencies.

### Linux/Mac

1. **Remove old virtual environment** (if exists):
```bash
cd backend
rm -rf venv .venv
```

2. **Install new dependencies**:
```bash
./start_backend.sh
```

This will create a new `.venv` and install updated dependencies.

## What Changed

### backend/requirements.txt
```diff
- passlib[bcrypt]==1.7.4
+ passlib==1.7.4
+ bcrypt==4.0.1
```

### backend/schemas.py
- Added max_length=72 validation for passwords

### backend/auth.py
- Added password length validation in `get_password_hash()`

### backend/main.py
- Added proper error handling for registration endpoint

### Scripts
- Changed from `venv` to `.venv`
- Changed from `pip` to `uv pip`
- Updated all start and test scripts

## Verify the Fix

Run the tests to verify everything works:

```bash
# Windows
run_tests.bat

# Linux/Mac
./run_tests.sh
```

All tests should now pass!

## If You Still Have Issues

1. Make sure you've completely removed the old virtual environment
2. Ensure `uv` is installed: `pip install uv`
3. Delete any `.db` files in the backend directory
4. Try running the backend manually:
   ```bash
   cd backend
   uv venv --python 3.12
   # Windows: .venv\Scripts\activate
   # Linux/Mac: source .venv/bin/activate
   uv pip install -r requirements.txt
   uvicorn main:app --reload
   ```

