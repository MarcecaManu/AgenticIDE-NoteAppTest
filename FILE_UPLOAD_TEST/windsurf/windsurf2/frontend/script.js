class FileManager {
    constructor() {
        this.apiBase = 'http://localhost:8000/api/files';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFiles();
    }

    setupEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');
        const refreshBtn = document.getElementById('refreshBtn');

        // Drag and drop events
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        uploadArea.addEventListener('click', () => fileInput.click());

        // File input events
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        // Refresh button
        refreshBtn.addEventListener('click', this.loadFiles.bind(this));
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('uploadArea').classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        this.uploadFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.uploadFiles(files);
        e.target.value = ''; // Reset input
    }

    async uploadFiles(files) {
        if (files.length === 0) return;

        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        progressContainer.style.display = 'block';
        
        let successCount = 0;
        let errorCount = 0;

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const progress = ((i + 1) / files.length) * 100;
            
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `Uploading ${i + 1} of ${files.length}: ${file.name}`;

            try {
                await this.uploadSingleFile(file);
                successCount++;
            } catch (error) {
                errorCount++;
                this.showToast('error', 'Upload Failed', `Failed to upload ${file.name}: ${error.message}`);
            }
        }

        progressContainer.style.display = 'none';
        
        if (successCount > 0) {
            this.showToast('success', 'Upload Complete', `Successfully uploaded ${successCount} file(s)`);
            this.loadFiles(); // Refresh file list
        }
        
        if (errorCount > 0) {
            this.showToast('error', 'Upload Errors', `${errorCount} file(s) failed to upload`);
        }
    }

    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.apiBase}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return await response.json();
    }

    async loadFiles() {
        const fileList = document.getElementById('fileList');
        const loading = document.getElementById('loading');
        
        try {
            if (loading) {
                loading.style.display = 'block';
            }
            
            const response = await fetch(`${this.apiBase}/`);
            if (!response.ok) {
                throw new Error('Failed to load files');
            }
            
            const data = await response.json();
            this.renderFiles(data.files);
            
        } catch (error) {
            this.showToast('error', 'Load Error', 'Failed to load files: ' + error.message);
            fileList.innerHTML = '<div class="error">Failed to load files. Please try again.</div>';
        } finally {
            if (loading) {
                loading.style.display = 'none';
            }
        }
    }

    renderFiles(files) {
        const fileList = document.getElementById('fileList');
        
        if (files.length === 0) {
            fileList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📂</div>
                    <h3>No files uploaded yet</h3>
                    <p>Start by uploading some files using the area above</p>
                </div>
            `;
            return;
        }

        // Sort files by upload date (newest first)
        files.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date));

        fileList.innerHTML = files.map(file => this.renderFileItem(file)).join('');
    }

    renderFileItem(file) {
        const uploadDate = new Date(file.upload_date).toLocaleString();
        const fileSize = this.formatFileSize(file.file_size);
        const fileIcon = this.getFileIcon(file.mime_type);

        return `
            <div class="file-item">
                <div class="file-header">
                    <div class="file-info">
                        <h3>${fileIcon} ${this.escapeHtml(file.original_filename)}</h3>
                        <div class="file-meta">
                            <div><strong>Size:</strong> ${fileSize}</div>
                            <div><strong>Type:</strong> ${file.mime_type}</div>
                            <div><strong>Uploaded:</strong> ${uploadDate}</div>
                            <div><strong>ID:</strong> ${file.id}</div>
                        </div>
                    </div>
                    <div class="file-actions">
                        <a href="${this.apiBase}/${file.id}" 
                           class="btn btn-download" 
                           download="${file.original_filename}"
                           title="Download file">
                            ⬇️ Download
                        </a>
                        <button class="btn btn-info" 
                                onclick="fileManager.showFileInfo('${file.id}')"
                                title="View file info">
                            ℹ️ Info
                        </button>
                        <button class="btn btn-delete" 
                                onclick="fileManager.deleteFile('${file.id}')"
                                title="Delete file">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    async showFileInfo(fileId) {
        try {
            const response = await fetch(`${this.apiBase}/${fileId}/info`);
            if (!response.ok) {
                throw new Error('Failed to get file info');
            }
            
            const fileInfo = await response.json();
            const uploadDate = new Date(fileInfo.upload_date).toLocaleString();
            const fileSize = this.formatFileSize(fileInfo.file_size);
            
            const message = `
                <strong>Original Name:</strong> ${this.escapeHtml(fileInfo.original_filename)}<br>
                <strong>File Size:</strong> ${fileSize}<br>
                <strong>MIME Type:</strong> ${fileInfo.mime_type}<br>
                <strong>Upload Date:</strong> ${uploadDate}<br>
                <strong>File ID:</strong> ${fileInfo.id}
            `;
            
            this.showToast('info', 'File Information', message);
            
        } catch (error) {
            this.showToast('error', 'Info Error', 'Failed to get file info: ' + error.message);
        }
    }

    async deleteFile(fileId) {
        if (!confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/${fileId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Delete failed');
            }

            this.showToast('success', 'File Deleted', 'File has been successfully deleted');
            this.loadFiles(); // Refresh file list

        } catch (error) {
            this.showToast('error', 'Delete Error', 'Failed to delete file: ' + error.message);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getFileIcon(mimeType) {
        if (mimeType.startsWith('image/')) return '🖼️';
        if (mimeType === 'application/pdf') return '📄';
        if (mimeType.startsWith('text/')) return '📝';
        if (mimeType === 'application/json') return '📋';
        if (mimeType === 'application/xml' || mimeType === 'text/xml') return '📄';
        return '📎';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showToast(type, title, message) {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        toast.innerHTML = `
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove toast after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
        
        // Remove on click
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
}

// Initialize the file manager when the page loads
let fileManager;
document.addEventListener('DOMContentLoaded', () => {
    fileManager = new FileManager();
});
