# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend, featuring JWT-based authentication, secure password hashing, and persistent data storage.

## Features

- ✅ User registration with validation
- ✅ Secure login with JWT tokens  
- ✅ Protected user profile access
- ✅ Token-based logout functionality
- ✅ Password hashing with bcrypt
- ✅ SQLite database for persistent storage
- ✅ Responsive frontend interface
- ✅ Comprehensive test suite

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── main.py             # Main FastAPI application
│   ├── database.py         # Database models and configuration
│   ├── auth.py             # Authentication utilities
│   ├── schemas.py          # Pydantic models
│   └── requirements.txt    # Backend dependencies
├── frontend/               # HTML/JavaScript frontend
│   ├── index.html          # Main frontend page
│   └── script.js           # Frontend JavaScript logic
├── tests/                  # Test suite
│   ├── test_auth_api.py    # API tests
│   └── requirements.txt    # Test dependencies
└── README.md               # This file
```

## API Endpoints

All endpoints are prefixed with `/api/auth/`:

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive JWT token
- `POST /api/auth/logout` - Logout and invalidate token
- `GET /api/auth/profile` - Get current user profile (requires authentication)
- `GET /api/health` - Health check endpoint

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python main.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

Simply open `frontend/index.html` in your web browser, or serve it with a simple HTTP server:

```bash
cd frontend
python -m http.server 3000
```

Then visit `http://localhost:3000`

### 3. Running Tests

```bash
# Navigate to tests directory
cd tests

# Install test dependencies (ensure you're using the project virtual environment)
pip install -r requirements.txt

# Run the test suite (use the project's virtual environment)
# On Windows:
..\\.venv\\Scripts\\activate; pytest test_auth_api.py -v

# On Linux/Mac:
source ../.venv/bin/activate && pytest test_auth_api.py -v
```

## Usage Examples

### 1. Registration

**Request:**
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "john_doe",
    "password": "secure123"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "created_at": "2023-12-07T10:30:00"
}
```

### 2. Login

**Request:**
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "john_doe",
    "password": "secure123"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 3. Access Profile

**Request:**
```http
GET /api/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "created_at": "2023-12-07T10:30:00"
}
```

### 4. Logout

**Request:**
```http
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
    "message": "Successfully logged out"
}
```

## Security Features

- **Password Hashing**: Uses bcrypt for secure password hashing
- **JWT Tokens**: JSON Web Tokens for stateless authentication
- **Token Invalidation**: Proper logout with token blacklisting
- **Input Validation**: Server-side validation for all inputs
- **CORS Protection**: Configurable CORS middleware
- **SQL Injection Prevention**: SQLAlchemy ORM protection

## Configuration

### Environment Variables

Create a `.env` file in the backend directory for production:

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./auth_app.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend Configuration

Update the `API_BASE` variable in `frontend/script.js` to match your backend URL:

```javascript
const API_BASE = 'http://your-backend-domain.com/api/auth';
```

## Testing

The test suite includes comprehensive coverage of:

- ✅ User registration (success, validation, duplicates)
- ✅ User login (valid/invalid credentials)
- ✅ Profile access (authenticated/unauthenticated)
- ✅ Logout functionality (token invalidation)
- ✅ Complete authentication flow
- ✅ Error handling and edge cases

Run tests with verbose output:
```bash
pytest tests/test_auth_api.py -v --tb=short
```

## Production Deployment

### Backend Deployment

1. Set strong `SECRET_KEY` in environment
2. Use PostgreSQL or MySQL instead of SQLite
3. Set up HTTPS/TLS encryption
4. Configure proper CORS origins
5. Use a production ASGI server like Gunicorn

### Frontend Deployment

1. Serve static files through a web server (nginx, Apache)
2. Update API_BASE URL to production backend
3. Enable HTTPS
4. Implement proper error logging

## API Documentation

When the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Check SQLite file permissions
3. **CORS Errors**: Verify frontend URL in CORS configuration
4. **Token Errors**: Check token format and expiration

### Debug Mode

Run the backend in debug mode:
```bash
uvicorn main:app --reload --log-level debug
```

## License

This project is provided as-is for educational and development purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request