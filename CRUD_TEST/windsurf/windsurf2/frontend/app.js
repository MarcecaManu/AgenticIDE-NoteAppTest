const API_URL = 'http://localhost:8000/api/notes';  // Base URL without trailing slash

// DOM Elements
const notesList = document.getElementById('notesList');
const noteForm = document.querySelector('.note-form');
const noteTitleInput = document.getElementById('noteTitle');
const noteContentInput = document.getElementById('noteContent');
const saveNoteButton = document.getElementById('saveNote');
const cancelEditButton = document.getElementById('cancelEdit');
const searchInput = document.getElementById('searchInput');
const editNoteId = document.getElementById('editNoteId');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load notes when page loads
    loadNotes();

    // Set up event listeners
    cancelEditButton.addEventListener('click', cancelEdit);
    searchInput.addEventListener('input', debounce(handleSearch, 300));
});

// Refresh notes periodically
setInterval(() => {
    if (!editNoteId.value) { // Don't refresh while editing
        loadNotes(searchInput.value);
    }
}, 5000); // Refresh every 5 seconds

// Form submit handler (defined in HTML)
window.handleSubmit = async function(e) {
    e.preventDefault(); // Prevent form from submitting normally
    const title = noteTitleInput.value.trim();
    const content = noteContentInput.value.trim();
    
    if (!title || !content) {
        alert('Please fill in both title and content');
        return;
    }

    const noteData = { title, content };
    const id = editNoteId.value;

    try {
        const url = id ? `${API_URL}/${id}` : `${API_URL}/`;
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(noteData),
        });

        if (!response.ok) throw new Error('Failed to save note');
        
        resetForm();
        loadNotes(searchInput.value);
    } catch (error) {
        console.error('Error saving note:', error);
        alert('Failed to save note. Please try again.');
    }
};

// Debounce function for search
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

// Load notes
async function loadNotes(search = '') {
    try {
        const url = search ? `${API_URL}/?search=${encodeURIComponent(search)}` : `${API_URL}/`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load notes');

        const notes = await response.json();
        displayNotes(notes);
    } catch (error) {
        console.error('Error loading notes:', error);
        notesList.innerHTML = '<p class="error">Failed to load notes. Please try again.</p>';
    }
}

// Display notes in the UI
function displayNotes(notes) {
    if (!notes || notes.length === 0) {
        notesList.innerHTML = '<p class="no-notes">No notes found. Create one!</p>';
        return;
    }

    notesList.innerHTML = notes.map(note => `
        <div class="note">
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.content)}</p>
            <div class="note-actions">
                <button onclick="editNote('${note.id}')">Edit</button>
                <button onclick="deleteNote('${note.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Edit note
async function editNote(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`);
        const note = await response.json();
        
        noteTitleInput.value = note.title;
        noteContentInput.value = note.content;
        editNoteId.value = id;
        saveNoteButton.textContent = 'Update Note';
        cancelEditButton.style.display = 'inline';
    } catch (error) {
        console.error('Error loading note for edit:', error);
        alert('Failed to load note for editing');
    }
}

// Delete note
async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) throw new Error('Failed to delete note');
        
        // Reload notes with current search term
        loadNotes(searchInput.value);
    } catch (error) {
        console.error('Error deleting note:', error);
        alert('Failed to delete note. Please try again.');
    }
}

// Cancel edit mode
function cancelEdit() {
    resetForm();
}

// Reset form to create mode
function resetForm() {
    noteForm.reset();
    editNoteId.value = '';
    saveNoteButton.textContent = 'Save Note';
    cancelEditButton.style.display = 'none';
}

// Handle search
function handleSearch(e) {
    loadNotes(e.target.value);
}

// Escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
