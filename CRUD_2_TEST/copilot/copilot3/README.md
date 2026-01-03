# Note Manager Application

A full-stack Note Manager application with FastAPI backend and plain HTML/JavaScript frontend.

## Features

- **Full CRUD Operations**: Create, Read, Update, and Delete notes
- **Persistent Storage**: Notes are stored in SQLite database
- **Search Functionality**: Filter notes by title in real-time
- **Modern UI**: Clean and responsive user interface
- **RESTful API**: Well-structured API at `/api/notes/`
- **Automated Tests**: Comprehensive test suite using pytest

## Project Structure

```
.
├── backend/
│   ├── main.py          # FastAPI application and API endpoints
│   └── database.py      # Database models and operations
├── frontend/
│   └── index.html       # Frontend UI with HTML, CSS, and JavaScript
├── tests/
│   └── test_api.py      # Pytest test suite for API endpoints
└── requirements.txt     # Python dependencies
```

## Installation

1. **Install Dependencies**

```powershell
pip install -r requirements.txt
```

## Running the Application

### 1. Start the Backend Server

From the project root directory:

```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 2. Open the Frontend

Open `frontend/index.html` in your web browser, or serve it using Python:

```powershell
cd frontend
python -m http.server 3000
```

Then navigate to `http://localhost:3000` in your browser.

## API Endpoints

All endpoints are prefixed with `/api/notes/`

- **GET /api/notes/** - Get all notes
- **GET /api/notes/{id}** - Get a specific note by ID
- **POST /api/notes/** - Create a new note
- **PUT /api/notes/{id}** - Update an existing note
- **DELETE /api/notes/{id}** - Delete a note

### Request/Response Examples

**Create a Note (POST /api/notes/)**
```json
Request:
{
  "title": "My Note",
  "content": "Note content here"
}

Response (201):
{
  "id": 1,
  "title": "My Note",
  "content": "Note content here",
  "createdAt": "2026-01-03T10:30:00",
  "updatedAt": "2026-01-03T10:30:00"
}
```

**Update a Note (PUT /api/notes/1)**
```json
Request:
{
  "title": "Updated Title",
  "content": "Updated content"
}

Response (200):
{
  "id": 1,
  "title": "Updated Title",
  "content": "Updated content",
  "createdAt": "2026-01-03T10:30:00",
  "updatedAt": "2026-01-03T11:00:00"
}
```

## Running Tests

Run the test suite from the project root:

```powershell
pytest tests/ -v
```

Run with coverage report:

```powershell
pytest tests/ -v --cov=backend
```

### Test Coverage

The test suite includes:
- ✅ Create note test
- ✅ Read all notes test
- ✅ Read note by ID test
- ✅ Update note test
- ✅ Delete note test
- ✅ Error handling tests (404 cases)
- ✅ Validation tests
- ✅ Complete CRUD workflow test

## Database

Notes are stored in `notes.db` (SQLite) in the backend directory. The database is created automatically on first run.

### Note Schema

- `id` (INTEGER): Auto-incrementing primary key
- `title` (TEXT): Note title
- `content` (TEXT): Note content
- `createdAt` (TEXT): ISO format timestamp of creation
- `updatedAt` (TEXT): ISO format timestamp of last update

## Frontend Features

- **View Notes**: All notes displayed in a grid layout
- **Create Note**: Click "New Note" button to open creation modal
- **Edit Note**: Click "Edit" button on any note card
- **Delete Note**: Click "Delete" button with confirmation prompt
- **Search**: Real-time filtering of notes by title
- **Responsive Design**: Works on desktop and mobile devices
- **No Page Reloads**: All operations use JavaScript fetch API

## Technologies Used

- **Backend**: FastAPI, Python 3.8+, SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest, httpx
- **Server**: Uvicorn ASGI server

## Development

The backend uses FastAPI with automatic API documentation. Visit `/docs` for interactive API documentation (Swagger UI) or `/redoc` for alternative documentation.

CORS is enabled to allow frontend access from any origin during development.

## Notes

- The SQLite database file (`notes.db`) is created in the `backend/` directory
- Test database (`test_notes.db`) is automatically created and cleaned up during tests
- All timestamps are in UTC ISO 8601 format
- The frontend assumes the backend is running on `http://localhost:8000`
