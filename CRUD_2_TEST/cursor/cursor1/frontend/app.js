// API Base URL
const API_URL = '/api/notes/';

// State
let allNotes = [];
let editingNoteId = null;

// DOM Elements
const noteForm = document.getElementById('noteForm');
const notesList = document.getElementById('notesList');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const titleInput = document.getElementById('title');
const contentInput = document.getElementById('content');
const noteIdInput = document.getElementById('noteId');
const submitBtn = document.getElementById('submitBtn');
const cancelBtn = document.getElementById('cancelBtn');
const formTitle = document.getElementById('formTitle');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadNotes();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    noteForm.addEventListener('submit', handleSubmit);
    cancelBtn.addEventListener('click', resetForm);
    searchInput.addEventListener('input', handleSearch);
}

// Load all notes from API
async function loadNotes() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error('Failed to load notes');
        }
        allNotes = await response.json();
        renderNotes(allNotes);
    } catch (error) {
        console.error('Error loading notes:', error);
        showError('Failed to load notes. Please refresh the page.');
    }
}

// Render notes to the DOM
function renderNotes(notes) {
    notesList.innerHTML = '';
    
    if (notes.length === 0) {
        emptyState.style.display = 'block';
        notesList.style.display = 'none';
        return;
    }
    
    emptyState.style.display = 'none';
    notesList.style.display = 'grid';
    
    notes.forEach(note => {
        const noteCard = createNoteCard(note);
        notesList.appendChild(noteCard);
    });
}

// Create a note card element
function createNoteCard(note) {
    const card = document.createElement('div');
    card.className = 'note-card';
    card.innerHTML = `
        <h3>${escapeHtml(note.title)}</h3>
        <div class="note-meta">
            <span>Created: ${formatDate(note.createdAt)}</span>
            <span>Updated: ${formatDate(note.updatedAt)}</span>
        </div>
        <p>${escapeHtml(note.content)}</p>
        <div class="note-actions">
            <button class="btn btn-edit" onclick="editNote(${note.id})">Edit</button>
            <button class="btn btn-delete" onclick="deleteNote(${note.id})">Delete</button>
        </div>
    `;
    return card;
}

// Handle form submission (create or update)
async function handleSubmit(e) {
    e.preventDefault();
    
    const noteData = {
        title: titleInput.value.trim(),
        content: contentInput.value.trim()
    };
    
    try {
        if (editingNoteId) {
            await updateNote(editingNoteId, noteData);
        } else {
            await createNote(noteData);
        }
        resetForm();
        await loadNotes();
    } catch (error) {
        console.error('Error saving note:', error);
        showError('Failed to save note. Please try again.');
    }
}

// Create a new note
async function createNote(noteData) {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(noteData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to create note');
    }
    
    return await response.json();
}

// Update an existing note
async function updateNote(id, noteData) {
    const response = await fetch(`${API_URL}${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(noteData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to update note');
    }
    
    return await response.json();
}

// Edit note - load data into form
function editNote(id) {
    const note = allNotes.find(n => n.id === id);
    if (!note) return;
    
    editingNoteId = id;
    titleInput.value = note.title;
    contentInput.value = note.content;
    noteIdInput.value = id;
    
    formTitle.textContent = 'Edit Note';
    submitBtn.textContent = 'Update Note';
    cancelBtn.style.display = 'inline-block';
    
    // Scroll to form
    document.querySelector('.form-container').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// Delete a note
async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete note');
        }
        
        await loadNotes();
    } catch (error) {
        console.error('Error deleting note:', error);
        showError('Failed to delete note. Please try again.');
    }
}

// Reset form to initial state
function resetForm() {
    noteForm.reset();
    editingNoteId = null;
    noteIdInput.value = '';
    formTitle.textContent = 'Create New Note';
    submitBtn.textContent = 'Create Note';
    cancelBtn.style.display = 'none';
}

// Handle search/filter
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase().trim();
    
    if (!searchTerm) {
        renderNotes(allNotes);
        return;
    }
    
    const filteredNotes = allNotes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );
    
    renderNotes(filteredNotes);
}

// Utility: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Utility: Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Utility: Show error message
function showError(message) {
    alert(message);
}

// Make functions globally available
window.editNote = editNote;
window.deleteNote = deleteNote;

