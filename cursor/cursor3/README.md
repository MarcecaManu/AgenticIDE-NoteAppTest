# Note Manager Application

A full-stack note management application built with FastAPI and vanilla JavaScript.

## Features

- Create, read, update, and delete notes
- Search notes by title
- Persistent storage using TinyDB
- Modern and responsive UI
- Real-time updates without page reloads
- Full test coverage for the backend API

## Project Structure

```
.
├── backend/
│   ├── main.py         # FastAPI application
│   ├── models.py       # Pydantic models
│   ├── database.py     # Database operations
│   └── requirements.txt
├── frontend/
│   ├── index.html      # Frontend UI
│   └── script.js       # Frontend logic
└── tests/
    └── test_api.py     # API tests
```

## Setup

1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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
   - Simply open `frontend/index.html` in your web browser
   - Or serve it using a local HTTP server:
     ```bash
     cd frontend
     python -m http.server
     ```
     Then visit http://localhost:8000

## Running Tests

To run the backend API tests:
```bash
cd tests
pytest test_api.py -v
```

## API Endpoints

- `GET /api/notes/` - Get all notes
- `GET /api/notes/{id}` - Get a specific note
- `POST /api/notes/` - Create a new note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note

## Technologies Used

- Backend:
  - FastAPI
  - TinyDB
  - Pydantic
  - pytest

- Frontend:
  - HTML5
  - CSS3
  - Vanilla JavaScript
  - Fetch API 