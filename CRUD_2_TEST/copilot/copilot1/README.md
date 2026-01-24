# Note Manager Application

A full-stack Note Manager application with FastAPI backend and vanilla JavaScript frontend.

## Project Structure

```
.
├── backend/           # FastAPI backend application
│   ├── main.py       # API endpoints and business logic
│   └── notes_data.json  # Persistent storage (auto-generated)
├── frontend/         # Frontend application
│   ├── index.html    # Main HTML file
│   └── app.js        # JavaScript application logic
├── tests/            # Automated tests
│   └── test_api.py   # pytest test suite
└── requirements.txt  # Python dependencies
```

## Features

### Backend (FastAPI)
- **REST API** at `/api/notes/` with full CRUD operations
- **Persistent storage** using JSON file
- **CORS enabled** for frontend communication
- **Data validation** using Pydantic models

### Frontend (HTML + JavaScript)
- **View all notes** in a responsive grid layout
- **Create new notes** with title and content
- **Edit existing notes** inline
- **Delete notes** with confirmation
- **Search/filter notes** by title in real-time
- **Dynamic UI updates** without page reloads

### Tests (pytest)
- Comprehensive test coverage for all CRUD operations
- Tests for edge cases (not found, empty database)
- Data persistence verification

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Backend Server

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Open the Frontend

Open `frontend/index.html` in your web browser, or serve it using a simple HTTP server:

```bash
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080` in your browser.

## Running Tests

Run all tests:
```bash
pytest tests/test_api.py -v
```

Run tests with coverage:
```bash
pytest tests/test_api.py -v --cov=backend
```

## API Endpoints

- `GET /api/notes/` - Get all notes
- `GET /api/notes/{id}` - Get a specific note by ID
- `POST /api/notes/` - Create a new note
- `PUT /api/notes/{id}` - Update an existing note
- `DELETE /api/notes/{id}` - Delete a note

## Note Schema

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content goes here",
  "createdAt": "2026-01-03T10:30:00.000000",
  "updatedAt": "2026-01-03T10:30:00.000000"
}
```

## Technologies Used

- **Backend**: FastAPI, Pydantic, Python 3.8+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest, httpx
- **Storage**: JSON file-based persistence

## Development Notes

- The backend uses a JSON file (`notes_data.json`) for persistent storage
- The file is automatically created when the first note is added
- All timestamps are stored in ISO 8601 format
- The frontend includes error handling and user feedback messages
- Tests automatically clean up test data before and after each test
