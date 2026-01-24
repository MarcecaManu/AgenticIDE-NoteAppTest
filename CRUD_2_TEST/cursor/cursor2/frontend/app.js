// API Base URL
const API_URL = '/api/notes/';

// State
let allNotes = [];
let isEditing = false;

// DOM Elements
const noteForm = document.getElementById('noteForm');
const formTitle = document.getElementById('formTitle');
const noteIdInput = document.getElementById('noteId');
const noteTitleInput = document.getElementById('noteTitle');
const noteContentInput = document.getElementById('noteContent');
const saveBtn = document.getElementById('saveBtn');
const cancelBtn = document.getElementById('cancelBtn');
const newNoteBtn = document.getElementById('newNoteBtn');
const searchInput = document.getElementById('searchInput');
const notesList = document.getElementById('notesList');

// Event Listeners
document.addEventListener('DOMContentLoaded', loadNotes);
newNoteBtn.addEventListener('click', showNewNoteForm);
saveBtn.addEventListener('click', saveNote);
cancelBtn.addEventListener('click', hideNoteForm);
searchInput.addEventListener('input', filterNotes);

// Load all notes from API
async function loadNotes() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Failed to load notes');
        
        allNotes = await response.json();
        renderNotes(allNotes);
    } catch (error) {
        console.error('Error loading notes:', error);
        showError('Failed to load notes');
    }
}

// Render notes to the DOM
function renderNotes(notes) {
    notesList.innerHTML = '';
    
    if (notes.length === 0) {
        notesList.innerHTML = `
            <div class="empty-state">
                <p>No notes found. Create your first note!</p>
            </div>
        `;
        return;
    }
    
    notes.forEach(note => {
        const noteCard = createNoteCard(note);
        notesList.appendChild(noteCard);
    });
}

// Create a note card element
function createNoteCard(note) {
    const card = document.createElement('div');
    card.className = 'note-card';
    
    const createdDate = new Date(note.createdAt).toLocaleString();
    const updatedDate = new Date(note.updatedAt).toLocaleString();
    
    card.innerHTML = `
        <h3>${escapeHtml(note.title)}</h3>
        <p>${escapeHtml(note.content)}</p>
        <div class="note-meta">
            Created: ${createdDate} | Updated: ${updatedDate}
        </div>
        <div class="note-actions">
            <button class="btn btn-edit" onclick="editNote('${note.id}')">Edit</button>
            <button class="btn btn-delete" onclick="deleteNote('${note.id}')">Delete</button>
        </div>
    `;
    
    return card;
}

// Show new note form
function showNewNoteForm() {
    isEditing = false;
    formTitle.textContent = 'Create New Note';
    noteIdInput.value = '';
    noteTitleInput.value = '';
    noteContentInput.value = '';
    noteForm.classList.add('active');
    noteTitleInput.focus();
}

// Hide note form
function hideNoteForm() {
    noteForm.classList.remove('active');
    noteIdInput.value = '';
    noteTitleInput.value = '';
    noteContentInput.value = '';
}

// Save note (create or update)
async function saveNote() {
    const title = noteTitleInput.value.trim();
    const content = noteContentInput.value.trim();
    
    if (!title || !content) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const noteId = noteIdInput.value;
        let response;
        
        if (noteId) {
            // Update existing note
            response = await fetch(`${API_URL}${noteId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, content })
            });
        } else {
            // Create new note
            response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, content })
            });
        }
        
        if (!response.ok) throw new Error('Failed to save note');
        
        hideNoteForm();
        await loadNotes();
        searchInput.value = '';
    } catch (error) {
        console.error('Error saving note:', error);
        showError('Failed to save note');
    }
}

// Edit note
async function editNote(noteId) {
    try {
        const response = await fetch(`${API_URL}${noteId}`);
        if (!response.ok) throw new Error('Failed to load note');
        
        const note = await response.json();
        
        isEditing = true;
        formTitle.textContent = 'Edit Note';
        noteIdInput.value = note.id;
        noteTitleInput.value = note.title;
        noteContentInput.value = note.content;
        noteForm.classList.add('active');
        noteTitleInput.focus();
    } catch (error) {
        console.error('Error loading note:', error);
        showError('Failed to load note');
    }
}

// Delete note
async function deleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}${noteId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete note');
        
        await loadNotes();
        searchInput.value = '';
    } catch (error) {
        console.error('Error deleting note:', error);
        showError('Failed to delete note');
    }
}

// Filter notes by title
function filterNotes() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    if (!searchTerm) {
        renderNotes(allNotes);
        return;
    }
    
    const filteredNotes = allNotes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );
    
    renderNotes(filteredNotes);
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show error message
function showError(message) {
    alert(message);
}

