# Authentication Module

This is a full-stack authentication module using FastAPI for the backend and HTML/JavaScript for the frontend.

## Project Structure

```
.
├── backend/
│   ├── models.py        # Data models and schemas
│   ├── database.py      # User database operations
│   ├── auth.py         # Authentication logic
│   └── main.py         # FastAPI application and routes
├── frontend/
│   ├── index.html      # Frontend UI
│   └── script.js       # Frontend logic
├── tests/
│   └── test_auth.py    # Backend API tests
└── run.py              # Application entry point
```

## Features

- User registration with username and password
- User login with JWT token authentication
- User logout
- Protected profile endpoint
- Persistent user storage
- Password hashing
- Automated tests

## Running the Application

1. Install dependencies:
```bash
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart pytest httpx
```

2. Start the backend server:
```bash
python run.py
```

3. Open the frontend:
Open `frontend/index.html` in a web browser

## Running Tests

```bash
pytest tests/
```

## API Endpoints

- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - Authenticate and get JWT token
- POST `/api/auth/logout` - Logout (client-side token removal)
- GET `/api/auth/profile` - Get authenticated user profile

## Security Features

- Password hashing using bcrypt
- JWT token-based authentication
- Protected routes requiring valid tokens
- CORS middleware configured
- No plain-text password storage
