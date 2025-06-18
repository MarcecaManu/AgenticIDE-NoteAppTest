const API_BASE_URL = 'http://localhost:8000/api/notes';

// DOM Elements
const notesList = document.getElementById('notesList');
const titleInput = document.getElementById('titleInput');
const contentInput = document.getElementById('contentInput');
const saveButton = document.getElementById('saveButton');
const cancelButton = document.getElementById('cancelButton');
const searchInput = document.getElementById('searchInput');
const noteIdInput = document.getElementById('noteId');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadNotes(); // Load all notes when page loads
});
saveButton.addEventListener('click', saveNote);
cancelButton.addEventListener('click', cancelEdit);
searchInput.addEventListener('input', debounce(handleSearch, 300));

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

async function loadNotes(searchTerm = '') {
    try {
        const url = searchTerm
            ? `${API_BASE_URL}/?search=${encodeURIComponent(searchTerm)}`
            : `${API_BASE_URL}/`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const notes = await response.json();
        displayNotes(notes);
    } catch (error) {
        console.error('Error loading notes:', error);
        notesList.innerHTML = '<p class="error">Failed to load notes. Please try again later.</p>';
    }
}

function displayNotes(notes) {
    notesList.innerHTML = notes.length 
        ? '' 
        : '<p class="no-notes">No notes found. Create your first note!</p>';
    
    notes.forEach(note => {
        const noteElement = createNoteElement(note);
        notesList.appendChild(noteElement);
    });
}

function createNoteElement(note) {
    const div = document.createElement('div');
    div.className = 'note-card';
    
    const created = new Date(note.created_at).toLocaleString();
    const updated = new Date(note.updated_at).toLocaleString();
    
    div.innerHTML = `
        <h3>${escapeHtml(note.title)}</h3>
        <p>${escapeHtml(note.content)}</p>
        <div class="timestamp">
            Created: ${created}<br>
            Updated: ${updated}
        </div>
        <div class="actions">
            <button class="edit-btn" onclick="editNote(${note.id})">Edit</button>
            <button class="delete-btn" onclick="deleteNote(${note.id})">Delete</button>
        </div>
    `;
    return div;
}

async function saveNote() {
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    
    if (!title || !content) {
        alert('Please fill in both title and content');
        return;
    }
    
    const noteId = noteIdInput.value;
    const method = noteId ? 'PUT' : 'POST';
    const url = noteId ? `${API_BASE_URL}/${noteId}` : API_BASE_URL + '/';
    
    try {
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
        });
        
        if (!response.ok) throw new Error('Failed to save note');
        
        resetForm();
        loadNotes(searchInput.value);
    } catch (error) {
        console.error('Error saving note:', error);
        alert('Failed to save note');
    }
}

function editNote(id) {
    fetch(`${API_BASE_URL}/${id}`)
        .then(response => response.json())
        .then(note => {
            titleInput.value = note.title;
            contentInput.value = note.content;
            noteIdInput.value = note.id;
            saveButton.textContent = 'Update Note';
            cancelButton.style.display = 'inline';
        })
        .catch(error => {
            console.error('Error fetching note:', error);
            alert('Failed to load note for editing');
        });
}

async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) throw new Error('Failed to delete note');
        
        loadNotes(searchInput.value);
    } catch (error) {
        console.error('Error deleting note:', error);
        alert('Failed to delete note');
    }
}

function handleSearch() {
    loadNotes(searchInput.value);
}

function cancelEdit() {
    resetForm();
}

function resetForm() {
    titleInput.value = '';
    contentInput.value = '';
    noteIdInput.value = '';
    saveButton.textContent = 'Save Note';
    cancelButton.style.display = 'none';
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
