# Note Manager Application

## Project Structure
```
.
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_api.py
```

## Setup Instructions
1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the backend server:
```bash
uvicorn backend.main:app --reload
```

3. Open frontend/index.html in a web browser