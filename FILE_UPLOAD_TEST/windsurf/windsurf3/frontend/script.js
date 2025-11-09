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

        // File input events
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        browseBtn.addEventListener('click', () => fileInput.click());

        // Refresh button
        refreshBtn.addEventListener('click', async () => {
            console.log('Manual refresh triggered');
            refreshBtn.disabled = true;
            refreshBtn.textContent = '🔄 Refreshing...';
            await this.loadFiles();
            refreshBtn.disabled = false;
            refreshBtn.textContent = '🔄 Refresh';
        });

        // Upload area click
        uploadArea.addEventListener('click', (e) => {
            if (e.target === uploadArea || e.target.closest('.upload-content')) {
                fileInput.click();
            }
        });
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

        const progressContainer = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        progressContainer.style.display = 'block';

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const progress = ((i + 1) / files.length) * 100;

            progressFill.style.width = `${progress}%`;
            progressText.textContent = `Uploading ${file.name} (${i + 1}/${files.length})`;

            try {
                await this.uploadSingleFile(file);
                this.showMessage(`Successfully uploaded ${file.name}`, 'success');
            } catch (error) {
                this.showMessage(`Failed to upload ${file.name}: ${error.message}`, 'error');
            }
        }

        progressContainer.style.display = 'none';
        console.log('Upload completed, refreshing file list...');
        // Add a small delay to ensure backend has processed the upload
        setTimeout(async () => {
            await this.loadFiles();
        }, 500);
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
        const loadingIndicator = document.getElementById('loadingIndicator');

        // Show loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }

        try {
            console.log('Loading files from:', `${this.apiBase}/`);
            const response = await fetch(`${this.apiBase}/`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                cache: 'no-cache' // Prevent caching issues
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Failed to load files`);
            }

            const data = await response.json();
            console.log('Loaded files count:', data.files ? data.files.length : 0);
            console.log('Files data:', data.files);
            
            this.renderFileList(data.files || []);
            
            // Show success message for manual refresh
            if (loadingIndicator && loadingIndicator.style.display === 'block') {
                console.log('File list refreshed successfully');
            }
        } catch (error) {
            console.error('Error loading files:', error);
            this.showMessage(`Failed to load files: ${error.message}. Make sure the backend is running on ${this.apiBase}`, 'error');
            if (fileList) {
                fileList.innerHTML = '<div class="empty-state"><div class="empty-icon">❌</div><p>Failed to load files. Check console for details.</p></div>';
            }
        } finally {
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        }
    }

    renderFileList(files) {
        const fileList = document.getElementById('fileList');

        if (files.length === 0) {
            fileList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📁</div>
                    <p>No files uploaded yet</p>
                    <small>Upload some files to get started</small>
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
            <div class="file-item" data-file-id="${file.id}">
                <div class="file-info">
                    <div class="file-name">
                        <span class="file-icon">${fileIcon}</span>
                        ${this.escapeHtml(file.original_filename)}
                    </div>
                    <div class="file-meta">
                        <span>📏 ${fileSize}</span>
                        <span>📅 ${uploadDate}</span>
                        <span>🏷️ ${file.mime_type}</span>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-info" onclick="fileManager.showFileInfo('${file.id}')">
                        ℹ️ Info
                    </button>
                    <a href="${this.apiBase}/${file.id}" class="btn btn-download" download>
                        ⬇️ Download
                    </a>
                    <button class="btn btn-delete" onclick="fileManager.deleteFile('${file.id}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `;
    }

    async deleteFile(fileId) {
        if (!confirm('Are you sure you want to delete this file?')) {
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

            this.showMessage('File deleted successfully', 'success');
            console.log('Delete completed, refreshing file list...');
            // Add a small delay to ensure backend has processed the deletion
            setTimeout(async () => {
                await this.loadFiles();
            }, 500);
        } catch (error) {
            this.showMessage(`Failed to delete file: ${error.message}`, 'error');
        }
    }

    async showFileInfo(fileId) {
        try {
            const response = await fetch(`${this.apiBase}/${fileId}/info`);
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to get file info');
            }

            const fileInfo = await response.json();
            const uploadDate = new Date(fileInfo.upload_date).toLocaleString();
            const fileSize = this.formatFileSize(fileInfo.file_size);

            const infoMessage = `
                📄 <strong>${this.escapeHtml(fileInfo.original_filename)}</strong><br>
                📏 Size: ${fileSize}<br>
                🏷️ Type: ${fileInfo.mime_type}<br>
                📅 Uploaded: ${uploadDate}<br>
                🆔 ID: ${fileInfo.id}
            `;

            this.showMessage(infoMessage, 'info', 8000);
        } catch (error) {
            this.showMessage(`Failed to get file info: ${error.message}`, 'error');
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
        return '📎';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showMessage(message, type = 'info', duration = 5000) {
        const messageContainer = document.getElementById('messageContainer');
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${type}`;
        messageElement.innerHTML = message;

        messageContainer.appendChild(messageElement);

        // Auto-remove message after duration
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.remove();
            }
        }, duration);

        // Remove on click
        messageElement.addEventListener('click', () => {
            messageElement.remove();
        });
    }
}

// Initialize the file manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.fileManager = new FileManager();
});
