# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and vanilla HTML/JavaScript frontend, featuring JWT-based authentication, secure password hashing, and persistent data storage.

## Features

### Backend (FastAPI)
- **POST /api/auth/register** - Register new users with username/password
- **POST /api/auth/login** - Authenticate users and return JWT tokens
- **POST /api/auth/logout** - Invalidate user sessions via token blacklisting
- **GET /api/auth/profile** - Get authenticated user profile
- Secure password hashing with bcrypt
- JWT token-based authentication
- File-based persistent storage (JSON)
- CORS enabled for frontend integration

### Frontend (HTML/JavaScript)
- User registration with password confirmation
- User login with credential validation
- Profile viewing for authenticated users
- Logout functionality
- Responsive design with modern UI
- Real-time form validation and error handling
- Token-based session management

### Testing
- Comprehensive pytest test suite
- Tests for all API endpoints
- Authentication flow testing
- Data persistence verification
- Password security validation

## Project Structure

```
├── backend/
│   ├── main.py           # FastAPI application and routes
│   ├── models.py         # Pydantic models and data structures
│   ├── database.py       # File-based database operations
│   ├── auth.py           # Authentication logic and JWT handling
│   └── requirements.txt  # Backend dependencies
├── frontend/
│   ├── index.html        # Main HTML interface
│   ├── styles.css        # Styling and responsive design
│   └── app.js            # Frontend JavaScript logic
├── tests/
│   ├── test_auth_api.py  # Comprehensive API tests
│   └── requirements.txt  # Testing dependencies
└── README.md
```

## Setup Instructions

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

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Open `index.html` in a web browser, or serve it using a simple HTTP server:
   ```bash
   # Using Python
   python -m http.server 3000
   
   # Using Node.js (if available)
   npx serve .
   ```

The frontend will be available at `http://localhost:3000` (or directly via file://)

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
  "username": "string",
  "password": "string"
}
```

### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer <jwt_token>
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer <jwt_token>
```

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Token Blacklisting**: Logout functionality via server-side token invalidation
- **CORS Protection**: Configurable cross-origin request handling
- **Input Validation**: Pydantic models ensure data integrity

## Data Storage

User data is stored in a JSON file (`users.json`) with the following structure:
```json
{
  "users": [
    {
      "id": 1,
      "username": "user1",
      "hashed_password": "$2b$12$..."
    }
  ],
  "next_id": 2
}
```

## Usage Examples

### Frontend Usage
1. Open the frontend in a web browser
2. Register a new account or login with existing credentials
3. View your profile information when authenticated
4. Logout to end your session

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

# Get Profile (replace TOKEN with actual JWT)
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer TOKEN"

# Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer TOKEN"
```

## Development Notes

- The JWT secret key should be changed in production
- Consider using environment variables for configuration
- The file-based database is suitable for development; consider PostgreSQL/MySQL for production
- CORS is currently set to allow all origins; restrict this in production
- Token expiration is set to 30 minutes; adjust as needed

## Testing Coverage

The test suite covers:
- User registration (success and duplicate username scenarios)
- User authentication (valid/invalid credentials)
- Profile retrieval (authenticated and unauthenticated)
- Logout functionality and token blacklisting
- Password hashing verification
- Data persistence validation