from fastapi import FastAPI, Request
from . import models
from .database import engine
from .router import auth, todos, admin,user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
origins = [
    "http://localhost:3000",  # frontend URL
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="Todoapp/templates")


app.mount("/static", StaticFiles(directory="Todoapp/static"), name="static")


@app.get("/")
def test(Request: Request):
    
    return templates.TemplateResponse("home.html", {"request": Request})


@app.get("/healthy")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)
