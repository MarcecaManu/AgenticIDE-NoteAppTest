const API_URL = 'http://localhost:8000/api/notes';

// State
let notes = [];
let editingNoteId = null;

// DOM Elements
const noteList = document.getElementById('noteList');
const noteForm = document.querySelector('.note-form');
const noteIdInput = document.getElementById('noteId');
const noteTitleInput = document.getElementById('noteTitle');
const noteContentInput = document.getElementById('noteContent');
const formTitle = document.getElementById('formTitle');
const cancelButton = document.getElementById('cancelButton');
const searchBar = document.getElementById('searchBar');

// Load notes on page load
document.addEventListener('DOMContentLoaded', loadNotes);

// Search functionality
searchBar.addEventListener('input', filterNotes);

async function loadNotes() {
    try {
        const response = await fetch(API_URL);
        notes = await response.json();
        renderNotes();
    } catch (error) {
        console.error('Error loading notes:', error);
    }
}

function renderNotes() {
    const filteredNotes = filterNotesBySearch();
    noteList.innerHTML = filteredNotes.map(note => `
        <div class="note-item">
            <h3>${note.title}</h3>
            <p>${note.content}</p>
            <div class="note-controls">
                <button onclick="editNote(${note.id})">Edit</button>
                <button onclick="deleteNote(${note.id})">Delete</button>
            </div>
            <small>Created: ${new Date(note.created_at).toLocaleString()}</small>
            <br>
            <small>Updated: ${new Date(note.updated_at).toLocaleString()}</small>
        </div>
    `).join('');
}

function filterNotes() {
    renderNotes();
}

function filterNotesBySearch() {
    const searchTerm = searchBar.value.toLowerCase();
    return notes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );
}

async function saveNote(event) {
    event.preventDefault();
    const title = noteTitleInput.value.trim();
    const content = noteContentInput.value.trim();
    
    if (!title || !content) {
        alert('Please fill in both title and content');
        return;
    }

    try {
        const noteData = { title, content };
        const url = editingNoteId ? `${API_URL}/${editingNoteId}` : API_URL;
        const method = editingNoteId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(noteData),
        });

        if (!response.ok) {
            throw new Error('Failed to save note');
        }

        const savedNote = await response.json();
        
        if (editingNoteId) {
            notes = notes.map(note => 
                note.id === editingNoteId ? savedNote : note
            );
        } else {
            notes.push(savedNote);
        }

        resetForm();
        renderNotes();
    } catch (error) {
        console.error('Error saving note:', error);
        alert('Failed to save note');
    }
}

function editNote(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        editingNoteId = id;
        noteTitleInput.value = note.title;
        noteContentInput.value = note.content;
        formTitle.textContent = 'Edit Note';
        cancelButton.style.display = 'inline';
    }
}

async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Failed to delete note');
        }

        notes = notes.filter(note => note.id !== id);
        renderNotes();
    } catch (error) {
        console.error('Error deleting note:', error);
        alert('Failed to delete note');
    }
}

function resetForm() {
    editingNoteId = null;
    noteIdInput.value = '';
    noteTitleInput.value = '';
    noteContentInput.value = '';
    formTitle.textContent = 'Create New Note';
    cancelButton.style.display = 'none';
}

// Add form submit event listener
noteForm.addEventListener('submit', saveNote);

// Add cancel button event listener
cancelButton.addEventListener('click', resetForm);