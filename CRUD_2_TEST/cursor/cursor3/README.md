# Note Manager Application

A full-stack Note Manager application built with FastAPI backend and plain HTML/JavaScript frontend.

## Features

- ✅ **Full CRUD Operations**: Create, Read, Update, and Delete notes
- 🔍 **Search Functionality**: Filter notes by title in real-time
- 💾 **Persistent Storage**: Notes are stored in a SQLite database
- 🎨 **Modern UI**: Clean, responsive design with smooth animations
- 🧪 **Comprehensive Tests**: Automated pytest tests for all API endpoints
- 🚀 **REST API**: Well-structured API at `/api/notes/`

## Project Structure

```
.
├── backend/
│   ├── main.py          # FastAPI application with all CRUD endpoints
│   └── notes.db         # SQLite database (created automatically)
├── frontend/
│   ├── index.html       # Main HTML interface
│   └── app.js           # JavaScript for API calls and UI updates
├── tests/
│   └── test_api.py      # Pytest test suite for API
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone or download this project**

2. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

## Running the Application

### 1. Start the Backend Server

From the project root directory:

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`

You can view the auto-generated API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Open the Frontend

Open the `frontend/index.html` file in your web browser:

- **Option 1**: Double-click the file
- **Option 2**: Right-click and select "Open with" your preferred browser
- **Option 3**: Use a local web server (e.g., Python's http.server)

```bash
cd frontend
python -m http.server 8080
```

Then navigate to: `http://localhost:8080`

## API Endpoints

All endpoints are prefixed with `/api/notes/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/notes/` | Create a new note |
| GET | `/api/notes/` | Get all notes (supports `?search=query`) |
| GET | `/api/notes/{id}` | Get a specific note by ID |
| PUT | `/api/notes/{id}` | Update a note |
| DELETE | `/api/notes/{id}` | Delete a note |

### Note Schema

Each note has the following fields:

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content goes here",
  "createdAt": "2024-01-01T12:00:00.000000",
  "updatedAt": "2024-01-01T12:30:00.000000"
}
```

## Running Tests

The project includes comprehensive pytest tests covering all CRUD operations.

### Run all tests

```bash
pytest tests/test_api.py -v
```

### Run specific test

```bash
pytest tests/test_api.py::test_create_note -v
```

### Run with coverage

```bash
pip install pytest-cov
pytest tests/test_api.py --cov=backend --cov-report=html
```

### Test Coverage

The test suite includes:
- ✅ Create note
- ✅ Read all notes
- ✅ Read note by ID
- ✅ Update note (full and partial)
- ✅ Delete note
- ✅ Search/filter notes by title
- ✅ Error handling (404 responses)
- ✅ Validation testing

## Using the Application

### Creating a Note

1. Click the "➕ New Note" button
2. Enter a title and content
3. Click "Save Note"

### Editing a Note

1. Click the "✏️ Edit" button on any note card
2. Modify the title or content
3. Click "Update Note"

### Deleting a Note

1. Click the "🗑️ Delete" button on any note card
2. Confirm the deletion

### Searching Notes

1. Type in the search bar at the top
2. Notes will be filtered in real-time as you type

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLite**: Lightweight, file-based database for persistent storage
- **Pydantic**: Data validation using Python type hints
- **Uvicorn**: Lightning-fast ASGI server

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with flexbox/grid, animations, and gradients
- **Vanilla JavaScript**: No frameworks, just clean ES6+ JavaScript
- **Fetch API**: For making HTTP requests to the backend

### Testing
- **pytest**: Testing framework
- **TestClient**: FastAPI's built-in test client
- **httpx**: Async HTTP client for testing

## Features Highlights

### Backend Features
- ✅ RESTful API design
- ✅ Persistent SQLite database storage
- ✅ CORS middleware for frontend communication
- ✅ Request/response validation with Pydantic
- ✅ Proper HTTP status codes
- ✅ Error handling with meaningful messages
- ✅ Search functionality with SQL LIKE queries
- ✅ Automatic timestamp management

### Frontend Features
- ✅ Responsive grid layout
- ✅ Real-time search with debouncing
- ✅ Modal dialogs for create/edit
- ✅ Smooth animations and transitions
- ✅ Error message display
- ✅ Confirmation dialogs for destructive actions
- ✅ XSS protection with HTML escaping
- ✅ No page reloads (SPA-like experience)

## Database

The application uses SQLite for persistent storage. The database file (`notes.db`) is created automatically in the `backend/` directory when the server starts.

### Database Schema

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL
);
```

## Development

### Code Structure

- **backend/main.py**: Contains all FastAPI routes, database operations, and Pydantic models
- **frontend/app.js**: Handles all API interactions and DOM manipulation
- **frontend/index.html**: Contains HTML structure and embedded CSS styles
- **tests/test_api.py**: Complete test suite with fixtures for isolated testing

### Adding New Features

1. **Add new API endpoint**: Extend `backend/main.py`
2. **Update frontend**: Add corresponding UI and API calls in `frontend/`
3. **Write tests**: Add test cases in `tests/test_api.py`

## Troubleshooting

### Backend won't start
- Make sure port 8000 is not in use
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Frontend can't connect to backend
- Verify the backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Ensure the API_URL in `app.js` matches your backend URL

### Tests fail
- Make sure you're running tests from the project root
- Check that the backend directory is in the Python path
- Verify all dependencies are installed

## License

This project is provided as-is for educational and development purposes.

## Author

Built with ❤️ using FastAPI and modern web technologies.

