const API_BASE_URL = 'http://localhost:8000/api/files';

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filesList = document.getElementById('filesList');
const messageDiv = document.getElementById('message');

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
        handleFiles(e.target.files);
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
        handleFiles(e.dataTransfer.files);
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
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            showMessage(error.detail || 'Upload failed', 'error');
            return;
        }

        const data = await response.json();
        showMessage(`File "${data.original_filename}" uploaded successfully!`, 'success');
    } catch (error) {
        showMessage(`Upload error: ${error.message}`, 'error');
    }
}

// Load and display files
async function loadFiles() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (!response.ok) {
            throw new Error('Failed to load files');
        }

        const data = await response.json();
        displayFiles(data.files || []);
    } catch (error) {
        filesList.innerHTML = `<div class="message error show">Error loading files: ${error.message}</div>`;
    }
}

// Display files
function displayFiles(files) {
    if (files.length === 0) {
        filesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <div>No files uploaded yet</div>
            </div>
        `;
        return;
    }

    filesList.innerHTML = files.map(file => `
        <div class="file-card">
            <div class="file-info">
                <div class="file-name">${escapeHtml(file.original_filename)}</div>
                <div class="file-meta">
                    <span>📦 ${formatFileSize(file.file_size)}</span>
                    <span>📄 ${file.mime_type}</span>
                    <span>📅 ${formatDate(file.upload_date)}</span>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn" onclick="downloadFile('${file.id}')">Download</button>
                <button class="btn btn-danger" onclick="deleteFile('${file.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Download file
async function downloadFile(fileId) {
    try {
        const response = await fetch(`${API_BASE_URL}/${fileId}`);
        if (!response.ok) {
            const error = await response.json();
            showMessage(error.detail || 'Download failed', 'error');
            return;
        }

        // Get filename from response headers or metadata
        const blob = await response.blob();
        const metadataResponse = await fetch(`${API_BASE_URL}/${fileId}/info`);
        const metadata = await metadataResponse.json();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = metadata.original_filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showMessage(`File "${metadata.original_filename}" downloaded!`, 'success');
    } catch (error) {
        showMessage(`Download error: ${error.message}`, 'error');
    }
}

// Delete file
async function deleteFile(fileId) {
    if (!confirm('Are you sure you want to delete this file?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/${fileId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            showMessage(error.detail || 'Delete failed', 'error');
            return;
        }

        showMessage('File deleted successfully!', 'success');
        loadFiles();
    } catch (error) {
        showMessage(`Delete error: ${error.message}`, 'error');
    }
}

// Utility functions
function showMessage(text, type = 'success') {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type} show`;
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 5000);
}

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

