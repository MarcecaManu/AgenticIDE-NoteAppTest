# Troubleshooting Guide

## Frontend Refresh Issue

If uploaded files don't appear in the file list immediately after upload, follow these steps:

### 1. Check Backend is Running
- Ensure the backend server is running on `http://localhost:8000`
- Run: `cd backend && python main.py`
- Verify API is accessible: `http://localhost:8000/docs`

### 2. Check CORS and Network
- Open browser Developer Tools (F12)
- Go to Console tab
- Look for error messages when uploading files
- Check Network tab for failed API requests

### 3. Frontend Debugging
The frontend now includes console logging. After uploading a file:
- Open Developer Tools (F12) → Console
- You should see:
  ```
  Upload completed, refreshing file list...
  Loading files from: http://localhost:8000/api/files/
  Loaded files: [array of files]
  ```

### 4. Common Issues and Solutions

#### Issue: "Failed to load files: HTTP 404"
**Solution**: Backend not running or wrong URL
- Start backend: `cd backend && python main.py`
- Check backend is on port 8000

#### Issue: "Failed to load files: Network Error"
**Solution**: CORS or connection issue
- Ensure backend has CORS enabled (already configured)
- Check if antivirus/firewall is blocking connections

#### Issue: Files upload but list doesn't refresh
**Solution**: JavaScript error or API response issue
- Check browser console for JavaScript errors
- Verify API response format matches expected structure

#### Issue: "No filename provided" error
**Solution**: File validation issue
- Ensure files have valid extensions (.txt, .pdf, .jpg, etc.)
- Check file size is under 10MB

### 5. Manual Testing Steps

1. **Start Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

2. **Test API Directly**:
   - Open `http://localhost:8000/api/files/` in browser
   - Should return: `{"files": []}`

3. **Start Frontend**:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   - Open `http://localhost:3000`

4. **Test Upload**:
   - Create a small text file (test.txt)
   - Drag and drop onto upload area
   - Check console for debug messages
   - File should appear in list immediately

### 6. Alternative Frontend Serving

If Python HTTP server doesn't work:

**Option 1: Direct File Access**
- Open `frontend/index.html` directly in browser
- Note: May have CORS restrictions

**Option 2: Node.js Server** (if available)
```bash
cd frontend
npx serve -s . -l 3000
```

**Option 3: Live Server Extension** (VS Code)
- Install Live Server extension
- Right-click `index.html` → "Open with Live Server"

### 7. Reset System

If issues persist:

1. **Clear Browser Cache**:
   - Ctrl+Shift+Delete → Clear cache and cookies

2. **Reset Backend Data**:
   ```bash
   cd backend
   del file_metadata.json
   rmdir /s uploads
   ```

3. **Restart Both Services**:
   - Use `start_system.bat` for automated startup

### 8. Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend accessible on port 3000 (or file:// URL)
- [ ] No console errors in browser
- [ ] API endpoint `/api/files/` returns valid JSON
- [ ] File upload returns 200 status code
- [ ] Console shows "Upload completed, refreshing file list..."
- [ ] Console shows "Loaded files: [...]"

### 9. Contact Information

If issues persist after following this guide:
- Check the main README.md for additional setup instructions
- Verify all dependencies are installed correctly
- Ensure no other services are using ports 8000 or 3000
