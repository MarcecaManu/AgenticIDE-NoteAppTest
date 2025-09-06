const API_BASE_URL = 'http://localhost:8000/api/notes';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const noteForm = document.querySelector('.note-form');
const titleInput = document.getElementById('titleInput');
const contentInput = document.getElementById('contentInput');
const noteIdInput = document.getElementById('noteId');
const saveButton = document.getElementById('saveButton');
const cancelButton = document.getElementById('cancelButton');
const notesList = document.getElementById('notesList');

// Event Listeners
searchInput.addEventListener('input', debounce(fetchNotes, 300));
saveButton.addEventListener('click', saveNote);
cancelButton.addEventListener('click', cancelEdit);

// Fetch and display notes
async function fetchNotes() {
    const searchQuery = searchInput.value;
    const url = searchQuery 
        ? `${API_BASE_URL}/?title=${encodeURIComponent(searchQuery)}`
        : API_BASE_URL + '/';

    try {
        const response = await fetch(url);
        const notes = await response.json();
        displayNotes(notes);
    } catch (error) {
        console.error('Error fetching notes:', error);
    }
}

function displayNotes(notes) {
    notesList.innerHTML = notes.map(note => `
        <div class="note-card">
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.content)}</p>
            <div class="note-actions">
                <button onclick="editNote(${note.id})">Edit</button>
                <button onclick="deleteNote(${note.id})">Delete</button>
            </div>
            <div class="timestamp">
                Created: ${new Date(note.createdAt).toLocaleString()}<br>
                Updated: ${new Date(note.updatedAt).toLocaleString()}
            </div>
        </div>
    `).join('');
}

async function saveNote() {
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    
    if (!title || !content) {
        alert('Please fill in both title and content');
        return;
    }

    const noteData = { title, content };
    const noteId = noteIdInput.value;
    
    try {
        const url = noteId 
            ? `${API_BASE_URL}/${noteId}`
            : API_BASE_URL + '/';
            
        const response = await fetch(url, {
            method: noteId ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(noteData)
        });

        if (response.ok) {
            resetForm();
            fetchNotes();
        } else {
            throw new Error('Failed to save note');
        }
    } catch (error) {
        console.error('Error saving note:', error);
        alert('Failed to save note');
    }
}

async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            fetchNotes();
        } else {
            throw new Error('Failed to delete note');
        }
    } catch (error) {
        console.error('Error deleting note:', error);
        alert('Failed to delete note');
    }
}

async function editNote(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/${id}`);
        const note = await response.json();
        
        titleInput.value = note.title;
        contentInput.value = note.content;
        noteIdInput.value = note.id;
        saveButton.textContent = 'Update Note';
        cancelButton.style.display = 'block';
    } catch (error) {
        console.error('Error fetching note:', error);
        alert('Failed to load note for editing');
    }
}

function cancelEdit() {
    resetForm();
}

function resetForm() {
    noteIdInput.value = '';
    titleInput.value = '';
    contentInput.value = '';
    saveButton.textContent = 'Save Note';
    cancelButton.style.display = 'none';
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

// Initial load
fetchNotes();