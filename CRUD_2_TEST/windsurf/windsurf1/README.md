# Note Manager Application

A full-stack Note Manager application with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- **Full CRUD Operations**: Create, Read, Update, and Delete notes
- **Persistent Storage**: SQLite database for data persistence
- **Search Functionality**: Filter notes by title in real-time
- **Modern UI**: Clean, responsive design with smooth animations
- **RESTful API**: Well-structured API at `/api/notes/`
- **Comprehensive Tests**: Pytest test suite covering all endpoints

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Backend dependencies
│   └── notes.db            # SQLite database (created on first run)
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # Styling
│   └── app.js              # JavaScript logic
├── tests/
│   ├── test_notes_api.py   # API tests
│   └── requirements.txt    # Test dependencies
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
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Open `index.html` in a web browser, or serve it using a simple HTTP server:
   ```bash
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
   pytest test_notes_api.py -v
   ```

## API Endpoints

### Create Note
- **POST** `/api/notes/`
- Body: `{"title": "string", "content": "string"}`
- Response: `201 Created` with note object

### Get All Notes
- **GET** `/api/notes/`
- Response: `200 OK` with array of notes

### Get Note by ID
- **GET** `/api/notes/{note_id}`
- Response: `200 OK` with note object or `404 Not Found`

### Update Note
- **PUT** `/api/notes/{note_id}`
- Body: `{"title": "string", "content": "string"}` (both optional)
- Response: `200 OK` with updated note or `404 Not Found`

### Delete Note
- **DELETE** `/api/notes/{note_id}`
- Response: `204 No Content` or `404 Not Found`

## Note Schema

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content",
  "createdAt": "2026-01-24T10:47:00.000000+00:00",
  "updatedAt": "2026-01-24T10:47:00.000000+00:00"
}
```

## Technologies Used

- **Backend**: FastAPI, SQLite, Pydantic
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Testing**: Pytest, HTTPX
- **CORS**: Enabled for cross-origin requests

## Features in Detail

### Backend
- RESTful API design with proper HTTP status codes
- SQLite database for persistent storage
- Automatic database initialization
- Input validation using Pydantic models
- CORS middleware for frontend communication
- Proper error handling with meaningful messages

### Frontend
- Real-time search/filter functionality
- Modal-based note creation and editing
- Responsive card-based layout
- Toast notifications for user feedback
- No page reloads (SPA-like experience)
- Modern gradient design with smooth animations

### Testing
- 12 comprehensive test cases
- Tests for all CRUD operations
- Edge case testing (not found, empty fields)
- Database persistence verification
- Isolated test environment with automatic cleanup
