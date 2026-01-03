// API Base URL
const API_BASE_URL = 'http://localhost:8000/api/notes';

// State
let allNotes = [];
let currentSearchQuery = '';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const createNoteForm = document.getElementById('createNoteForm');
const editNoteForm = document.getElementById('editNoteForm');
const notesContainer = document.getElementById('notesContainer');
const createFormSection = document.getElementById('createFormSection');
const editFormSection = document.getElementById('editFormSection');
const cancelEditBtn = document.getElementById('cancelEditBtn');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadNotes();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    searchInput.addEventListener('input', handleSearch);
    createNoteForm.addEventListener('submit', handleCreateNote);
    editNoteForm.addEventListener('submit', handleUpdateNote);
    cancelEditBtn.addEventListener('click', cancelEdit);
}

// API Functions
async function loadNotes() {
    try {
        const response = await fetch(API_BASE_URL + '/');
        if (!response.ok) {
            throw new Error('Failed to load notes');
        }
        allNotes = await response.json();
        renderNotes(allNotes);
    } catch (error) {
        showError('Failed to load notes. Make sure the backend server is running.');
        console.error('Error loading notes:', error);
    }
}

async function createNote(title, content) {
    try {
        const response = await fetch(API_BASE_URL + '/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
        });

        if (!response.ok) {
            throw new Error('Failed to create note');
        }

        const newNote = await response.json();
        allNotes.push(newNote);
        renderNotes(filterNotes(allNotes, currentSearchQuery));
        showSuccess('Note created successfully!');
        return newNote;
    } catch (error) {
        showError('Failed to create note.');
        console.error('Error creating note:', error);
        throw error;
    }
}

async function updateNote(id, title, content) {
    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
        });

        if (!response.ok) {
            throw new Error('Failed to update note');
        }

        const updatedNote = await response.json();
        const index = allNotes.findIndex(note => note.id === id);
        if (index !== -1) {
            allNotes[index] = updatedNote;
        }
        renderNotes(filterNotes(allNotes, currentSearchQuery));
        showSuccess('Note updated successfully!');
        return updatedNote;
    } catch (error) {
        showError('Failed to update note.');
        console.error('Error updating note:', error);
        throw error;
    }
}

async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Failed to delete note');
        }

        allNotes = allNotes.filter(note => note.id !== id);
        renderNotes(filterNotes(allNotes, currentSearchQuery));
        showSuccess('Note deleted successfully!');
    } catch (error) {
        showError('Failed to delete note.');
        console.error('Error deleting note:', error);
    }
}

// Event Handlers
async function handleCreateNote(e) {
    e.preventDefault();

    const title = document.getElementById('createTitle').value.trim();
    const content = document.getElementById('createContent').value.trim();

    if (!title || !content) {
        showError('Please fill in all fields.');
        return;
    }

    try {
        await createNote(title, content);
        createNoteForm.reset();
    } catch (error) {
        // Error already handled in createNote
    }
}

async function handleUpdateNote(e) {
    e.preventDefault();

    const id = parseInt(document.getElementById('editNoteId').value);
    const title = document.getElementById('editTitle').value.trim();
    const content = document.getElementById('editContent').value.trim();

    if (!title || !content) {
        showError('Please fill in all fields.');
        return;
    }

    try {
        await updateNote(id, title, content);
        cancelEdit();
    } catch (error) {
        // Error already handled in updateNote
    }
}

function handleSearch(e) {
    currentSearchQuery = e.target.value.toLowerCase().trim();
    const filtered = filterNotes(allNotes, currentSearchQuery);
    renderNotes(filtered);
}

function filterNotes(notes, query) {
    if (!query) {
        return notes;
    }
    return notes.filter(note => 
        note.title.toLowerCase().includes(query)
    );
}

// UI Functions
function renderNotes(notes) {
    if (notes.length === 0) {
        notesContainer.innerHTML = '<div class="empty-state">No notes found. Create your first note!</div>';
        return;
    }

    const notesHTML = notes.map(note => createNoteCard(note)).join('');
    notesContainer.innerHTML = `<div class="notes-grid">${notesHTML}</div>`;
}

function createNoteCard(note) {
    const createdDate = new Date(note.createdAt).toLocaleString();
    const updatedDate = new Date(note.updatedAt).toLocaleString();

    return `
        <div class="note-card" data-note-id="${note.id}">
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.content)}</p>
            <div class="note-meta">
                <div>Created: ${createdDate}</div>
                <div>Updated: ${updatedDate}</div>
            </div>
            <div class="note-actions">
                <button class="btn-edit" onclick="editNote(${note.id})">Edit</button>
                <button class="btn-danger" onclick="deleteNote(${note.id})">Delete</button>
            </div>
        </div>
    `;
}

function editNote(id) {
    const note = allNotes.find(n => n.id === id);
    if (!note) {
        showError('Note not found.');
        return;
    }

    document.getElementById('editNoteId').value = note.id;
    document.getElementById('editTitle').value = note.title;
    document.getElementById('editContent').value = note.content;

    editFormSection.style.display = 'block';
    createFormSection.style.display = 'none';

    // Scroll to edit form
    editFormSection.scrollIntoView({ behavior: 'smooth' });
}

function cancelEdit() {
    editFormSection.style.display = 'none';
    createFormSection.style.display = 'block';
    editNoteForm.reset();
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';

    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';

    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make functions available globally for onclick handlers
window.editNote = editNote;
window.deleteNote = deleteNote;
