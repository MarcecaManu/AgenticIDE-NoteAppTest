class NoteManager {
    constructor() {
        // API endpoint is absolute from the server root
        this.apiUrl = '/api/notes/';
        this.notesList = document.getElementById('notesList');
        this.searchInput = document.getElementById('searchInput');
        this.titleInput = document.getElementById('titleInput');
        this.contentInput = document.getElementById('contentInput');
        this.saveButton = document.getElementById('saveButton');
        this.cancelButton = document.getElementById('cancelButton');
        this.noteIdInput = document.getElementById('noteId');

        this.setupEventListeners();
        this.loadNotes();
    }

    setupEventListeners() {
        this.saveButton.addEventListener('click', () => this.saveNote());
        this.cancelButton.addEventListener('click', () => this.cancelEdit());
        this.searchInput.addEventListener('input', debounce(() => this.loadNotes(), 300));
    }

    async loadNotes() {
        try {
            console.log('Loading notes from:', this.apiUrl); // Debug log
            const searchTerm = this.searchInput.value;
            const url = searchTerm 
                ? `${this.apiUrl}?search=${encodeURIComponent(searchTerm)}`
                : this.apiUrl;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const notes = await response.json();
            this.displayNotes(notes);
        } catch (error) {
            console.error('Error loading notes:', error);
            this.displayError('Failed to load notes. Please ensure the server is running and refresh the page.');
        }
    }

    displayNotes(notes) {
        if (!Array.isArray(notes)) {
            console.error('Received invalid notes data:', notes);
            this.displayError('Invalid data received from server');
            return;
        }

        if (notes.length === 0) {
            this.notesList.innerHTML = '<p class="no-notes">No notes found. Create your first note!</p>';
            return;
        }

        this.notesList.innerHTML = notes.map(note => `
            <div class="note-card" data-id="${note.id}">
                <h3>${escapeHtml(note.title)}</h3>
                <p>${escapeHtml(note.content)}</p>
                <div class="note-meta">
                    Created: ${new Date(note.created_at).toLocaleString()}<br>
                    Updated: ${new Date(note.updated_at).toLocaleString()}
                </div>
                <div class="actions">
                    <button class="edit-btn" onclick="noteManager.editNote(${note.id})">Edit</button>
                    <button class="delete-btn" onclick="noteManager.deleteNote(${note.id})">Delete</button>
                </div>
            </div>
        `).join('');
    }

    async saveNote() {
        try {
            const title = this.titleInput.value.trim();
            const content = this.contentInput.value.trim();
            
            if (!title || !content) {
                alert('Please fill in both title and content');
                return;
            }

            const noteId = this.noteIdInput.value;
            const method = noteId ? 'PUT' : 'POST';
            const url = noteId ? `${this.apiUrl}${noteId}` : this.apiUrl;

            console.log('Saving note to:', url); // Debug log
            console.log('Request payload:', { title, content }); // Debug log

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ title, content })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const savedNote = await response.json();
            console.log('Note saved successfully:', savedNote);

            this.resetForm();
            await this.loadNotes();
            this.displayError('Note deleted successfully!', 'success');
            this.displayError('Note saved successfully!', 'success');
            
        } catch (error) {
            console.error('Error saving note:', error);
            this.displayError(`Failed to save note: ${error.message}`);
        }
    }

    async deleteNote(id) {
        if (!confirm('Are you sure you want to delete this note?')) return;

        try {
            console.log('Deleting note:', id); // Debug log
            const response = await fetch(`${this.apiUrl}${id}`, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            await this.loadNotes();
        } catch (error) {
            console.error('Error deleting note:', error);
            this.displayError(`Failed to delete note: ${error.message}`);
        }
    }

    async editNote(id) {
        try {
            console.log('Loading note for edit:', id); // Debug log
            const response = await fetch(`${this.apiUrl}${id}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const note = await response.json();
            this.titleInput.value = note.title;
            this.contentInput.value = note.content;
            this.noteIdInput.value = note.id;
            this.saveButton.textContent = 'Update Note';
            this.cancelButton.style.display = 'inline-block';
        } catch (error) {
            console.error('Error loading note for edit:', error);
            this.displayError(`Failed to load note for editing. Please try again.`);
        }
    }

    displayError(message, type = 'error') {
        // Remove any existing error messages
        const existingErrors = document.querySelectorAll('.message');
        existingErrors.forEach(el => el.remove());

        // Show error in the UI
        const className = type === 'success' ? 'success-message' : 'error-message';
        const messageHtml = `
            <div class="message ${className}" style="padding: 10px; margin: 10px 0; border-radius: 4px;">
                ${escapeHtml(message)}
            </div>
        `;
        this.notesList.insertAdjacentHTML('beforebegin', messageHtml);
        
        // Remove message after 5 seconds
        setTimeout(() => {
            const messageElement = document.querySelector(`.${className}`);
            if (messageElement) {
                messageElement.remove();
            }
        }, 5000);
    }

    cancelEdit() {
        this.resetForm();
    }

    resetForm() {
        this.titleInput.value = '';
        this.contentInput.value = '';
        this.noteIdInput.value = '';
        this.saveButton.textContent = 'Save Note';
        this.cancelButton.style.display = 'none';
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initialize the note manager
const noteManager = new NoteManager();
