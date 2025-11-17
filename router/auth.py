from fastapi import APIRouter, Depends, status, HTTPException, Request
from pydantic import BaseModel
from ..models import User
from passlib.context import CryptContext
from ..database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates

# -----------------------------
# Router setup
# -----------------------------
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# -----------------------------
# Pydantic Models
# -----------------------------
class CreateUserRequest(BaseModel):
    username: str
    emails: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# -----------------------------
# Security Setup
# -----------------------------
SECRET_KEY = '1934abcd5678efgh9012ijk8l3456mnop7890qrstuvwx1234yzab5678cdef9012'
ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# -----------------------------
# Helper functions for bcrypt
# -----------------------------
def hash_password(password: str) -> str:
    # Truncate to 72 bytes to avoid bcrypt ValueError
    return bcrypt_context.hash(password[:72])

def verify_password(password: str, hashed: str) -> bool:
    # Truncate to 72 bytes when verifying
    return bcrypt_context.verify(password[:72], hashed)

# -----------------------------
# Database dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# -----------------------------
# Templates
# -----------------------------
templates = Jinja2Templates(directory="Todoapp/templates")  # corrected folder name

# -----------------------------
# Pages
# -----------------------------
@router.get("/login")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# -----------------------------
# Authentication Utility Functions
# -----------------------------
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):  # ✅ fixed
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expire_delta: timedelta):
    payload = {
        "sub": username,
        "id": user_id,
        "role": role,
        "exp": datetime.utcnow() + expire_delta
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return {"username": username, "id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# -----------------------------
# Routes
# -----------------------------
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == create_user_request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    new_user = User(
        emails=create_user_request.emails,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=hash_password(create_user_request.password),  # ✅ fixed
        is_active=True,
        # phone_number=create_user_request.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User '{new_user.username}' created successfully."}


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Create JWT token
    access_token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expire_delta=timedelta(minutes=30)
    )

    return {"access_token": access_token, "token_type": "bearer"}