const API_URL = 'http://localhost:8000/api/notes';

// DOM Elements
const noteForm = document.getElementById('noteForm');
const notesList = document.getElementById('notesList');
const searchInput = document.getElementById('searchInput');
const titleInput = document.getElementById('titleInput');
const contentInput = document.getElementById('contentInput');
const noteIdInput = document.getElementById('noteId');
const submitBtn = document.getElementById('submitBtn');
const cancelBtn = document.getElementById('cancelBtn');

let notes = [];

// Fetch all notes
async function fetchNotes() {
    try {
        const response = await fetch(API_URL);
        notes = await response.json();
        displayNotes();
    } catch (error) {
        console.error('Error fetching notes:', error);
    }
}

// Display notes
function displayNotes() {
    const searchTerm = searchInput.value.toLowerCase();
    const filteredNotes = notes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );

    notesList.innerHTML = filteredNotes.map(note => `
        <div class="note-card">
            <div class="note-actions">
                <button onclick="editNote(${note.id})">Edit</button>
                <button onclick="deleteNote(${note.id})">Delete</button>
            </div>
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.content)}</p>
            <div class="date">
                Created: ${new Date(note.created_at).toLocaleString()}<br>
                Updated: ${new Date(note.updated_at).toLocaleString()}
            </div>
        </div>
    `).join('');
}

// Create/Update note
async function handleSubmit(event) {
    event.preventDefault();

    const noteData = {
        title: titleInput.value,
        content: contentInput.value
    };

    try {
        const isEditing = noteIdInput.value !== '';
        const url = isEditing ? `${API_URL}/${noteIdInput.value}` : API_URL;
        const method = isEditing ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(noteData)
        });

        if (!response.ok) {
            throw new Error('Failed to save note');
        }

        await fetchNotes();
        resetForm();
    } catch (error) {
        console.error('Error saving note:', error);
    }
}

// Delete note
async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete note');
        }

        await fetchNotes();
    } catch (error) {
        console.error('Error deleting note:', error);
    }
}

// Edit note
function editNote(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        noteIdInput.value = note.id;
        titleInput.value = note.title;
        contentInput.value = note.content;
        submitBtn.textContent = 'Update Note';
        cancelBtn.style.display = 'inline-block';
    }
}

// Reset form
function resetForm() {
    noteForm.reset();
    noteIdInput.value = '';
    submitBtn.textContent = 'Add Note';
    cancelBtn.style.display = 'none';
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

// Event Listeners
noteForm.addEventListener('submit', handleSubmit);
cancelBtn.addEventListener('click', resetForm);
searchInput.addEventListener('input', displayNotes);

// Initial load
fetchNotes(); 