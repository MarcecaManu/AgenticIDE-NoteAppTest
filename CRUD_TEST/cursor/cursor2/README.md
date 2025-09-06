# Note Manager Application

A full-stack note management application built with FastAPI and vanilla JavaScript.

## Features

- Create, read, update, and delete notes
- Persistent storage using TinyDB
- Real-time search functionality
- Modern and responsive UI
- Full test coverage for the backend API

## Project Structure

```
.
├── backend/
│   ├── main.py         # FastAPI application
│   ├── models.py       # Data models
│   ├── database.py     # Database operations
│   └── requirements.txt
├── frontend/
│   ├── index.html      # Frontend UI
│   └── app.js          # Frontend logic
└── tests/
    └── test_api.py     # API tests
```

## Prerequisites

- Python 3.8 or higher
- A modern web browser

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd note-manager
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```
The API will be available at http://localhost:8000

2. Open the frontend:
- Navigate to the `frontend` directory
- Open `index.html` in your web browser
- Or serve it using a local HTTP server:
  ```bash
  python -m http.server 8080
  ```
  Then visit http://localhost:8080

## Running Tests

To run the automated tests:
```bash
# Make sure you're in the project root directory
python -m pytest tests/
```

Note: If you encounter import errors, you may need to add the project root to PYTHONPATH:
```bash
# On Windows
set PYTHONPATH=%PYTHONPATH%;.

# On Unix/Linux/MacOS
export PYTHONPATH=$PYTHONPATH:.
```

## API Endpoints

- `GET /api/notes/` - Get all notes
- `GET /api/notes/{id}` - Get a specific note
- `POST /api/notes/` - Create a new note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note

## Frontend Features

- Responsive grid layout for notes
- Real-time search filtering
- Edit and delete functionality
- Clean and modern UI
- No page reloads required

## Technologies Used

- Backend:
  - FastAPI
  - TinyDB
  - Python
  - pytest

- Frontend:
  - HTML5
  - CSS3
  - Vanilla JavaScript
  - Fetch API 