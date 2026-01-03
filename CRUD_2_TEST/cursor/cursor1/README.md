# Note Manager Application

A full-stack note management application with FastAPI backend and vanilla JavaScript frontend.

## Features

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Persistent storage using SQLite database
- ✅ Real-time search/filter by title
- ✅ Modern, responsive UI
- ✅ RESTful API design
- ✅ Comprehensive automated tests

## Project Structure

```
.
├── backend/
│   ├── main.py           # FastAPI application and API endpoints
│   ├── models.py         # Pydantic data models
│   ├── database.py       # Database connection and initialization
│   ├── crud.py           # CRUD operations
│   └── notes.db          # SQLite database (created on first run)
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── styles.css        # CSS styling
│   └── app.js            # JavaScript logic
├── tests/
│   └── test_api.py       # Pytest test suite
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

1. **Clone or download the project**

2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Backend Server

From the project root directory, run:

```bash
# On Windows PowerShell
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# On Linux/Mac
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Frontend**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Quick Start

If you want to test the application:

1. **Start the server** (in one terminal):
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Run the tests** (in another terminal):
   ```bash
   pytest tests/test_api.py -v
   ```

3. **Open the web interface**:
   Navigate to http://localhost:8000/ in your browser

## API Endpoints

All endpoints are prefixed with `/api/notes/`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notes/` | Get all notes |
| GET | `/api/notes/{id}` | Get a specific note |
| POST | `/api/notes/` | Create a new note |
| PUT | `/api/notes/{id}` | Update a note |
| DELETE | `/api/notes/{id}` | Delete a note |

### Note Schema

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content",
  "createdAt": "2024-01-01T12:00:00",
  "updatedAt": "2024-01-01T12:00:00"
}
```

## Running Tests

Run the automated test suite:

```bash
pytest tests/test_api.py -v
```

This will run 10+ tests covering:
- Creating notes
- Reading all notes
- Reading notes by ID
- Updating notes
- Deleting notes
- Error handling (404 responses)
- Data persistence

## Frontend Features

The web interface provides:

1. **View Notes**: Display all notes in a card layout
2. **Create Note**: Form to add new notes
3. **Edit Note**: Click "Edit" to modify existing notes
4. **Delete Note**: Remove notes with confirmation
5. **Search**: Real-time filtering by title

## Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- Pydantic - Data validation
- SQLite - Lightweight database
- Uvicorn - ASGI server

**Frontend:**
- HTML5
- CSS3 (Modern responsive design)
- Vanilla JavaScript (ES6+)

**Testing:**
- Pytest - Testing framework
- FastAPI TestClient - API testing

## Database

Notes are stored persistently in a SQLite database (`backend/notes.db`). The database is automatically created on first run with the following schema:

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development

The application uses:
- CORS middleware for cross-origin requests
- Automatic API documentation (Swagger UI)
- Context managers for database connections
- Proper HTTP status codes
- Error handling and validation

## License

MIT License - Feel free to use this project for learning or production.

