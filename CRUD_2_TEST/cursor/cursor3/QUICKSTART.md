# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Start the Backend

### Windows:
```bash
run_backend.bat
```

### Linux/Mac:
```bash
chmod +x run_backend.sh
./run_backend.sh
```

### Or manually:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

## Step 3: Open the Frontend

Open `frontend/index.html` in your web browser:
- Double-click the file, or
- Right-click and select "Open with" your browser

## Step 4: Use the Application

1. **Create a note**: Click "➕ New Note"
2. **Search notes**: Type in the search bar
3. **Edit a note**: Click "✏️ Edit" on any note
4. **Delete a note**: Click "🗑️ Delete" on any note

## Step 5: Run Tests (Optional)

### Windows:
```bash
run_tests.bat
```

### Linux/Mac:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Or manually:
```bash
pytest tests/test_api.py -v
```

## API Endpoints

- `POST /api/notes/` - Create a note
- `GET /api/notes/` - Get all notes (add `?search=keyword` for filtering)
- `GET /api/notes/{id}` - Get a specific note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note

## Troubleshooting

**Backend won't start:**
- Make sure port 8000 is available
- Check that dependencies are installed

**Frontend can't connect:**
- Verify backend is running on port 8000
- Check browser console for errors

**Tests fail:**
- Run from project root directory
- Ensure all dependencies are installed

