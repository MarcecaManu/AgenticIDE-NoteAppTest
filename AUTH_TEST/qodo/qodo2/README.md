# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI)
- **POST /api/auth/register** - Register new users with username/password
- **POST /api/auth/login** - Authenticate users and return JWT tokens
- **POST /api/auth/logout** - Invalidate user sessions/tokens
- **GET /api/auth/profile** - Get current user profile (requires authentication)

### Security Features
- Passwords are securely hashed using bcrypt
- JWT tokens for stateless authentication
- Token blacklisting for secure logout
- Input validation and error handling
- CORS support for frontend integration

### Frontend
- User registration with validation
- User login with credential verification
- Profile viewing for authenticated users
- Secure logout functionality
- Responsive design with modern UI
- Real-time form validation and error messages

### Data Persistence
- User data stored in JSON file (`users.json`)
- Persistent across server restarts
- Secure password hashing (never stored in plain text)

## Project Structure

```
├── backend/
│   ├── main.py           # FastAPI application and routes
│   ├── models.py         # Pydantic models and data structures
│   ├── auth.py           # Authentication logic and JWT handling
│   ├── database.py       # File-based database operations
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── styles.css        # CSS styling
│   └── app.js           # JavaScript application logic
├── tests/
│   ├── test_auth_api.py  # Comprehensive API tests
│   └── requirements.txt  # Test dependencies
└── README.md            # This file
```

## Setup and Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
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

2. Open `index.html` in a web browser:
   ```bash
   # On Windows
   start index.html
   
   # On macOS
   open index.html
   
   # On Linux
   xdg-open index.html
   ```

   Or serve it using a simple HTTP server:
   ```bash
   # Python 3
   python -m http.server 3000
   
   # Node.js (if you have http-server installed)
   npx http-server -p 3000
   ```

### Running Tests

1. Navigate to the tests directory:
   ```bash
   cd tests
   ```

2. Install test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the test suite:
   ```bash
   pytest test_auth_api.py -v
   ```

## API Documentation

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response (201 Created):**
```json
{
  "username": "john_doe",
  "id": 1
}
```

### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "username": "john_doe",
  "id": 1
}
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

## Test Coverage

The test suite includes comprehensive tests for:

- ✅ User registration (valid/invalid data, duplicates)
- ✅ User authentication (valid/invalid credentials)
- ✅ Profile retrieval (with/without valid tokens)
- ✅ Logout functionality (token blacklisting)
- ✅ Complete user flow (register → login → profile → logout)
- ✅ Data persistence verification
- ✅ Security validations (password hashing, token validation)

## Security Considerations

- Passwords are hashed using bcrypt with salt
- JWT tokens have expiration times (30 minutes default)
- Tokens are blacklisted on logout for security
- Input validation prevents common attacks
- CORS is configured (should be restricted in production)
- Secret key should be changed in production environment

## Usage Examples

### Frontend Usage
1. Open the frontend in a browser
2. Register a new account with username (3+ chars) and password (6+ chars)
3. Login with your credentials
4. View your profile information
5. Logout to end the session

### API Usage with curl
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Get Profile (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer TOKEN"

# Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer TOKEN"
```

## Development Notes

- The backend uses file-based storage (`users.json`) for simplicity
- In production, consider using a proper database (PostgreSQL, MySQL, etc.)
- The JWT secret key should be environment-specific and secure
- Consider implementing refresh tokens for better security
- Add rate limiting for production deployment
- Implement proper logging and monitoring