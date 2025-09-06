from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_notes(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(models.Note)
    if search:
        query = query.filter(models.Note.title.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def get_note(db: Session, note_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id).first()

def create_note(db: Session, note: schemas.NoteCreate):
    db_note = models.Note(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, note_id: int, note: schemas.NoteUpdate):
    db_note = get_note(db, note_id)
    if db_note:
        update_data = note.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_note, key, value)
        db_note.updated_at = datetime.now()
        db.commit()
        db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int):
    db_note = get_note(db, note_id)
    if db_note:
        db.delete(db_note)
        db.commit()
        return True
    return False