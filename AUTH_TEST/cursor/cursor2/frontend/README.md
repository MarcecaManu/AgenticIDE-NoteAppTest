# Frontend - Authentication Module

Simple, modern authentication UI built with vanilla HTML, CSS, and JavaScript.

## Running the Frontend

1. Start a local web server in this directory:

```bash
# Using Python 3
python -m http.server 8080

# Or using Node.js http-server
npx http-server -p 8080
```

2. Open your browser to `http://localhost:8080`

3. Make sure the backend is running at `http://localhost:8000` (or update `API_BASE_URL` in `app.js`)

## Features

- Registration form with validation
- Login form
- Authenticated profile view
- Logout functionality
- Responsive design
- Real-time error/success messages
- Token persistence in localStorage

