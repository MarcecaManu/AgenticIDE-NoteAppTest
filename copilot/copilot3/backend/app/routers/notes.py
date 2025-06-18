from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..models.note import Note

router = APIRouter()

@router.get("/api/notes/", response_model=List[dict])
def get_notes(db: Session = Depends(get_db)):
    notes = db.query(Note).all()
    return [{"id": note.id, "title": note.title, "content": note.content, 
             "created_at": note.created_at, "updated_at": note.updated_at} 
            for note in notes]

@router.get("/api/notes/{note_id}", response_model=dict)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"id": note.id, "title": note.title, "content": note.content,
            "created_at": note.created_at, "updated_at": note.updated_at}

@router.post("/api/notes/", response_model=dict)
def create_note(note: dict, db: Session = Depends(get_db)):
    db_note = Note(title=note["title"], content=note["content"])
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return {"id": db_note.id, "title": db_note.title, "content": db_note.content,
            "created_at": db_note.created_at, "updated_at": db_note.updated_at}

@router.put("/api/notes/{note_id}", response_model=dict)
def update_note(note_id: int, note: dict, db: Session = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.title = note["title"]
    db_note.content = note["content"]
    db.commit()
    db.refresh(db_note)
    return {"id": db_note.id, "title": db_note.title, "content": db_note.content,
            "created_at": db_note.created_at, "updated_at": db_note.updated_at}

@router.delete("/api/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully"}