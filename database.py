import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------
# Database Configuration
# ----------------------------

# ✅ Use environment variable or fallback to default
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