# Testing Guide - UI Refresh Functionality

## Quick Test Steps

### 1. Start the System

**Option A: Automated Startup**
```bash
# From project root
start_system.bat
```

**Option B: Manual Startup**
```bash
# Terminal 1: Start Backend
cd backend
python main.py

# Terminal 2: Start Frontend (optional)
cd frontend
python -m http.server 3000
```

### 2. Access the Frontend

- **With Server**: `http://localhost:3000`
- **Direct File**: Open `frontend/index.html` in browser

### 3. Test Upload Refresh

1. **Open browser Developer Tools** (F12) → Console tab
2. **Upload a file** (drag & drop or browse)
3. **Check console output** - should see:
   ```
   Upload completed, refreshing file list...
   Loading files from: http://localhost:8000/api/files/
   Loaded files count: 1
   Files data: [array with file info]
   ```
4. **Verify**: File appears in list automatically (no manual refresh needed)

### 4. Test Delete Refresh

1. **Click "🗑️ Delete" button** on any file
2. **Confirm deletion** in popup
3. **Check console output** - should see:
   ```
   Delete completed, refreshing file list...
   Loading files from: http://localhost:8000/api/files/
   Loaded files count: 0
   Files data: []
   ```
4. **Verify**: File disappears from list automatically

### 5. Test Manual Refresh Button

1. **Click "🔄 Refresh" button**
2. **Check console output** - should see:
   ```
   Manual refresh triggered
   Loading files from: http://localhost:8000/api/files/
   ```
3. **Verify**: Button shows "🔄 Refreshing..." then returns to "🔄 Refresh"

## Expected Behavior

### ✅ Working Correctly
- Files appear immediately after upload (within 0.5 seconds)
- Files disappear immediately after deletion (within 0.5 seconds)
- Manual refresh button works and shows visual feedback
- Console shows detailed logging of all operations
- Error messages appear if backend is not running

### ❌ Issues to Report
- Files don't appear until manual browser refresh (Ctrl+F5)
- Delete doesn't remove files from list automatically
- Console shows errors like "Failed to load files"
- Refresh button doesn't work

## Troubleshooting

### Issue: Files Don't Appear After Upload

**Check:**
1. Backend is running on port 8000
2. Console shows "Upload completed, refreshing file list..."
3. Console shows "Loaded files count: X"
4. No CORS errors in console

**Solutions:**
- Restart backend server
- Clear browser cache (Ctrl+Shift+Delete)
- Use `http://localhost:3000` instead of file:// URL

### Issue: Refresh Button Doesn't Work

**Check:**
1. Console shows "Manual refresh triggered"
2. No JavaScript errors in console
3. Backend responds to `/api/files/` endpoint

**Solutions:**
- Check browser console for errors
- Verify backend is accessible at `http://localhost:8000/api/files/`

### Issue: CORS Errors

**Symptoms:**
- Console shows "CORS policy" errors
- API calls fail with network errors

**Solutions:**
- Use `python -m http.server 3000` to serve frontend
- Don't open `index.html` directly in browser
- Ensure backend CORS is enabled (already configured)

## Debug Information

### Console Logging
The frontend now includes comprehensive logging:
- Upload operations
- Delete operations
- File list refreshes
- API call results
- Error conditions

### Network Tab
Check browser Network tab (F12) for:
- API calls to `http://localhost:8000/api/files/`
- HTTP status codes (200 = success)
- Response data

### Backend Logs
Backend terminal shows:
- Incoming requests
- File operations
- Any server errors

## Performance Notes

- **Refresh Delay**: 500ms delay added after upload/delete to ensure backend processing
- **Cache Prevention**: `cache: 'no-cache'` header prevents stale data
- **Error Recovery**: Automatic error handling and user feedback

## Success Criteria

✅ **Upload Test**: File appears in list within 1 second of upload completion
✅ **Delete Test**: File disappears from list within 1 second of deletion
✅ **Refresh Test**: Manual refresh button works and shows feedback
✅ **Error Handling**: Clear error messages when backend is unavailable
✅ **Console Logging**: Detailed debug information available
