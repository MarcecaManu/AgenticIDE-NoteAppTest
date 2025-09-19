# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- **User Registration**: Create new accounts with username and password
- **User Login**: Authenticate with JWT tokens
- **User Profile**: View authenticated user information
- **Secure Logout**: Token invalidation for security
- **Persistent Storage**: File-based user data storage
- **Password Security**: Bcrypt hashing for passwords
- **Token-based Auth**: JWT tokens for session management
- **Comprehensive Tests**: Full test coverage with pytest

## Project Structure

```
├── backend/
│   └── main.py           # FastAPI application with auth endpoints
├── frontend/
│   ├── index.html        # Frontend HTML with forms and UI
│   └── app.js            # JavaScript for API communication
├── tests/
│   └── test_auth_api.py  # Comprehensive API tests
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
# From the project root directory
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### 3. Open the Frontend

Open `frontend/index.html` in your web browser, or serve it with a simple HTTP server:

```bash
# From the frontend directory
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080` in your browser.

### 4. Run Tests

```bash
# From the project root directory
pytest tests/test_auth_api.py -v
```

## API Endpoints

### Authentication Endpoints

- **POST /api/auth/register**
  - Register a new user
  - Body: `{"username": "string", "password": "string"}`
  - Response: `{"message": "User registered successfully", "username": "string"}`

- **POST /api/auth/login**
  - Authenticate user and get JWT token
  - Body: `{"username": "string", "password": "string"}`
  - Response: `{"access_token": "string", "token_type": "bearer"}`

- **POST /api/auth/logout**
  - Invalidate user session
  - Headers: `Authorization: Bearer <token>`
  - Response: `{"message": "Successfully logged out"}`

- **GET /api/auth/profile**
  - Get current user profile
  - Headers: `Authorization: Bearer <token>`
  - Response: `{"username": "string", "created_at": "ISO datetime"}`

### Health Check

- **GET /**
  - Health check endpoint
  - Response: `{"message": "Authentication API is running"}`

## Security Features

1. **Password Hashing**: Passwords are hashed using bcrypt before storage
2. **JWT Tokens**: Secure token-based authentication with expiration
3. **Token Blacklisting**: Logout invalidates tokens immediately
4. **Input Validation**: Server-side validation for all inputs
5. **CORS Configuration**: Properly configured for frontend communication

## Frontend Features

1. **Single Page Application**: No page reloads during navigation
2. **Form Validation**: Client-side validation with user feedback
3. **Token Management**: Automatic token storage and header injection
4. **Error Handling**: User-friendly error messages
5. **Responsive Design**: Clean, modern UI that works on all devices

## Data Storage

User data is stored in a JSON file (`users.json`) with the following structure:

```json
{
  "username": {
    "username": "string",
    "hashed_password": "bcrypt_hash",
    "created_at": "ISO_datetime"
  }
}
```

## Testing

The test suite includes:

- User registration tests (success, duplicates, validation)
- User login tests (valid/invalid credentials)
- User logout tests (token invalidation)
- User profile tests (authentication required)
- Integration tests (complete auth flow)
- Health check tests

Run with verbose output:
```bash
pytest tests/test_auth_api.py -v --tb=short
```

## Development

### Backend Development

The FastAPI application is in `backend/main.py`. Key components:

- **Models**: Pydantic models for request/response validation
- **Security**: JWT token handling and password hashing
- **Storage**: File-based user persistence
- **Endpoints**: RESTful API endpoints for authentication

### Frontend Development

The frontend consists of:

- **HTML**: Single page with multiple sections
- **CSS**: Inline styles with modern, responsive design
- **JavaScript**: Vanilla JS with fetch API for backend communication

### Adding Features

To extend the system:

1. Add new endpoints in `backend/main.py`
2. Update frontend forms and JavaScript in `frontend/`
3. Add corresponding tests in `tests/test_auth_api.py`

## Production Considerations

For production deployment:

1. Change the `SECRET_KEY` in `backend/main.py`
2. Use a proper database instead of JSON file storage
3. Use Redis for token blacklisting
4. Configure CORS origins specifically
5. Add rate limiting and other security middleware
6. Use HTTPS for all communications
7. Set up proper logging and monitoring

## License

This project is provided as-is for educational and demonstration purposes.