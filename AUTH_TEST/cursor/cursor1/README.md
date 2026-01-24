# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- **User Registration**: Create new accounts with username and password
- **User Login**: Authenticate with JWT token-based authentication
- **User Profile**: View authenticated user information
- **User Logout**: Invalidate tokens securely
- **Persistent Storage**: SQLite database for user data
- **Password Security**: Bcrypt hashing with salts
- **Token Blacklisting**: Revoke JWT tokens on logout
- **Comprehensive Tests**: Full pytest test suite

## Project Structure

```
.
├── backend/
│   ├── main.py          # FastAPI application with all endpoints
│   └── users.db         # SQLite database (created automatically)
├── frontend/
│   ├── index.html       # Main HTML page
│   └── app.js           # JavaScript for API interaction
├── tests/
│   └── test_auth.py     # Pytest test suite
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. **Clone or download this project**

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

## Running the Application

### 1. Start the Backend Server

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 2. Serve the Frontend

You can use any static file server. For example:

**Using Python's built-in server**:
```bash
cd frontend
python -m http.server 8080
```

**Using Node.js http-server** (if installed):
```bash
cd frontend
npx http-server -p 8080
```

Then open `http://localhost:8080` in your browser.

## API Endpoints

All authentication endpoints are under `/api/auth/`:

### POST /api/auth/register
Register a new user.

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response** (201 Created):
```json
{
  "message": "User registered successfully"
}
```

### POST /api/auth/login
Authenticate and receive a JWT token.

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### GET /api/auth/profile
Get current user profile (requires authentication).

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "username": "john_doe",
  "created_at": "2024-01-01 12:00:00"
}
```

### POST /api/auth/logout
Logout and invalidate the current token.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

## Running Tests

Run the entire test suite:

```bash
pytest tests/test_auth.py -v
```

Run specific test class:

```bash
pytest tests/test_auth.py::TestLogin -v
```

Run a specific test:

```bash
pytest tests/test_auth.py::TestLogin::test_login_valid_credentials -v
```

## Security Features

1. **Password Hashing**: All passwords are hashed using bcrypt with automatic salt generation
2. **JWT Authentication**: Secure token-based authentication
3. **Token Blacklisting**: Tokens are invalidated on logout
4. **Token Expiration**: Tokens expire after 30 minutes
5. **No Plain Text Storage**: Passwords are never stored or transmitted in plain text
6. **CORS Enabled**: Configured for frontend-backend communication

## Technology Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **SQLite**: Lightweight, persistent database
- **bcrypt**: Password hashing library
- **PyJWT**: JWT token creation and validation
- **Pydantic**: Data validation using Python type annotations

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern, gradient-based UI design
- **Vanilla JavaScript**: No frameworks, pure ES6+
- **LocalStorage API**: Client-side token storage

### Testing
- **pytest**: Testing framework
- **TestClient**: FastAPI's testing client for HTTP requests
- **httpx**: Async HTTP client (required by TestClient)

## Configuration

You can configure the application by modifying these variables in `backend/main.py`:

```python
SECRET_KEY = "your-secret-key-change-in-production"  # Change for production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DB_PATH = "backend/users.db"
```

**Important**: Always use a strong, random SECRET_KEY in production. You can set it via environment variable:

```bash
export SECRET_KEY="your-very-secure-random-secret-key"
uvicorn backend.main:app --reload
```

## Usage Example

1. **Register a new account**:
   - Open the frontend in your browser
   - Fill in the registration form
   - Click "Register"

2. **Login**:
   - After registration, you'll be redirected to login
   - Enter your credentials
   - Click "Login"

3. **View Profile**:
   - After successful login, you'll see your profile
   - Shows username and account creation date

4. **Logout**:
   - Click "Logout" button
   - Your token will be invalidated
   - You'll be redirected to the login page

## Development

The project is structured for easy maintenance and extension:

- **backend/main.py**: Contains all API logic, can be split into multiple files as it grows
- **frontend/app.js**: Frontend logic separated from HTML
- **tests/test_auth.py**: Comprehensive test coverage

## Troubleshooting

**Issue**: Frontend can't connect to backend
- **Solution**: Make sure the backend is running on port 8000 and CORS is enabled

**Issue**: Tests fail with database errors
- **Solution**: Make sure no other instance is using the test database

**Issue**: Token expired errors
- **Solution**: Login again to get a new token (tokens expire after 30 minutes)

## License

This project is provided as-is for educational and development purposes.

