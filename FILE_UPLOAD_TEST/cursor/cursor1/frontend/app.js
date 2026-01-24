const API_BASE_URL = 'http://localhost:8000/api/files';

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadProgress = document.getElementById('uploadProgress');
const errorMessage = document.getElementById('errorMessage');
const filesList = document.getElementById('filesList');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadFiles();
    setupUploadArea();
});

// Setup upload area with drag and drop
function setupUploadArea() {
    // Click to browse
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
        fileInput.value = ''; // Reset input
    });
}

// Handle file uploads
async function handleFiles(files) {
    hideError();
    
    for (const file of files) {
        await uploadFile(file);
    }
    
    loadFiles(); // Refresh list after upload
}

// Upload a single file
async function uploadFile(file) {
    showProgress(`Uploading ${file.name}...`);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Upload failed');
        }

        showProgress(`✓ ${file.name} uploaded successfully!`);
        setTimeout(hideProgress, 2000);
    } catch (error) {
        showError(error.message);
        hideProgress();
    }
}

// Load and display all files
async function loadFiles() {
    try {
        filesList.innerHTML = '<p class="loading">Loading files...</p>';
        
        const response = await fetch(`${API_BASE_URL}/`);
        
        if (!response.ok) {
            throw new Error('Failed to load files');
        }

        const files = await response.json();
        
        if (files.length === 0) {
            filesList.innerHTML = '<p class="empty-state">No files uploaded yet. Upload your first file above!</p>';
            return;
        }

        displayFiles(files);
    } catch (error) {
        filesList.innerHTML = `<p class="error-message">Error loading files: ${error.message}</p>`;
    }
}

// Display files in the list
function displayFiles(files) {
    filesList.innerHTML = files.map(file => `
        <div class="file-item" data-file-id="${file.id}">
            <div class="file-info">
                <div class="file-name">${escapeHtml(file.original_filename)}</div>
                <div class="file-meta">
                    <span>📄 ${file.mime_type}</span>
                    <span>📦 ${formatFileSize(file.file_size)}</span>
                    <span>📅 ${formatDate(file.upload_date)}</span>
                </div>
            </div>
            <div class="file-actions">
                <a href="${API_BASE_URL}/${file.id}" class="btn btn-primary" download>Download</a>
                <button class="btn btn-danger" onclick="deleteFile('${file.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Delete a file
async function deleteFile(fileId) {
    if (!confirm('Are you sure you want to delete this file?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/${fileId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Delete failed');
        }

        // Remove from UI
        const fileItem = document.querySelector(`[data-file-id="${fileId}"]`);
        if (fileItem) {
            fileItem.remove();
        }

        // Reload list to ensure consistency
        loadFiles();
    } catch (error) {
        showError(`Failed to delete file: ${error.message}`);
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
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showProgress(message) {
    uploadProgress.textContent = message;
    uploadProgress.classList.remove('hidden');
}

function hideProgress() {
    uploadProgress.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    setTimeout(hideError, 5000);
}

function hideError() {
    errorMessage.classList.add('hidden');
}

