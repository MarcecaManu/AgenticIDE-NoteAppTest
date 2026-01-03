# Authentication Module

A full-stack authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- **User Registration**: Create new accounts with username and password validation
- **Secure Login**: JWT-based authentication with token management
- **User Profile**: View authenticated user information
- **Logout**: Token blacklisting for secure session termination
- **Password Security**: Bcrypt hashing for password storage
- **Persistent Storage**: SQLite database for user data
- **Comprehensive Tests**: Automated pytest suite with 18+ test cases

## Project Structure

```
.
├── backend/
│   ├── main.py          # FastAPI application with all auth endpoints
│   └── users.db         # SQLite database (created automatically)
├── frontend/
│   ├── index.html       # Single-page application UI
│   └── app.js           # Frontend logic and API integration
├── tests/
│   └── test_auth.py     # Comprehensive pytest test suite
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## API Endpoints

All endpoints are prefixed with `/api/auth/`:

### `POST /api/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "username": "string (3-50 chars)",
  "password": "string (min 6 chars)"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully"
}
```

### `POST /api/auth/login`
Authenticate and receive a JWT access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### `GET /api/auth/profile`
Get the authenticated user's profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "username": "string",
  "created_at": "2024-01-01T12:00:00"
}
```

### `POST /api/auth/logout`
Logout and invalidate the current token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Create and activate a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Important:** This project uses `bcrypt==4.0.1` for compatibility with `passlib`. Do not upgrade bcrypt to 5.x as it has breaking changes.

3. **Start the backend server:**
   
   **Windows:**
   ```bash
   .\start_backend.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start_backend.sh
   ./start_backend.sh
   ```
   
   Or manually:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   The API will be available at `http://localhost:8000`
   
   API documentation: `http://localhost:8000/docs`

4. **Serve the frontend (in a new terminal):**
   
   **Windows:**
   ```bash
   .\start_frontend.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start_frontend.sh
   ./start_frontend.sh
   ```
   
   Or manually:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   
   Open `http://localhost:3000` in your browser

## Running Tests

### Unit Tests

Run the automated test suite with pytest:

**Windows:**
```bash
.\run_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

Or manually:
```bash
python -m pytest tests/test_auth.py -v
```

For more detailed output:
```bash
python -m pytest tests/test_auth.py -v -s
```

### Integration Tests

With the backend server running, test the live API:

```bash
python test_api_integration.py
```

This will test the complete authentication flow against the running server.

### Test Coverage

The test suite includes:
- ✅ User registration (valid and invalid inputs)
- ✅ Duplicate username prevention
- ✅ Successful login with correct credentials
- ✅ Login failure with wrong credentials
- ✅ Profile retrieval with valid token
- ✅ Profile access denied without token
- ✅ Logout functionality
- ✅ Token blacklisting after logout
- ✅ Password hashing verification
- ✅ End-to-end authentication flow

## Security Features

1. **Password Hashing**: Passwords are hashed using bcrypt before storage
2. **JWT Tokens**: Secure token-based authentication with expiration
3. **Token Blacklisting**: Invalidated tokens are stored to prevent reuse
4. **Input Validation**: Pydantic models enforce data validation
5. **No Plain Text**: Passwords never stored or transmitted in plain text

## Usage

### Register a New Account
1. Open the frontend in your browser
2. Click "Register here"
3. Enter a username (3-50 characters) and password (minimum 6 characters)
4. Click "Register"

### Login
1. Enter your credentials on the login page
2. Click "Login"
3. You'll be redirected to your profile page

### View Profile
- After logging in, your profile displays your username and account creation date

### Logout
- Click the "Logout" button to end your session
- The token will be invalidated on the server

## Development

### Backend Configuration

Edit `backend/main.py` to customize:
- `SECRET_KEY`: Change for production deployment
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `DATABASE_PATH`: Database location

### Frontend Configuration

Edit `frontend/app.js` to change:
- `API_BASE_URL`: Backend server address

## Production Deployment

Before deploying to production:

1. **Change the SECRET_KEY** in `backend/main.py`
2. **Update CORS settings** to restrict allowed origins
3. **Use HTTPS** for secure token transmission
4. **Set secure environment variables** for sensitive data
5. **Consider using PostgreSQL** instead of SQLite for better scalability
6. **Implement rate limiting** to prevent abuse
7. **Add refresh tokens** for better UX

## Troubleshooting

### CORS Errors
- Ensure the backend server is running
- Check that `API_BASE_URL` in `app.js` matches your backend address
- Verify CORS middleware is properly configured

### Database Errors
- The database is created automatically in the `backend/` directory
- Delete `users.db` to reset the database

### Token Expiration
- Tokens expire after 30 minutes by default
- Login again to get a new token
- Consider implementing refresh tokens for production

## License

This project is provided as-is for educational purposes.

