class FileManager {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/files';
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.filesContainer = document.getElementById('filesContainer');
        this.emptyState = document.getElementById('emptyState');
        this.loading = document.getElementById('loading');
        
        this.initializeEventListeners();
        this.loadFiles();
    }

    initializeEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('drag-over');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('drag-over');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('drag-over');
            this.handleFiles(e.dataTransfer.files);
        });

        // Click to open file dialog
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });
    }

    showLoading() {
        this.loading.style.display = 'block';
    }

    hideLoading() {
        this.loading.style.display = 'none';
    }

    showAlert(message, type = 'info') {
        const alertElement = document.getElementById(`alert-${type}`);
        alertElement.textContent = message;
        alertElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            alertElement.style.display = 'none';
        }, 5000);
    }

    hideAllAlerts() {
        ['success', 'error', 'info'].forEach(type => {
            document.getElementById(`alert-${type}`).style.display = 'none';
        });
    }

    async handleFiles(files) {
        if (files.length === 0) return;

        this.hideAllAlerts();
        
        // Validate files before upload
        const validFiles = [];
        const invalidFiles = [];

        for (const file of files) {
            if (this.validateFile(file)) {
                validFiles.push(file);
            } else {
                invalidFiles.push(file);
            }
        }

        if (invalidFiles.length > 0) {
            const invalidNames = invalidFiles.map(f => f.name).join(', ');
            this.showAlert(`Invalid files rejected: ${invalidNames}. Only images, PDFs, and text files under 10MB are allowed.`, 'error');
        }

        if (validFiles.length === 0) return;

        // Upload valid files
        for (const file of validFiles) {
            await this.uploadFile(file);
        }

        // Refresh file list
        await this.loadFiles();
        
        // Clear file input
        this.fileInput.value = '';
    }

    validateFile(file) {
        // Check file size (10MB = 10 * 1024 * 1024 bytes)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            return false;
        }

        // Check file type
        const allowedTypes = [
            'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
            'application/pdf',
            'text/plain', 'text/csv', 'text/html', 'text/css', 'text/javascript',
            'application/json', 'application/xml'
        ];

        const allowedExtensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
            '.pdf',
            '.txt', '.csv', '.html', '.css', '.js', '.json', '.xml'
        ];

        const fileName = file.name.toLowerCase();
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        const hasValidType = allowedTypes.includes(file.type);

        return hasValidExtension && hasValidType;
    }

    async uploadFile(file) {
        try {
            this.showLoading();

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${this.apiBaseUrl}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }

            const result = await response.json();
            this.showAlert(`Successfully uploaded: ${result.original_filename}`, 'success');

        } catch (error) {
            console.error('Upload error:', error);
            this.showAlert(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadFiles() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/`);
            
            if (!response.ok) {
                throw new Error('Failed to load files');
            }

            const files = await response.json();
            this.renderFileList(files);

        } catch (error) {
            console.error('Load files error:', error);
            this.showAlert('Failed to load files', 'error');
        }
    }

    renderFileList(files) {
        // Clear existing files
        this.filesContainer.innerHTML = '';

        if (files.length === 0) {
            this.filesContainer.appendChild(this.emptyState);
            return;
        }

        files.forEach(file => {
            const fileElement = this.createFileElement(file);
            this.filesContainer.appendChild(fileElement);
        });
    }

    createFileElement(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const fileIcon = this.getFileIcon(file.mime_type);
        const fileSize = this.formatFileSize(file.file_size);
        const uploadDate = new Date(file.upload_date).toLocaleString();

        fileItem.innerHTML = `
            <div class="file-icon ${this.getIconClass(file.mime_type)}">
                ${fileIcon}
            </div>
            <div class="file-details">
                <div class="file-name">${this.escapeHtml(file.original_filename)}</div>
                <div class="file-meta">
                    ${fileSize} • ${file.mime_type} • Uploaded: ${uploadDate}
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-info" onclick="fileManager.getFileInfo('${file.id}')">
                    ℹ️ Info
                </button>
                <a href="${this.apiBaseUrl}/${file.id}" class="btn btn-primary" download>
                    ⬇️ Download
                </a>
                <button class="btn btn-danger" onclick="fileManager.deleteFile('${file.id}', '${this.escapeHtml(file.original_filename)}')">
                    🗑️ Delete
                </button>
            </div>
        `;

        return fileItem;
    }

    getFileIcon(mimeType) {
        if (mimeType.startsWith('image/')) return '🖼️';
        if (mimeType === 'application/pdf') return '📄';
        if (mimeType.startsWith('text/')) return '📝';
        return '📄';
    }

    getIconClass(mimeType) {
        if (mimeType.startsWith('image/')) return 'image';
        if (mimeType === 'application/pdf') return 'pdf';
        if (mimeType.startsWith('text/')) return 'text';
        return 'text';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    async getFileInfo(fileId) {
        try {
            this.showLoading();

            const response = await fetch(`${this.apiBaseUrl}/${fileId}/info`);
            
            if (!response.ok) {
                throw new Error('Failed to get file info');
            }

            const fileInfo = await response.json();
            
            const infoMessage = `
File Information:
━━━━━━━━━━━━━━━━━━━━
📁 Name: ${fileInfo.original_filename}
📏 Size: ${this.formatFileSize(fileInfo.file_size)}
🏷️ Type: ${fileInfo.mime_type}
📅 Uploaded: ${new Date(fileInfo.upload_date).toLocaleString()}
🆔 ID: ${fileInfo.id}
            `;

            alert(infoMessage);

        } catch (error) {
            console.error('Get file info error:', error);
            this.showAlert('Failed to get file information', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async deleteFile(fileId, fileName) {
        if (!confirm(`Are you sure you want to delete "${fileName}"?`)) {
            return;
        }

        try {
            this.showLoading();

            const response = await fetch(`${this.apiBaseUrl}/${fileId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Delete failed');
            }

            this.showAlert(`Successfully deleted: ${fileName}`, 'success');
            await this.loadFiles(); // Refresh file list

        } catch (error) {
            console.error('Delete error:', error);
            this.showAlert(`Delete failed: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
}

// Initialize the file manager when the page loads
let fileManager;

document.addEventListener('DOMContentLoaded', () => {
    fileManager = new FileManager();
});

// Add some utility functions for better UX
window.addEventListener('beforeunload', (e) => {
    // Warn user if there are ongoing uploads
    const loading = document.getElementById('loading');
    if (loading.style.display === 'block') {
        e.preventDefault();
        e.returnValue = 'Upload in progress. Are you sure you want to leave?';
    }
});

// Handle connection errors gracefully
window.addEventListener('online', () => {
    document.querySelector('.header p').textContent = 'Upload, manage, and download your files securely';
});

window.addEventListener('offline', () => {
    document.querySelector('.header p').textContent = 'You are offline. Please check your internet connection.';
});