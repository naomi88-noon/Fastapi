import os
from sqlalchemy import String, create_engine, text
from sqlalchemy.orm import sessionmaker
from ..database import Base, get_db
from ..main import app
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from ..models import Todo
from fastapi import status
from numbers import Number
import pytest
from .utils import *
from sqlalchemy.orm import declarative_base





SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:noon8899@localhost:3306/todoApplicationDatabase1"
)

# ✅ Create the engine with recommended options
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,          # Avoid dropped connections
    echo=False,                  # Set to True for SQL logging
    connect_args={},             # For MySQL, usually empty (used for SQLite)
)

# ✅ Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Base class for ORM models
Base = declarative_base()

# ----------------------------
# Dependency for FastAPI routes
# ----------------------------
def get_db():
    """Dependency that provides a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def override_get_current_user():
  
    
    
 client = TestClient(app)
@pytest.fixture()
def test_todo():
    todo = Todo(
        title="Test Todo",
        description="This is a test todo item",
        priority=3,
        completed=False,
        owner_id=1
    )
    
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield
    
