from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    emails = Column(String(100), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    hashed_password = Column(String(200))
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user")
    # phone_number = Column(String(20), nullable=True)

    # Relationship to Todo
    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String(20), default="low")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
  
    # Relationship to User
    owner = relationship("User", back_populates="todos")