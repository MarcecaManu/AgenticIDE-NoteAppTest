# Authentication Module

This is a full-stack authentication module using FastAPI for the backend and plain HTML + JavaScript for the frontend.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   └── database.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   └── script.js
└── tests/
    └── test_auth.py
```

## Features

- User registration with username and password
- Secure password hashing
- JWT-based authentication
- Protected profile endpoint
- Persistent user storage using TinyDB
- Automated tests for all endpoints
- Cross-Origin Resource Sharing (CORS) support

## Setup and Running

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install backend dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```
   uvicorn app.main:app --reload
   ```
   The API will be available at http://localhost:8000

4. Open the frontend:
   - Open the `frontend/index.html` file in your browser
   - If you're using VS Code, you can use the Live Server extension

## Running Tests

To run the tests, make sure you're in the project root directory and run:
```
pytest
```

## API Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive JWT token
- `POST /api/auth/logout` - Logout (requires authentication)
- `GET /api/auth/profile` - Get user profile (requires authentication)

## Security Features

- Passwords are never stored in plain text
- Bcrypt is used for password hashing
- JWT tokens for authentication
- CORS protection
- Protected routes require valid JWT tokens

## Notes

- In a production environment, you should:
  - Use environment variables for sensitive data
  - Implement proper CORS restrictions
  - Use a more robust database
  - Add rate limiting
  - Implement token blacklisting for logout
  - Use HTTPS
