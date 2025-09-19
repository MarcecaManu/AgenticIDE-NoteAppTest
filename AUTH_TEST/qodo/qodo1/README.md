# Full-Stack Authentication Module

A complete authentication system built with FastAPI backend and vanilla HTML/CSS/JavaScript frontend.

## Features

### Backend (FastAPI)
- **POST /api/auth/register** - Register new users with username/password validation
- **POST /api/auth/login** - Authenticate users and return JWT tokens
- **POST /api/auth/logout** - Invalidate user sessions via token blacklisting
- **GET /api/auth/profile** - Get authenticated user profile

### Security Features
- Passwords are hashed using bcrypt
- JWT tokens for stateless authentication
- Token blacklisting for secure logout
- Input validation and sanitization
- CORS support for frontend integration

### Frontend
- User registration with validation
- User login with credential verification
- Profile viewing for authenticated users
- Secure logout functionality
- Responsive design with modern UI
- Real-time form validation
- Error handling and user feedback

### Data Persistence
- File-based database using JSON storage
- Persistent user data across server restarts
- Atomic file operations for data integrity

## Project Structure

```
├── backend/
│   ├── main.py           # FastAPI application and routes
│   ├── models.py         # Pydantic models and data structures
│   ├── auth.py           # Authentication logic and JWT handling
│   ├── database.py       # File-based database operations
│   └── requirements.txt  # Backend dependencies
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── styles.css        # CSS styling
│   └── script.js         # JavaScript application logic
├── tests/
│   ├── test_auth_api.py  # Comprehensive API tests
│   └── requirements.txt  # Test dependencies
└── README.md
```

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
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Open `index.html` in a web browser or serve it using a local server:
   ```bash
   # Using Python's built-in server
   python -m http.server 3000
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
Authorization: Bearer <token>
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

## Testing Coverage

The test suite includes comprehensive coverage for:

- ✅ User registration with valid data
- ✅ Duplicate username prevention
- ✅ Input validation (username/password requirements)
- ✅ User authentication with valid credentials
- ✅ Authentication failure handling
- ✅ Profile retrieval with valid tokens
- ✅ Unauthorized access prevention
- ✅ Token-based logout functionality
- ✅ Token invalidation after logout
- ✅ Data persistence verification

## Security Considerations

- Passwords are never stored in plain text
- JWT tokens have configurable expiration times
- Token blacklisting prevents reuse of logged-out tokens
- Input validation prevents common injection attacks
- CORS is configured for secure cross-origin requests

## Usage

1. Start the backend server
2. Open the frontend in a web browser
3. Register a new account or login with existing credentials
4. View your profile when authenticated
5. Logout to end your session

The application provides a complete authentication flow with persistent data storage and comprehensive security measures.