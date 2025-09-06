const API_URL = 'http://localhost:8000/api/notes';

// DOM Elements
const notesList = document.getElementById('notes-list');
const noteForm = document.querySelector('.note-form');
const noteIdInput = document.getElementById('note-id');
const titleInput = document.getElementById('title');
const contentInput = document.getElementById('content');
const saveBtn = document.getElementById('save-btn');
const clearBtn = document.getElementById('clear-btn');
const searchInput = document.getElementById('search');

// State
let notes = [];

// Event Listeners
document.addEventListener('DOMContentLoaded', fetchNotes);
noteForm.addEventListener('submit', handleSubmit);
clearBtn.addEventListener('click', clearForm);
searchInput.addEventListener('input', handleSearch);

// Fetch all notes
async function fetchNotes() {
    try {
        const response = await fetch(API_URL);
        notes = await response.json();
        renderNotes(notes);
    } catch (error) {
        console.error('Error fetching notes:', error);
    }
}

// Render notes
function renderNotes(notesToRender) {
    notesList.innerHTML = notesToRender.map(note => `
        <div class="note-card">
            <h3>${note.title}</h3>
            <p>${note.content}</p>
            <div class="actions">
                <button class="edit-btn" onclick="editNote(${note.id})">Edit</button>
                <button class="delete-btn" onclick="deleteNote(${note.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Handle form submission (create/update)
async function handleSubmit(e) {
    e.preventDefault();
    const note = {
        title: titleInput.value,
        content: contentInput.value
    };

    try {
        let response;
        if (noteIdInput.value) {
            // Update existing note
            response = await fetch(`${API_URL}/${noteIdInput.value}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(note)
            });
        } else {
            // Create new note
            response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(note)
            });
        }

        if (!response.ok) throw new Error('Failed to save note');
        
        clearForm();
        await fetchNotes();
    } catch (error) {
        console.error('Error saving note:', error);
    }
}

// Edit note
function editNote(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        noteIdInput.value = note.id;
        titleInput.value = note.title;
        contentInput.value = note.content;
        saveBtn.textContent = 'Update Note';
    }
}

// Delete note
async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete note');
        await fetchNotes();
    } catch (error) {
        console.error('Error deleting note:', error);
    }
}

// Clear form
function clearForm() {
    noteIdInput.value = '';
    titleInput.value = '';
    contentInput.value = '';
    saveBtn.textContent = 'Save Note';
}

// Handle search
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const filteredNotes = notes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );
    renderNotes(filteredNotes);
}