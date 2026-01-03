# Note Manager Application

A full-stack Note Manager application with a FastAPI backend and vanilla JavaScript frontend.

## Features

- ✅ Create, read, update, and delete notes
- ✅ Persistent storage using JSON file
- ✅ Search/filter notes by title
- ✅ Real-time UI updates without page reloads
- ✅ Modern, responsive design
- ✅ Comprehensive test coverage

## Project Structure

```
cursor2/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI application with CRUD endpoints
│   └── notes.json       # Persistent storage (created automatically)
├── frontend/
│   ├── index.html       # Main HTML page
│   ├── styles.css       # Styling
│   └── app.js           # Frontend JavaScript logic
├── tests/
│   ├── __init__.py
│   └── test_api.py      # Pytest test suite
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

## Running the Application

1. **Start the FastAPI server:**

```bash
uvicorn backend.main:app --reload
```

2. **Open your browser and navigate to:**

```
http://localhost:8000
```

The application will be running and ready to use!

## API Endpoints

All endpoints are prefixed with `/api/notes/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notes/` | Get all notes |
| GET | `/api/notes/{id}` | Get a specific note by ID |
| POST | `/api/notes/` | Create a new note |
| PUT | `/api/notes/{id}` | Update an existing note |
| DELETE | `/api/notes/{id}` | Delete a note |

### Note Schema

```json
{
  "id": "string (UUID)",
  "title": "string",
  "content": "string",
  "createdAt": "string (ISO 8601 datetime)",
  "updatedAt": "string (ISO 8601 datetime)"
}
```

## Running Tests

Run the test suite using pytest:

```bash
pytest tests/ -v
```

### Test Coverage

The test suite includes 11 comprehensive tests covering:

- ✅ Create note
- ✅ Get all notes
- ✅ Get note by ID (success and 404 cases)
- ✅ Update note (full and partial updates, with 404 cases)
- ✅ Delete note (success and 404 cases)
- ✅ Data persistence verification

## Usage

### Creating a Note

1. Click the "+ New Note" button
2. Enter a title and content
3. Click "Save Note"

### Editing a Note

1. Click the "Edit" button on any note card
2. Modify the title and/or content
3. Click "Save Note"

### Deleting a Note

1. Click the "Delete" button on any note card
2. Confirm the deletion in the popup dialog

### Searching Notes

1. Type in the search bar at the top
2. Notes will be filtered by title in real-time

## Technologies Used

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server for running FastAPI

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with modern animations and responsive design
- **Vanilla JavaScript** - Interactive functionality with Fetch API

### Testing
- **pytest** - Testing framework
- **httpx** - HTTP client for testing FastAPI endpoints

## Data Persistence

Notes are stored in `backend/notes.json` file. The file is created automatically on the first note creation. All CRUD operations update this file immediately, ensuring data persistence across server restarts.

## Development

### Adding New Features

1. Update the backend API endpoints in `backend/main.py`
2. Modify the frontend UI in `frontend/index.html` and `frontend/styles.css`
3. Update the JavaScript logic in `frontend/app.js`
4. Add corresponding tests in `tests/test_api.py`

### Code Quality

- Backend follows RESTful API design principles
- Frontend uses async/await for all API calls
- Comprehensive error handling throughout the application
- Modular and maintainable code structure

## License

This project is open source and available for educational purposes.

