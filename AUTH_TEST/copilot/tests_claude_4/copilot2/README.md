# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and plain HTML/JavaScript frontend, featuring JWT token-based authentication, secure password hashing, and comprehensive test coverage.

## Features

- ✅ **Secure User Registration** - Username validation and secure password hashing
- ✅ **JWT Token Authentication** - Token-based login with automatic expiration
- ✅ **Session Management** - Secure logout with token blacklisting
- ✅ **User Profile Management** - Protected profile access
- ✅ **Persistent Data Storage** - SQLite database with proper schema
- ✅ **Input Validation** - Client and server-side validation
- ✅ **Responsive Frontend** - Clean, modern HTML/CSS/JavaScript interface
- ✅ **Comprehensive Testing** - Full test suite with pytest
- ✅ **CORS Support** - Cross-origin resource sharing enabled

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application and routes
│   ├── auth.py              # Authentication utilities (JWT, hashing)
│   ├── database.py          # Database operations and models
│   ├── models.py            # Pydantic models for validation
│   └── requirements.txt     # Backend dependencies
├── frontend/
│   ├── index.html           # Main HTML interface
│   └── script.js            # JavaScript for API communication
├── tests/
│   ├── conftest.py          # Test configuration and fixtures
│   ├── test_auth_api.py     # Comprehensive API tests
│   └── requirements.txt     # Test dependencies
└── README.md                # This file
```

## API Endpoints

### Authentication Routes (Base path: `/api/auth/`)

| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|-------------------------|
| POST | `/api/auth/register` | Register new user | ❌ |
| POST | `/api/auth/login` | User login | ❌ |
| POST | `/api/auth/logout` | User logout | ✅ |
| GET | `/api/auth/profile` | Get user profile | ✅ |

### Additional Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve frontend application |
| GET | `/health` | Health check endpoint |

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```powershell
   cd backend
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set environment variables (optional):**
   ```powershell
   $env:SECRET_KEY = "your-super-secret-key-change-in-production"
   ```

4. **Run the server:**
   ```powershell
   python main.py
   ```
   
   Or using uvicorn directly:
   ```powershell
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The backend will be available at `http://localhost:8000`

### Frontend Access

The frontend is automatically served by the FastAPI server at:
- **Main Application:** `http://localhost:8000`
- **Static Files:** `http://localhost:8000/static/`

### Testing

1. **Install test dependencies:**
   ```powershell
   cd tests
   pip install -r requirements.txt
   ```

2. **Run tests:**
   ```powershell
   pytest test_auth_api.py -v
   ```

3. **Run tests with coverage:**
   ```powershell
   pytest test_auth_api.py --cov=../backend --cov-report=html
   ```

## API Usage Examples

### User Registration
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "securepassword123"
     }'
```

**Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "created_at": "2025-09-16T10:30:00"
}
```

### User Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "securepassword123"
     }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Profile
```bash
curl -X GET "http://localhost:8000/api/auth/profile" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "created_at": "2025-09-16T10:30:00"
}
```

### Logout
```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## Frontend Usage

### Registration Flow
1. Click "Don't have an account? Sign up"
2. Enter username (3+ characters) and password (6+ characters)
3. Confirm password
4. Click "Sign Up"
5. Upon success, automatically redirected to login

### Login Flow
1. Enter registered username and password
2. Click "Sign In"
3. Upon success, redirected to profile page

### Profile Management
1. View user information (ID, username, registration date)
2. Click "Logout" to end session

### Features
- **Form Validation:** Real-time client-side validation
- **Error Handling:** Clear error messages for failed operations
- **Loading States:** Visual feedback during API calls
- **Token Management:** Automatic token storage and cleanup
- **Responsive Design:** Works on desktop and mobile devices

## Security Features

### Password Security
- ✅ **Bcrypt Hashing:** Passwords hashed with bcrypt + salt
- ✅ **Minimum Length:** 6 character minimum requirement
- ✅ **Never Stored Plain:** Plain text passwords never stored or logged

### JWT Token Security
- ✅ **Signed Tokens:** HMAC SHA-256 signature
- ✅ **Expiration:** 30-minute token lifetime
- ✅ **Blacklisting:** Logout invalidates tokens server-side
- ✅ **Bearer Authentication:** Standard Authorization header

### API Security
- ✅ **Input Validation:** Pydantic models validate all inputs
- ✅ **SQL Injection Protection:** Parameterized queries
- ✅ **CORS Configuration:** Configurable cross-origin policies
- ✅ **Error Handling:** Secure error messages (no sensitive data leakage)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Blacklisted Tokens Table
```sql
CREATE TABLE blacklisted_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Test Coverage

The test suite includes comprehensive coverage for:

### Registration Tests
- ✅ Successful user registration
- ✅ Duplicate username handling
- ✅ Username validation (length, format)
- ✅ Password validation (length requirements)

### Login Tests
- ✅ Successful authentication
- ✅ Invalid username handling
- ✅ Wrong password handling
- ✅ Missing credentials validation

### Logout Tests
- ✅ Successful logout
- ✅ Invalid token handling
- ✅ Missing authorization handling
- ✅ Token blacklisting verification

### Profile Tests
- ✅ Authenticated profile access
- ✅ Unauthorized access prevention
- ✅ Invalid token handling
- ✅ Malformed authorization headers

### Integration Tests
- ✅ Complete user flow (register → login → profile → logout)
- ✅ Multiple user isolation
- ✅ Health check endpoint

## Configuration

### Environment Variables
- `SECRET_KEY`: JWT signing secret (default: dev key - **change in production**)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30 minutes)

### Database
- **File:** `users.db` (SQLite, created automatically)
- **Location:** Backend directory
- **Schema:** Auto-initialized on startup

## Development

### Adding New Features
1. Update database schema in `database.py`
2. Add Pydantic models in `models.py`
3. Implement endpoints in `main.py`
4. Add authentication logic in `auth.py`
5. Write tests in `tests/test_auth_api.py`
6. Update frontend JavaScript if needed

### Running in Development
```powershell
# Backend with auto-reload
uvicorn main:app --reload

# Run tests in watch mode
pytest --watch

# Frontend development (served by FastAPI)
# No separate server needed - visit http://localhost:8000
```

## Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Configure specific CORS origins (remove `allow_origins=["*"]`)
- [ ] Use HTTPS in production
- [ ] Set up proper database backup procedures
- [ ] Configure log levels appropriately
- [ ] Implement rate limiting
- [ ] Set up monitoring and health checks

### Deployment Options
- **Docker:** Containerize with Dockerfile
- **Cloud:** Deploy to AWS, GCP, Azure, or Heroku
- **VPS:** Use nginx + gunicorn for production serving
- **Serverless:** Adapt for AWS Lambda or similar

## License

This project is provided as an example implementation. Feel free to use and modify as needed for your applications.

## Support

For issues or questions:
1. Check the test suite for usage examples
2. Review the API documentation above
3. Examine the source code comments
4. Test locally with the provided examples