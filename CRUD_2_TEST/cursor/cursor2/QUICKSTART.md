# Quick Start Guide

Get your Note Manager up and running in 3 simple steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Start the Server

### Windows:
```bash
start.bat
```

### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

Or manually:
```bash
uvicorn backend.main:app --reload
```

## Step 3: Open Your Browser

Navigate to: **http://localhost:8000**

That's it! Your Note Manager is ready to use! 🎉

---

## Running Tests

To verify everything works correctly:

```bash
pytest tests/ -v
```

Expected output: **11 tests passed** ✅

---

## API Testing

You can also test the API directly:

### Create a Note
```bash
curl -X POST "http://localhost:8000/api/notes/" \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Note","content":"Hello World!"}'
```

### Get All Notes
```bash
curl "http://localhost:8000/api/notes/"
```

### Get Note by ID
```bash
curl "http://localhost:8000/api/notes/{note_id}"
```

### Update a Note
```bash
curl -X PUT "http://localhost:8000/api/notes/{note_id}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title","content":"Updated content"}'
```

### Delete a Note
```bash
curl -X DELETE "http://localhost:8000/api/notes/{note_id}"
```

---

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, start the server on a different port:
```bash
uvicorn backend.main:app --reload --port 8001
```

### Module Not Found Error
Make sure you're running commands from the project root directory and have installed all dependencies.

### Tests Failing
Ensure the backend server is not running when executing tests to avoid conflicts with the storage file.

---

## Need Help?

Check out the full [README.md](README.md) for detailed documentation.

