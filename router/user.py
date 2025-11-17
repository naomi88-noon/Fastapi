from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,Body, status, Path, HTTPException

from ..models import Todo, User
from ..database import SessionLocal, engine, Base
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter( 
    prefix="/user",
    tags=["user"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/",status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
   
    return db.query(Todo).all()



@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, todo_id: int = Path(..., gt=0)):
    
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
    
@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str ):
    if user is None:
         raise HTTPException(status_code=401, detail="Authentication failed!")
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
    