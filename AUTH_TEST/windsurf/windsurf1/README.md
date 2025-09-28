# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend, featuring JWT-based authentication, secure password hashing, and persistent user storage.

## Features

### Backend (FastAPI)
- **User Registration**: Secure user registration with password hashing
- **User Authentication**: JWT-based login system
- **Session Management**: Token-based logout with blacklisting
- **User Profile**: Protected endpoint for user data retrieval
- **Persistent Storage**: File-based user data storage (JSON)
- **Security**: bcrypt password hashing, JWT tokens, CORS support

### Frontend (HTML/JavaScript)
- **Responsive UI**: Modern, mobile-friendly interface
- **Registration Form**: User-friendly registration with validation
- **Login Form**: Secure login with error handling
- **Profile View**: Display user information and account details
- **Session Management**: Automatic token handling and logout
- **Real-time Feedback**: Toast notifications for all operations

### Testing
- **Comprehensive Test Suite**: 20+ automated tests using pytest
- **API Coverage**: Tests for all endpoints and edge cases
- **Integration Tests**: Complete user flow validation
- **Security Tests**: Token blacklisting and authentication verification

## Project Structure

```
├── backend/
│   └── main.py              # FastAPI application with all endpoints
├── frontend/
│   ├── index.html           # Main HTML interface
│   ├── styles.css           # Modern CSS styling
│   └── auth.js              # JavaScript authentication logic
├── tests/
│   └── test_auth_api.py     # Comprehensive pytest test suite
├── requirements.txt         # Python dependencies
└── README.md               # This documentation
```

## API Endpoints

### Authentication Endpoints (Base: `/api/auth/`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/auth/register` | Register new user | None |
| POST | `/api/auth/login` | User login | None |
| POST | `/api/auth/logout` | User logout | Bearer Token |
| GET | `/api/auth/profile` | Get user profile | Bearer Token |

### Request/Response Examples

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}

# Response (200 OK)
{
  "message": "User registered successfully"
}
```

#### Login User
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}

# Response (200 OK)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Profile
```bash
GET /api/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Response (200 OK)
{
  "username": "john_doe",
  "created_at": "2024-01-15T10:30:00.123456"
}
```

#### Logout
```bash
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Response (200 OK)
{
  "message": "Successfully logged out"
}
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Backend Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI Server**
   ```bash
   cd backend
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The API will be available at: `http://localhost:8000`
   
   Interactive API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Serve the Frontend**
   
   You can use any static file server. Here are a few options:
   
   **Option A: Python HTTP Server**
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   
   **Option B: Node.js HTTP Server**
   ```bash
   cd frontend
   npx http-server -p 3000
   ```
   
   **Option C: Live Server (VS Code Extension)**
   - Install the "Live Server" extension in VS Code
   - Right-click on `index.html` and select "Open with Live Server"

   The frontend will be available at: `http://localhost:3000`

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=backend

# Run specific test class
pytest tests/test_auth_api.py::TestUserRegistration -v
```

## Security Features

### Password Security
- **bcrypt Hashing**: Passwords are hashed using bcrypt with salt
- **No Plain Text Storage**: Passwords are never stored in plain text
- **Secure Transmission**: Passwords are only sent over HTTPS in production

### JWT Token Security
- **Signed Tokens**: All tokens are cryptographically signed
- **Expiration**: Tokens expire after 30 minutes
- **Blacklisting**: Logout invalidates tokens immediately
- **Bearer Authentication**: Standard Authorization header format

### Data Persistence
- **File-based Storage**: User data stored in `users.json`
- **Structured Data**: JSON format for easy management
- **Atomic Operations**: Safe concurrent access patterns

## Configuration

### Environment Variables (Recommended for Production)

```bash
# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DB_FILE=users.json

# CORS (Production)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Production Considerations

1. **Change Secret Key**: Use a strong, random secret key
2. **HTTPS Only**: Serve over HTTPS in production
3. **CORS Configuration**: Restrict origins to your domain
4. **Database Migration**: Consider PostgreSQL/MySQL for production
5. **Rate Limiting**: Implement rate limiting for auth endpoints
6. **Logging**: Add comprehensive logging for security events

## Frontend Usage

### User Registration
1. Click "Register here" link
2. Enter username and password
3. Confirm password
4. Click "Register" button
5. Redirected to login form on success

### User Login
1. Enter username and password
2. Click "Login" button
3. Redirected to profile page on success
4. Token stored in localStorage

### View Profile
1. After login, profile is automatically loaded
2. Click "Refresh Profile" to reload data
3. Displays username and registration date

### Logout
1. Click "Logout" button in header
2. Token is invalidated on server
3. Redirected to login form
4. Token removed from localStorage

## Testing

The test suite includes:

### Registration Tests
- Successful registration
- Duplicate username prevention
- Input validation
- Password hashing verification

### Login Tests
- Valid credential authentication
- Invalid username/password handling
- JWT token generation
- Missing credential validation

### Logout Tests
- Valid token invalidation
- Invalid token handling
- Token blacklisting
- Missing authorization handling

### Profile Tests
- Authenticated profile retrieval
- Token validation
- Blacklisted token rejection
- Missing authorization handling

### Integration Tests
- Complete user flow (register → login → profile → logout)
- Multiple user scenarios
- Token isolation between users

## Error Handling

### Common HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 200 | Success | Operation completed successfully |
| 400 | Bad Request | Invalid input data, duplicate username |
| 401 | Unauthorized | Invalid credentials, expired/invalid token |
| 403 | Forbidden | Missing authorization header |
| 404 | Not Found | User not found |
| 422 | Validation Error | Missing required fields |
| 500 | Server Error | Internal server error |

### Frontend Error Messages

The frontend provides user-friendly error messages for:
- Network connectivity issues
- Invalid credentials
- Registration conflicts
- Session expiration
- Server errors

## Development

### Adding New Features

1. **Backend**: Add new endpoints in `backend/main.py`
2. **Frontend**: Update `frontend/auth.js` for new functionality
3. **Tests**: Add corresponding tests in `tests/test_auth_api.py`
4. **Documentation**: Update this README

### Code Style

- **Backend**: Follow PEP 8 Python style guidelines
- **Frontend**: Use consistent JavaScript ES6+ patterns
- **Tests**: Descriptive test names and comprehensive coverage

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS is configured for frontend origin
   - Check that frontend is making requests to correct backend URL

2. **Token Issues**
   - Verify token is included in Authorization header
   - Check token expiration (30 minutes default)
   - Clear localStorage if tokens are corrupted

3. **File Permissions**
   - Ensure backend can write to `users.json`
   - Check directory permissions for data storage

4. **Port Conflicts**
   - Backend default: 8000
   - Frontend default: 3000
   - Change ports if conflicts occur

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export FASTAPI_DEBUG=true
```

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:
1. Check this README for common solutions
2. Review the test suite for usage examples
3. Examine the API documentation at `/docs`
4. Check browser console for frontend errors
