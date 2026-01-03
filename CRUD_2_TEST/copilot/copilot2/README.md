# Note Manager Application

A full-stack Note Manager application built with FastAPI (backend) and vanilla HTML/JavaScript (frontend).

## Features

- ✅ Create, Read, Update, and Delete notes
- ✅ Search/filter notes by title
- ✅ Persistent storage using JSON file
- ✅ Real-time UI updates without page reloads
- ✅ Comprehensive test coverage with pytest

## Project Structure

```
copilot2/
├── backend/
│   ├── main.py          # FastAPI application with REST API
│   └── notes.json       # Persistent data storage (auto-generated)
├── frontend/
│   └── index.html       # Single-page application UI
├── tests/
│   └── test_api.py      # Automated API tests
└── requirements.txt     # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at http://localhost:8000

2. Open the frontend:
   - Open `frontend/index.html` in your web browser
   - Or use a local server:
     ```bash
     cd frontend
     python -m http.server 8080
     ```
   - Then navigate to http://localhost:8080

### Running Tests

Run all tests:
```bash
pytest tests/test_api.py -v
```

Run specific test:
```bash
pytest tests/test_api.py::test_create_note -v
```

## API Endpoints

All endpoints are prefixed with `/api/notes`

- `GET /api/notes/` - Get all notes
- `GET /api/notes/{id}` - Get a specific note by ID
- `POST /api/notes/` - Create a new note
- `PUT /api/notes/{id}` - Update an existing note
- `DELETE /api/notes/{id}` - Delete a note

### Note Schema

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content here",
  "createdAt": "2026-01-03T12:00:00Z",
  "updatedAt": "2026-01-03T12:00:00Z"
}
```

## Usage

### Creating a Note
1. Click the "New Note" button
2. Fill in the title and content
3. Click "Save Note"

### Editing a Note
1. Click the "Edit" button on any note card
2. Modify the title or content
3. Click "Save Note"

### Deleting a Note
1. Click the "Delete" button on any note card
2. Confirm the deletion

### Searching Notes
- Type in the search bar to filter notes by title in real-time

## Technologies Used

- **Backend**: FastAPI, Python, Pydantic
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest, FastAPI TestClient
- **Data Storage**: JSON file

## Notes

- The backend automatically creates a `notes.json` file in the backend directory for persistent storage
- The frontend requires CORS to be enabled on the backend (already configured)
- All timestamps are in UTC ISO format
