# Note Manager Application

A full-stack note management application with FastAPI backend and HTML/JavaScript frontend.

## Project Structure
- `backend/`: FastAPI backend implementation
- `frontend/`: HTML and JavaScript frontend
- `tests/`: API tests using pytest

## Setup and Running

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

3. Open `frontend/index.html` in your browser to use the application.

## Features
- Create, read, update, and delete notes
- Search notes by title
- Persistent storage using SQLite database
- Real-time UI updates without page reloads
