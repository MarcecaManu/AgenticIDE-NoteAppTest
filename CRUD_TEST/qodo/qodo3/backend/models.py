from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import os

Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Get the absolute path to the database file
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'notes.db'))
DATABASE_URL = f"sqlite:///{db_path}"

# Create the engine with the correct path
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

def init_db():
    """Initialize the database and create all tables."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

# Initialize the database when this module is imported
init_db()
