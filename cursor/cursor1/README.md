# Note Manager Application

A full-stack note management application built with FastAPI and vanilla JavaScript.

## Features

- Create, read, update, and delete notes
- Search notes by title
- Responsive design
- Persistent storage using TinyDB
- RESTful API
- Automated tests

## Project Structure

```
.
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   └── js/
│       └── app.js
└── tests/
    └── test_api.py
```

## Prerequisites

- Python 3.8 or higher
- A modern web browser

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd note-manager
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r backend/requirements.txt
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```
The API will be available at http://localhost:8000

2. Open the frontend:
- Navigate to the `frontend` directory
- Open `index.html` in your web browser
- Or serve it using a local HTTP server:
  ```bash
  python -m http.server
  ```
  Then visit http://localhost:8000

## Running Tests

To run the automated tests:
```bash
pytest tests/
```

## API Endpoints

- `GET /api/notes/` - Get all notes
- `GET /api/notes/?search={term}` - Search notes by title
- `GET /api/notes/{id}` - Get a specific note
- `POST /api/notes/` - Create a new note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note

## Note Structure

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note Content",
  "created_at": "2024-01-01T12:00:00.000Z",
  "updated_at": "2024-01-01T12:00:00.000Z"
}
``` 