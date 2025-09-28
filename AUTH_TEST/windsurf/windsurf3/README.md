# Full-Stack Authentication System

A complete authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- **User Registration**: Create new accounts with username/password
- **User Login**: Authenticate with JWT tokens
- **User Profile**: View authenticated user information
- **User Logout**: Secure token invalidation with blacklisting
- **Password Security**: Bcrypt hashing for secure password storage
- **Persistent Storage**: SQLite database for user data
- **Token-based Auth**: JWT tokens with expiration
- **Comprehensive Tests**: Full pytest test suite

## Project Structure

```
├── backend/
│   ├── main.py           # FastAPI application and API endpoints
│   ├── auth.py           # Authentication logic and JWT handling
│   ├── database.py       # SQLite database operations
│   ├── models.py         # Pydantic models for API
│   └── requirements.txt  # Backend dependencies
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── app.js           # JavaScript application logic
│   └── styles.css       # CSS styling
├── tests/
│   ├── test_auth_api.py  # Comprehensive API tests
│   └── requirements.txt  # Test dependencies
└── README.md
```

## API Endpoints

All endpoints are prefixed with `/api/auth/`:

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/profile` - Get user profile (requires Bearer token)
- `POST /api/auth/logout` - Logout and blacklist token

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
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Serve the files using a simple HTTP server:
   ```bash
   # Using Python
   python -m http.server 3000
   
   # Or using Node.js
   npx serve -s . -l 3000
   ```

The frontend will be available at `http://localhost:3000`

### Running Tests

1. Navigate to the tests directory:
   ```bash
   cd tests
   ```

2. Install test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the tests:
   ```bash
   pytest test_auth_api.py -v
   ```

## Usage

1. **Start the Backend**: Run the FastAPI server on port 8000
2. **Start the Frontend**: Serve the HTML files on port 3000
3. **Register**: Create a new account with username and password
4. **Login**: Authenticate to receive a JWT token
5. **View Profile**: Access your user information
6. **Logout**: Invalidate your session token

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with expiration
- **Token Blacklisting**: Secure logout with token invalidation
- **Input Validation**: Server-side validation for all inputs
- **CORS Support**: Configurable cross-origin resource sharing

## Testing

The test suite includes:

- **Registration Tests**: Valid/invalid user registration scenarios
- **Login Tests**: Authentication with various credential combinations
- **Profile Tests**: Token validation and user data retrieval
- **Logout Tests**: Token blacklisting and invalidation
- **Integration Tests**: Complete authentication flows
- **Multi-user Tests**: Independent user session management

Run tests with: `pytest tests/test_auth_api.py -v`

## Configuration

Key configuration options in `backend/auth.py`:

- `SECRET_KEY`: JWT signing key (change in production)
- `ALGORITHM`: JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (30 minutes)

## Production Considerations

- Change the `SECRET_KEY` to a secure random value
- Use environment variables for sensitive configuration
- Configure proper CORS origins instead of allowing all
- Use HTTPS in production
- Consider token refresh mechanisms for longer sessions
- Implement rate limiting for authentication endpoints
