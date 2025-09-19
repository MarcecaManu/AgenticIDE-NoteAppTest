# Authentication System

A full-stack authentication system built with FastAPI and plain HTML/JavaScript.

## Features

- User registration
- User login with JWT authentication
- User logout
- Protected profile endpoint
- Persistent data storage using SQLite
- Secure password hashing
- Automated tests

## Project Structure

```
.
├── backend/
│   ├── auth.py         # Authentication logic and utilities
│   ├── database.py     # Database configuration and session management
│   ├── main.py         # FastAPI application and endpoints
│   ├── models.py       # SQLAlchemy models
│   └── schemas.py      # Pydantic schemas
├── frontend/
│   ├── index.html      # Frontend interface
│   └── script.js       # Frontend logic
└── tests/
    └── test_auth.py    # API tests
```

## Setup and Running

1. Make sure you have Python 3.7+ installed

2. Install dependencies:
   ```
   pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart sqlalchemy pytest
   ```

3. Start the backend server:
   ```
   uvicorn backend.main:app --reload
   ```

4. Open the frontend:
   - Navigate to the `frontend` directory
   - Open `index.html` in a web browser or serve it using a local HTTP server

## Running Tests

To run the tests:

```
pytest tests/test_auth.py -v
```

## Security Notes

- In production, replace the secret key in `auth.py` with a secure value
- Configure CORS settings in `main.py` to allow only specific origins
- Use HTTPS in production
- Consider adding rate limiting for authentication endpoints
- Add password complexity requirements
- Implement refresh tokens for better security
