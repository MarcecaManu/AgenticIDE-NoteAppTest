# Note Manager Application

A full-stack Note Manager application built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- **Create Notes**: Add new notes with title and content
- **Read Notes**: View all notes or get a specific note by ID
- **Update Notes**: Edit existing notes
- **Delete Notes**: Remove notes you no longer need
- **Search**: Filter notes by title using the search bar
- **Persistent Storage**: Notes are stored in SQLite database

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── notes.db            # SQLite database (created automatically)
├── frontend/
│   ├── index.html          # Main HTML page
│   ├── styles.css          # CSS styles
│   └── app.js              # JavaScript application logic
└── tests/
    ├── test_api.py         # Pytest test suite
    └── requirements.txt    # Test dependencies
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
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Open `index.html` in your web browser, or serve it using a simple HTTP server:
```bash
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

### Running Tests

1. Navigate to the tests directory:
```bash
cd tests
```

2. Install test dependencies:
```bash
pip install -r requirements.txt
pip install -r ../backend/requirements.txt
```

3. Run the tests:
```bash
pytest test_api.py -v
```

## API Endpoints

### Base URL: `/api/notes/`

- **POST /api/notes/** - Create a new note
  - Request body: `{"title": "string", "content": "string"}`
  - Response: 201 Created with note object

- **GET /api/notes/** - Get all notes
  - Response: 200 OK with array of notes

- **GET /api/notes/{id}** - Get a specific note
  - Response: 200 OK with note object or 404 Not Found

- **PUT /api/notes/{id}** - Update a note
  - Request body: `{"title": "string", "content": "string"}` (both optional)
  - Response: 200 OK with updated note or 404 Not Found

- **DELETE /api/notes/{id}** - Delete a note
  - Response: 204 No Content or 404 Not Found

## Note Schema

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content",
  "createdAt": "2024-01-01T12:00:00Z",
  "updatedAt": "2024-01-01T12:00:00Z"
}
```

## Technologies Used

- **Backend**: FastAPI, SQLite, Pydantic
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Testing**: Pytest, FastAPI TestClient
