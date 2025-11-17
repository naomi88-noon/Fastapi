from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Body, status, Path, HTTPException, Request

from ..models import Todo, User
from ..database import SessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


template = Jinja2Templates(directory="TodoApp/templates")
router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Pydantic schema for request validation
class TodoRequest(BaseModel):
    id: int | None = None   
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool = False

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


# pages
@router.get("/todo-page")
async def render_todo_page(request: Request,db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        todos = db.query(Todo).filter(Todo.owner_id == user.get("id")).all()
        return template.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except:
        return redirect_to_login()
    
@router.get("/add_todo_page")
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        print(f"User in todo-page: {user}")

        if user is None:
            return redirect_to_login()

        return template.TemplateResponse("add_todo.html", {"request": request, "user": user})
    except:
        return redirect_to_login() 
    
    
@router.get("/edit_todo_page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user.get("id")).first()
       
        return redirect_to_login("edit_todo.html", {"request": request, "todo": todo, "user": user})
    except:
        return redirect_to_login()

        


# Endpoints
# GET all todos
@router.get("/todos", status_code=status.HTTP_200_OK)       
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=404, detail="Authentication failed!")
    return db.query(Todo).all()

# GET a single todo by ID
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(..., gt=0)
):
    if user is None:
        raise HTTPException(status_code=404, detail="Authentication failed!")
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found!")

# CREATE a new todo
@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_request: TodoRequest,
    db: db_dependency,
    user: user_dependency
):
    print(f"User: {user}")
    if user is None:
        raise HTTPException(status_code=404, detail="Authentication failed!")
    todo_model = Todo(**todo_request.dict(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

# UPDATE an existing todo
@router.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(
    todo_id: Annotated[int, Path(..., gt=0)],
    todo_request: Annotated[TodoRequest, Body(...)],
    user: user_dependency,
    db: db_dependency
):
    print(f"User: {user}")
    
    if user is None:
        raise HTTPException(status_code=404, detail="Authentication failed!")
    todo_model = db.query(Todo).filter(
        Todo.id == todo_id, Todo.owner_id == user.get("id")
    ).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found!")

    # Update fields
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

# DELETE a todo
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(..., gt=0)
):
    if user is None:
        raise HTTPException(status_code=404, detail="Authentication failed!")
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()