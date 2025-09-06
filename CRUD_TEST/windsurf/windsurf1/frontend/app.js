const API_URL = 'http://127.0.0.1:8000/api/notes/';

// DOM Elements
const notesList = document.getElementById('notesList');
const noteForm = document.querySelector('.note-form');
const noteIdInput = document.getElementById('noteId');
const noteTitleInput = document.getElementById('noteTitle');
const noteContentInput = document.getElementById('noteContent');
const saveButton = document.getElementById('saveButton');
const cancelButton = document.getElementById('cancelButton');
const searchInput = document.getElementById('searchInput');

let notes = [];

// Fetch all notes
async function fetchNotes() {
    try {
        const response = await fetch(API_URL);
        notes = await response.json();
        renderNotes();
    } catch (error) {
        console.error('Error fetching notes:', error);
    }
}

// Create a new note
async function createNote(title, content) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
        });
        const newNote = await response.json();
        notes.push(newNote);
        renderNotes();
        resetForm();
    } catch (error) {
        console.error('Error creating note:', error);
    }
}

// Update an existing note
async function updateNote(id, title, content) {
    try {
        const response = await fetch(`${API_URL}${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
        });
        const updatedNote = await response.json();
        const index = notes.findIndex(note => note.id === id);
        notes[index] = updatedNote;
        renderNotes();
        resetForm();
    } catch (error) {
        console.error('Error updating note:', error);
    }
}

// Delete a note
async function deleteNote(id) {
    try {
        await fetch(`${API_URL}${id}`, {
            method: 'DELETE',
        });
        notes = notes.filter(note => note.id !== id);
        renderNotes();
    } catch (error) {
        console.error('Error deleting note:', error);
    }
}

// Render notes list
function renderNotes() {
    const searchTerm = searchInput.value.toLowerCase();
    const filteredNotes = notes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );

    notesList.innerHTML = filteredNotes.map(note => `
        <div class="note-card">
            <h3>${note.title}</h3>
            <p>${note.content}</p>
            <div class="metadata">
                Created: ${new Date(note.created_at).toLocaleString()}<br>
                Updated: ${new Date(note.updated_at).toLocaleString()}
            </div>
            <div class="actions">
                <button class="edit" onclick="editNote(${note.id})">Edit</button>
                <button class="delete" onclick="deleteNote(${note.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Edit note
function editNote(id) {
    const note = notes.find(note => note.id === id);
    noteIdInput.value = note.id;
    noteTitleInput.value = note.title;
    noteContentInput.value = note.content;
    saveButton.textContent = 'Update Note';
    cancelButton.style.display = 'inline-block';
}

// Reset form
function resetForm() {
    noteIdInput.value = '';
    noteTitleInput.value = '';
    noteContentInput.value = '';
    saveButton.textContent = 'Save Note';
    cancelButton.style.display = 'none';
}

// Event Listeners
noteForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const id = parseInt(noteIdInput.value);
    const title = noteTitleInput.value;
    const content = noteContentInput.value;

    if (id) {
        updateNote(id, title, content);
    } else {
        createNote(title, content);
    }
});

cancelButton.addEventListener('click', () => {
    resetForm();
});

searchInput.addEventListener('input', renderNotes);

// Initial load
fetchNotes();
