// API Base URL
const API_URL = 'http://localhost:8000/api/notes/';

// Global state
let currentNoteId = null;
let allNotes = [];

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    loadNotes();
    setupSearchListener();
});

// Setup search input listener with debounce
function setupSearchListener() {
    const searchInput = document.getElementById('searchInput');
    let debounceTimer;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            filterNotes(e.target.value);
        }, 300);
    });
}

// Load all notes from API
async function loadNotes() {
    try {
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        allNotes = await response.json();
        displayNotes(allNotes);
        hideError();
    } catch (error) {
        console.error('Error loading notes:', error);
        showError('Failed to load notes. Make sure the backend server is running on http://localhost:8000');
    }
}

// Filter notes by search query
async function filterNotes(query) {
    try {
        const url = query ? `${API_URL}?search=${encodeURIComponent(query)}` : API_URL;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const notes = await response.json();
        displayNotes(notes);
        hideError();
    } catch (error) {
        console.error('Error filtering notes:', error);
        showError('Failed to filter notes');
    }
}

// Display notes in the UI
function displayNotes(notes) {
    const container = document.getElementById('notesContainer');
    
    if (notes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h2>No notes found</h2>
                <p>Try a different search or create a new note!</p>
            </div>
        `;
        return;
    }
    
    const notesHTML = notes.map(note => `
        <div class="note-card">
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.content)}</p>
            <div class="note-meta">
                Created: ${formatDate(note.createdAt)}<br>
                Updated: ${formatDate(note.updatedAt)}
            </div>
            <div class="note-actions">
                <button class="btn btn-primary" onclick="editNote(${note.id})">
                    ✏️ Edit
                </button>
                <button class="btn btn-danger" onclick="deleteNote(${note.id})">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = `<div class="notes-grid">${notesHTML}</div>`;
}

// Create new note - open modal
function createNote() {
    currentNoteId = null;
    document.getElementById('modalTitle').textContent = 'Create Note';
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteContent').value = '';
    document.getElementById('saveButton').textContent = 'Save Note';
    openModal();
}

// Edit existing note - open modal with data
async function editNote(id) {
    try {
        const response = await fetch(`${API_URL}${id}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const note = await response.json();
        
        currentNoteId = id;
        document.getElementById('modalTitle').textContent = 'Edit Note';
        document.getElementById('noteTitle').value = note.title;
        document.getElementById('noteContent').value = note.content;
        document.getElementById('saveButton').textContent = 'Update Note';
        openModal();
        hideError();
    } catch (error) {
        console.error('Error loading note:', error);
        showError('Failed to load note for editing');
    }
}

// Save note (create or update)
document.getElementById('noteForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('noteTitle').value.trim();
    const content = document.getElementById('noteContent').value.trim();
    
    if (!title || !content) {
        showError('Title and content are required');
        return;
    }
    
    const noteData = { title, content };
    
    try {
        let response;
        
        if (currentNoteId === null) {
            // Create new note
            response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(noteData),
            });
        } else {
            // Update existing note
            response = await fetch(`${API_URL}${currentNoteId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(noteData),
            });
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        closeModal();
        await loadNotes();
        hideError();
    } catch (error) {
        console.error('Error saving note:', error);
        showError('Failed to save note');
    }
});

// Delete note
async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}${id}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        await loadNotes();
        hideError();
    } catch (error) {
        console.error('Error deleting note:', error);
        showError('Failed to delete note');
    }
}

// Modal controls
function openModal() {
    document.getElementById('noteModal').classList.add('active');
}

function closeModal() {
    document.getElementById('noteModal').classList.remove('active');
    currentNoteId = null;
}

// Close modal when clicking outside
document.getElementById('noteModal').addEventListener('click', (e) => {
    if (e.target.id === 'noteModal') {
        closeModal();
    }
});

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.classList.add('active');
}

function hideError() {
    const errorElement = document.getElementById('errorMessage');
    errorElement.classList.remove('active');
}

