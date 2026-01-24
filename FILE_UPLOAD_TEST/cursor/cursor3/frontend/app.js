const API_BASE_URL = 'http://localhost:8000/api/files';

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filesList = document.getElementById('filesList');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
    setupUploadHandlers();
});

// Setup upload handlers
function setupUploadHandlers() {
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
    if (files.length === 0) return;

    for (const file of files) {
        await uploadFile(file);
    }
}

// Upload a single file
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Upload failed');
        }

        showSuccess(`File "${data.original_filename}" uploaded successfully!`);
        loadFiles();
    } catch (error) {
        showError(error.message || 'Failed to upload file');
    } finally {
        hideLoading();
    }
}

// Load all files
async function loadFiles() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error('Failed to load files');
        }

        displayFiles(data.files || []);
    } catch (error) {
        showError('Failed to load files: ' + error.message);
        filesList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><div>Failed to load files</div></div>';
    } finally {
        hideLoading();
    }
}

// Display files in the list
function displayFiles(files) {
    if (files.length === 0) {
        filesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📂</div>
                <div>No files uploaded yet</div>
            </div>
        `;
        return;
    }

    filesList.innerHTML = files.map(file => `
        <div class="file-item" data-file-id="${file.id}">
            <div class="file-info">
                <div class="file-name">${escapeHtml(file.original_filename)}</div>
                <div class="file-meta">
                    <span>📊 ${formatFileSize(file.file_size)}</span>
                    <span>📄 ${file.mime_type}</span>
                    <span>📅 ${formatDate(file.upload_date)}</span>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-info" onclick="showFileInfo('${file.id}')">Info</button>
                <button class="btn btn-download" onclick="downloadFile('${file.id}')">Download</button>
                <button class="btn btn-delete" onclick="deleteFile('${file.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Download file
async function downloadFile(fileId) {
    try {
        const response = await fetch(`${API_BASE_URL}/${fileId}`);
        if (!response.ok) {
            throw new Error('Failed to download file');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Get filename from response headers or use file ID
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `file_${fileId}`;
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

        showSuccess('File downloaded successfully!');
    } catch (error) {
        showError('Failed to download file: ' + error.message);
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
            throw new Error('Failed to delete file');
        }

        showSuccess('File deleted successfully!');
        loadFiles();
    } catch (error) {
        showError('Failed to delete file: ' + error.message);
    }
}

// Show file info
async function showFileInfo(fileId) {
    try {
        const response = await fetch(`${API_BASE_URL}/${fileId}/info`);
        if (!response.ok) {
            throw new Error('Failed to get file info');
        }

        const fileInfo = await response.json();
        const infoText = `
File ID: ${fileInfo.id}
Original Filename: ${fileInfo.original_filename}
Stored Filename: ${fileInfo.stored_filename}
File Size: ${formatFileSize(fileInfo.file_size)}
MIME Type: ${fileInfo.mime_type}
Upload Date: ${formatDate(fileInfo.upload_date)}
        `.trim();

        alert(infoText);
    } catch (error) {
        showError('Failed to get file info: ' + error.message);
    }
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

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(() => {
        errorMessage.classList.remove('show');
    }, 5000);
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.classList.add('show');
    setTimeout(() => {
        successMessage.classList.remove('show');
    }, 3000);
}

function showLoading() {
    if (filesList.querySelector('.loading')) return;
    filesList.innerHTML = '<div class="loading">Loading...</div>';
}

function hideLoading() {
    // Loading is replaced by displayFiles, so no action needed
}

