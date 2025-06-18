const API_BASE_URL = 'http://localhost:8000/api/notes/';

class NoteManager {
    constructor() {
        this.notes = [];
        this.currentNoteId = null;
        this.initializeElements();
        this.addEventListeners();
        this.loadNotes();
    }

    initializeElements() {
        this.searchInput = document.getElementById('searchInput');
        this.titleInput = document.getElementById('titleInput');
        this.contentInput = document.getElementById('contentInput');
        this.saveButton = document.getElementById('saveButton');
        this.cancelButton = document.getElementById('cancelButton');
        this.notesList = document.getElementById('notesList');
    }

    addEventListeners() {
        this.searchInput.addEventListener('input', () => this.filterNotes());
        this.saveButton.addEventListener('click', () => this.saveNote());
        this.cancelButton.addEventListener('click', () => this.cancelEdit());
    }

    async loadNotes() {
        try {
            const response = await fetch(API_BASE_URL);
            this.notes = await response.json();
            this.renderNotes();
        } catch (error) {
            console.error('Error loading notes:', error);
        }
    }

    renderNotes() {
        const searchTerm = this.searchInput.value.toLowerCase();
        const filteredNotes = this.notes.filter(note => 
            note.title.toLowerCase().includes(searchTerm)
        );

        this.notesList.innerHTML = filteredNotes.map(note => `
            <div class="note-card">
                <h3>${this.escapeHtml(note.title)}</h3>
                <p>${this.escapeHtml(note.content)}</p>
                <div class="note-actions">
                    <button onclick="noteManager.editNote(${note.id})">Edit</button>
                    <button onclick="noteManager.deleteNote(${note.id})">Delete</button>
                </div>
                <div class="timestamp">
                    Created: ${new Date(note.created_at).toLocaleString()}<br>
                    Updated: ${new Date(note.updated_at).toLocaleString()}
                </div>
            </div>
        `).join('');
    }

    filterNotes() {
        this.renderNotes();
    }

    async saveNote() {
        const title = this.titleInput.value.trim();
        const content = this.contentInput.value.trim();

        if (!title || !content) {
            alert('Please fill in both title and content');
            return;
        }

        const noteData = { title, content };
        
        try {
            let response;
            if (this.currentNoteId) {
                // Update existing note
                response = await fetch(`${API_BASE_URL}${this.currentNoteId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(noteData)
                });
            } else {
                // Create new note
                response = await fetch(API_BASE_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(noteData)
                });
            }

            if (!response.ok) throw new Error('Failed to save note');
            
            await this.loadNotes();
            this.clearForm();
        } catch (error) {
            console.error('Error saving note:', error);
            alert('Failed to save note');
        }
    }

    editNote(id) {
        const note = this.notes.find(n => n.id === id);
        if (note) {
            this.currentNoteId = id;
            this.titleInput.value = note.title;
            this.contentInput.value = note.content;
            this.saveButton.textContent = 'Update Note';
            this.cancelButton.style.display = 'inline';
        }
    }

    async deleteNote(id) {
        if (!confirm('Are you sure you want to delete this note?')) return;

        try {
            const response = await fetch(`${API_BASE_URL}${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to delete note');
            
            await this.loadNotes();
        } catch (error) {
            console.error('Error deleting note:', error);
            alert('Failed to delete note');
        }
    }

    cancelEdit() {
        this.clearForm();
    }

    clearForm() {
        this.currentNoteId = null;
        this.titleInput.value = '';
        this.contentInput.value = '';
        this.saveButton.textContent = 'Save Note';
        this.cancelButton.style.display = 'none';
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

const noteManager = new NoteManager();