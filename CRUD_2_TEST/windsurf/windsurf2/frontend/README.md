# Frontend - Note Manager UI

Modern, responsive web interface for the Note Manager application.

## Features

- Clean, modern UI with gradient design
- Responsive grid layout for notes
- Real-time search filtering
- Modal-based note editing
- Drag-and-drop friendly interface
- Success/error message notifications

## Running

Simply open `index.html` in a web browser, or serve with a local server:

```bash
python -m http.server 8080
```

Then navigate to `http://localhost:8080`

## Configuration

The API base URL is configured in `app.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/notes';
```

Make sure the backend is running on port 8000 before using the frontend.

## Browser Compatibility

Works with all modern browsers that support:
- ES6+ JavaScript
- CSS Grid
- Fetch API
- Async/Await
