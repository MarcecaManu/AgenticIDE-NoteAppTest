// Configuration
const API_BASE_URL = 'http://localhost:8000/api/files';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const fileList = document.getElementById('fileList');
const refreshBtn = document.getElementById('refreshBtn');
const loading = document.getElementById('loading');
const message = document.getElementById('message');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadFiles();
});

// Event Listeners
function setupEventListeners() {
    // Upload area drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Browse button
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Refresh button
    refreshBtn.addEventListener('click', loadFiles);
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    uploadFiles(files);
}

// File Selection Handler
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    uploadFiles(files);
}

// File Upload Function
async function uploadFiles(files) {
    if (files.length === 0) return;
    
    showUploadProgress();
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const progress = ((i + 1) / files.length) * 100;
        
        try {
            await uploadSingleFile(file);
            updateProgress(progress, `Uploaded ${i + 1} of ${files.length} files`);
        } catch (error) {
            showMessage(`Failed to upload ${file.name}: ${error.message}`, 'error');
        }
    }
    
    hideUploadProgress();
    loadFiles();
    fileInput.value = ''; // Reset file input
}

// Upload Single File
async function uploadSingleFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
    }
    
    const result = await response.json();
    showMessage(`Successfully uploaded ${result.original_filename}`, 'success');
    return result;
}

// Load Files from Server
async function loadFiles() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/`);
        
        if (!response.ok) {
            throw new Error('Failed to load files');
        }
        
        const files = await response.json();
        displayFiles(files);
    } catch (error) {
        showMessage(`Failed to load files: ${error.message}`, 'error');
        displayEmptyState();
    } finally {
        hideLoading();
    }
}

// Display Files
function displayFiles(files) {
    if (files.length === 0) {
        displayEmptyState();
        return;
    }
    
    const fileListHTML = files.map(file => createFileItemHTML(file)).join('');
    fileList.innerHTML = fileListHTML;
    
    // Add event listeners to action buttons
    addFileActionListeners();
}

// Create File Item HTML
function createFileItemHTML(file) {
    const fileIcon = getFileIcon(file.mime_type);
    const fileSize = formatFileSize(file.file_size);
    const uploadDate = formatDate(file.upload_date);
    
    return `
        <div class="file-item" data-file-id="${file.id}">
            <div class="file-info">
                <div class="file-name">
                    <span class="file-type-icon">${fileIcon}</span>
                    ${escapeHtml(file.original_filename)}
                </div>
                <div class="file-details">
                    <span class="file-size">${fileSize}</span> • 
                    <span class="file-type">${file.mime_type}</span>
                </div>
                <div class="upload-date">Uploaded: ${uploadDate}</div>
            </div>
            <div class="file-actions">
                <button class="btn btn-info" onclick="showFileInfo('${file.id}')">Info</button>
                <a href="${API_BASE_URL}/${file.id}" class="btn btn-download" download>Download</a>
                <button class="btn btn-delete" onclick="deleteFile('${file.id}')">Delete</button>
            </div>
        </div>
    `;
}

// Add Event Listeners to File Action Buttons
function addFileActionListeners() {
    // Event listeners are added via onclick attributes in the HTML
    // This is for any additional listeners if needed
}

// Delete File
async function deleteFile(fileId) {
    if (!confirm('Are you sure you want to delete this file?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/${fileId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Delete failed');
        }
        
        showMessage('File deleted successfully', 'success');
        loadFiles();
    } catch (error) {
        showMessage(`Failed to delete file: ${error.message}`, 'error');
    }
}

// Show File Info
async function showFileInfo(fileId) {
    try {
        const response = await fetch(`${API_BASE_URL}/${fileId}/info`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get file info');
        }
        
        const fileInfo = await response.json();
        const fileSize = formatFileSize(fileInfo.file_size);
        const uploadDate = formatDate(fileInfo.upload_date);
        
        const infoMessage = `
            File: ${fileInfo.original_filename}
            Size: ${fileSize}
            Type: ${fileInfo.mime_type}
            Uploaded: ${uploadDate}
            ID: ${fileInfo.id}
        `;
        
        alert(infoMessage);
    } catch (error) {
        showMessage(`Failed to get file info: ${error.message}`, 'error');
    }
}

// Utility Functions
function getFileIcon(mimeType) {
    if (mimeType.startsWith('image/')) return '🖼️';
    if (mimeType === 'application/pdf') return '📄';
    if (mimeType.startsWith('text/')) return '📝';
    if (mimeType === 'application/json') return '📋';
    if (mimeType === 'application/xml') return '📋';
    return '📁';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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

// UI Helper Functions
function showUploadProgress() {
    uploadProgress.style.display = 'block';
    updateProgress(0, 'Starting upload...');
}

function hideUploadProgress() {
    setTimeout(() => {
        uploadProgress.style.display = 'none';
    }, 1000);
}

function updateProgress(percent, text) {
    progressFill.style.width = percent + '%';
    progressText.textContent = text || `${Math.round(percent)}%`;
}

function showLoading() {
    loading.style.display = 'block';
    fileList.innerHTML = '';
}

function hideLoading() {
    loading.style.display = 'none';
}

function displayEmptyState() {
    fileList.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📂</div>
            <h3>No files uploaded yet</h3>
            <p>Upload your first file using the area above</p>
        </div>
    `;
}

function showMessage(text, type = 'info') {
    message.textContent = text;
    message.className = `message ${type}`;
    message.style.display = 'block';
    
    setTimeout(() => {
        message.style.display = 'none';
    }, 5000);
}

// Error Handling for Network Issues
window.addEventListener('online', () => {
    showMessage('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    showMessage('Connection lost. Please check your internet connection.', 'error');
});
