# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and vanilla JavaScript frontend, featuring JWT-based authentication, secure password hashing, and persistent storage.

## Features

- ✅ User registration and login
- ✅ JWT token-based authentication
- ✅ Secure password hashing with bcrypt
- ✅ Persistent storage with SQLite database
- ✅ Token invalidation on logout
- ✅ Protected profile endpoint
- ✅ Modern, responsive UI
- ✅ Comprehensive test suite

## Project Structure

```
.
├── backend/              # FastAPI backend application
│   ├── main.py          # Main application and API endpoints
│   ├── auth.py          # Authentication logic and JWT handling
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic schemas for validation
│   ├── database.py      # Database configuration
│   └── requirements.txt # Python dependencies
├── frontend/            # Plain HTML/CSS/JS frontend
│   ├── index.html      # Main HTML page
│   ├── styles.css      # Styling
│   └── app.js          # JavaScript for API calls and UI updates
├── tests/              # Automated tests
│   └── test_auth.py    # Pytest test suite for all endpoints
└── README.md           # This file
```

## API Endpoints

### Base Path: `/api/auth/`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register a new user | No |
| POST | `/api/auth/login` | Login and receive JWT token | No |
| POST | `/api/auth/logout` | Invalidate current token | Yes |
| GET | `/api/auth/profile` | Get current user profile | Yes |

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- uv (Fast Python package manager) - Install: `pip install uv`
- A modern web browser

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
# Windows
uv venv --python 3.12
.venv\Scripts\activate

# Linux/Mac
uv venv --python 3.12
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

**Or simply use the provided scripts** (recommended):
```bash
# Windows: start_backend.bat
# Linux/Mac: ./start_backend.sh
```

4. Run the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Serve the frontend using Python's built-in HTTP server:
```bash
# Python 3
python -m http.server 8080

# Or use any other static file server
```

The frontend will be available at `http://localhost:8080`

**Note:** Make sure to update the `API_BASE_URL` in `frontend/app.js` if your backend runs on a different URL.

### Running Tests

1. Navigate to the tests directory:
```bash
cd tests
```

2. Run the test suite with pytest:
```bash
pytest test_auth.py -v
```

Or run from the project root:
```bash
pytest tests/test_auth.py -v
```

## Usage Guide

### 1. Register a New Account

- Open the frontend in your browser
- Fill in the registration form with:
  - Username (minimum 3 characters)
  - Password (minimum 6 characters)
- Click "Register"
- You'll see a success message

### 2. Login

- Fill in the login form with your credentials
- Click "Login"
- Upon successful login, you'll see your profile

### 3. View Profile

- After logging in, the profile section displays:
  - User ID
  - Username
  - Account creation date

### 4. Logout

- Click the "Logout" button in the profile section
- You'll be redirected back to the login/register forms
- Your token will be invalidated

## API Usage Examples

### Register a New User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "secure_password123"}'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "secure_password123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Profile (Authenticated)

```bash
curl -X GET "http://localhost:8000/api/auth/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Logout

```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Security Features

- **Password Hashing**: Passwords are hashed using bcrypt before storage
- **JWT Tokens**: Stateless authentication using JSON Web Tokens
- **Token Expiration**: Tokens expire after 30 minutes
- **Token Blacklist**: Logout invalidates tokens by adding them to a blacklist
- **Input Validation**: Pydantic models validate all input data
- **CORS**: Configured to prevent unauthorized cross-origin requests

## Testing

The test suite includes comprehensive tests for:

- ✅ User registration (success and validation)
- ✅ Duplicate username handling
- ✅ User login (success and failure cases)
- ✅ Profile retrieval with authentication
- ✅ Logout and token invalidation
- ✅ Password hashing verification
- ✅ Complete authentication flow

Run all tests:
```bash
pytest tests/test_auth.py -v
```

Run specific test:
```bash
pytest tests/test_auth.py::TestAuthentication::test_login_success -v
```

## Database

The application uses SQLite for persistent storage:
- **Production DB**: `auth_database.db` (created in backend directory)
- **Test DB**: `test_auth_database.db` (created during tests)

The database schema includes:
- User ID (primary key)
- Username (unique, indexed)
- Hashed password
- Creation timestamp

## Configuration

Key configuration values in `backend/auth.py`:
- `SECRET_KEY`: Used for JWT signing (change in production!)
- `ALGORITHM`: HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 30 minutes

## Development Notes

- The frontend uses localStorage to persist the JWT token
- All API calls are made using the Fetch API
- The UI updates without page reloads
- Error messages are displayed inline
- The backend uses dependency injection for database sessions

## Production Considerations

Before deploying to production:

1. **Change the SECRET_KEY** in `backend/auth.py` to a secure random string
2. **Configure CORS** to allow only specific origins
3. **Use HTTPS** for all communication
4. **Set up proper environment variables** for configuration
5. **Use a production database** (PostgreSQL, MySQL) instead of SQLite
6. **Implement rate limiting** to prevent brute force attacks
7. **Add refresh tokens** for better security
8. **Set up proper logging** and monitoring

## License

This project is provided as-is for educational purposes.

## Author

Built with FastAPI, SQLAlchemy, and vanilla JavaScript.

