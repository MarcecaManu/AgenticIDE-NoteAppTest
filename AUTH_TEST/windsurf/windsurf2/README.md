# Authentication Module

A full-stack authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- **User Registration**: Create new accounts with username and password
- **User Login**: Authenticate with JWT tokens
- **User Profile**: View authenticated user information
- **Secure Logout**: Token blacklisting for secure session termination
- **Password Security**: Bcrypt hashing for password storage
- **Persistent Storage**: SQLite database for user data
- **Token-based Authentication**: JWT with expiration handling

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application with auth endpoints
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML interface
│   └── app.js              # JavaScript for API communication
├── tests/
│   └── test_auth_api.py    # Comprehensive API tests
└── README.md               # This file
```

## API Endpoints

All endpoints are prefixed with `/api/auth/`:

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive JWT token
- `POST /api/auth/logout` - Logout and blacklist token
- `GET /api/auth/profile` - Get user profile (requires authentication)

## Setup and Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Serve the HTML file using any web server. For example, with Python:
```bash
python -m http.server 3000
```

The frontend will be available at `http://localhost:3000`

### Running Tests

1. Navigate to the tests directory:
```bash
cd tests
```

2. Run the tests:
```bash
pytest test_auth_api.py -v
```

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Token Blacklisting**: Logout invalidates tokens server-side
- **CORS Support**: Configured for cross-origin requests
- **Input Validation**: Pydantic models for request validation

## Database Schema

The SQLite database contains two tables:

### users
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE)
- `hashed_password` (TEXT)
- `created_at` (TIMESTAMP)

### blacklisted_tokens
- `id` (INTEGER PRIMARY KEY)
- `token` (TEXT UNIQUE)
- `blacklisted_at` (TIMESTAMP)

## Configuration

Key configuration options in `backend/main.py`:

- `SECRET_KEY`: JWT signing key (change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30 minutes)
- `DATABASE_PATH`: SQLite database file location

## Usage

1. Start the backend server
2. Open the frontend in a web browser
3. Register a new account or login with existing credentials
4. View your profile information
5. Logout to invalidate your session

## Testing

The test suite covers:
- User registration (success and duplicate username)
- User login (valid and invalid credentials)
- Profile retrieval (with and without valid tokens)
- Logout functionality and token blacklisting
- Password hashing verification
- JWT token structure validation

Run tests with: `pytest tests/test_auth_api.py -v`
