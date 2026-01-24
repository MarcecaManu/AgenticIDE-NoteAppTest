const API_BASE = 'http://localhost:8000/api/files';

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filesList = document.getElementById('filesList');
const messageArea = document.getElementById('messageArea');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
    setupUploadArea();
});

// Setup upload area
function setupUploadArea() {
    // Click to browse
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(Array.from(e.target.files));
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });
}

// Handle file uploads
async function handleFiles(files) {
    for (const file of files) {
        await uploadFile(file);
    }
    loadFiles();
}

// Upload a single file
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        showMessage('Uploading ' + file.name + '...', 'info');
        
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const result = await response.json();
        showMessage(`File "${result.original_filename}" uploaded successfully!`, 'success');
    } catch (error) {
        showMessage(`Error uploading ${file.name}: ${error.message}`, 'error');
    }
}

// Load and display files
async function loadFiles() {
    try {
        const response = await fetch(`${API_BASE}/`);
        if (!response.ok) {
            throw new Error('Failed to load files');
        }

        const data = await response.json();
        displayFiles(data.files || []);
    } catch (error) {
        showMessage('Error loading files: ' + error.message, 'error');
        filesList.innerHTML = '<div class="empty-state">Error loading files</div>';
    }
}

// Display files in the list
function displayFiles(files) {
    if (files.length === 0) {
        filesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📂</div>
                <p>No files uploaded yet</p>
                <p style="margin-top: 10px; font-size: 0.9em;">Upload your first file above!</p>
            </div>
        `;
        return;
    }

    filesList.innerHTML = files.map(file => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-name">${escapeHtml(file.original_filename)}</div>
                <div class="file-meta">
                    ${formatFileSize(file.file_size)} • ${file.mime_type} • ${formatDate(file.upload_date)}
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-secondary" onclick="downloadFile('${file.id}')">
                    ⬇️ Download
                </button>
                <button class="btn btn-danger" onclick="deleteFile('${file.id}', '${escapeHtml(file.original_filename)}')">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
}

// Download file
async function downloadFile(fileId) {
    try {
        const response = await fetch(`${API_BASE}/${fileId}`);
        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Get filename from response headers or use fileId
        const contentDisposition = response.headers.get('content-disposition');
        let filename = fileId;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+?)"?$/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showMessage('File downloaded successfully!', 'success');
    } catch (error) {
        showMessage('Error downloading file: ' + error.message, 'error');
    }
}

// Delete file
async function deleteFile(fileId, filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/${fileId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Delete failed');
        }

        showMessage(`File "${filename}" deleted successfully!`, 'success');
        loadFiles();
    } catch (error) {
        showMessage('Error deleting file: ' + error.message, 'error');
    }
}

// Show message
function showMessage(message, type) {
    const messageClass = type === 'error' ? 'error-message' : 
                        type === 'success' ? 'success-message' : 'error-message';
    
    messageArea.innerHTML = `<div class="${messageClass}">${escapeHtml(message)}</div>`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageArea.innerHTML = '';
    }, 5000);
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


