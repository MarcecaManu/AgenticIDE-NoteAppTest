# Note Manager Application

A full-stack note management application built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- **Create Notes**: Add new notes with title and content
- **View Notes**: Display all notes in a responsive grid layout
- **Edit Notes**: Update existing notes with a modal interface
- **Delete Notes**: Remove notes with confirmation
- **Search**: Filter notes by title in real-time
- **Persistent Storage**: Notes are stored in SQLite database

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application with REST API
│   ├── requirements.txt     # Python dependencies
│   └── notes.db            # SQLite database (created automatically)
├── frontend/
│   ├── index.html          # Main HTML interface
│   └── app.js              # JavaScript for UI interactions
├── tests/
│   ├── test_api.py         # Comprehensive API tests
│   └── requirements.txt    # Test dependencies
└── README.md               # This file
```

## API Endpoints

All endpoints are under `/api/notes/`:

- `POST /api/notes/` - Create a new note
- `GET /api/notes/` - Get all notes
- `GET /api/notes/{id}` - Get a specific note by ID
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note

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

3. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Open `index.html` in a web browser, or serve it with a simple HTTP server:
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
```

3. Run the tests:
```bash
pytest test_api.py -v
```

## Usage

1. **Start the backend server** (must be running on port 8000)
2. **Open the frontend** in your web browser
3. **Create notes** using the form at the top
4. **Search notes** using the search bar
5. **Edit notes** by clicking the Edit button on any note card
6. **Delete notes** by clicking the Delete button (with confirmation)

## Technology Stack

- **Backend**: FastAPI, SQLite, Pydantic
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Testing**: pytest, httpx

## Notes

- The backend uses SQLite for persistent storage
- CORS is enabled for local development
- All timestamps are stored in UTC ISO format
- The UI is fully responsive and works on mobile devices
