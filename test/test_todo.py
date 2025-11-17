from numbers import Number
from fastapi.testclient import TestClient
from sqlalchemy import String, create_engine, text
from sqlalchemy.orm import sessionmaker
from ..database import Base, get_db
from ..main import app
from ..router.todos import get_current_user
import pytest
from ..models import Todo
from fastapi import status

# ----------------------------
# 1. Configure a test database
# ----------------------------
# Use a separate database for testing
SQLALCHEMY_TEST_DATABASE_URL = "mysql+pymysql://root:noon8899@localhost:3306/todoapplicationdatabase1"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables for testing
Base.metadata.create_all(bind=engine)

# ----------------------------
# 2. Override dependencies
# ----------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    # Return a fake admin user
    return {"id": 1, "username": "Njang Naomi", "role": "admin"}

# Apply overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# ----------------------------
# 3. TestClient instance
# ----------------------------
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
    
    # with engine.begin() as connection:
    #     connection.execute(text("DELETE FROM todos"))

# ----------------------------
# 4. Example test
# ----------------------------
def test_read_all_authentication(test_todo):
    response = client.get("/todos/todos/")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert isinstance(data, list)
    
def test_read_one_authentication(test_todo):
    response = client.get("/todos/todo/20")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data



def test_read_one_authenticated_not_found():
    response = client.get('/todos/todo/999')
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found!"}
    
def test_creat_todo():
    request_data = {
        
        'title': 'new todo!',
        'description': 'new todo description',
        'priority':'3',
        'completed':False
    }
    
    response = client.post('/todos/todos', json=request_data)
    assert response.status_code == 201
    
    
    # db = TestingSessionLocal()
    # model = db.query(Todo).filter(Todo.id == 15).first()
    # assert model.title == request_data('title')
    # assert model.description == request_data('description')
    # assert model.priority == request_data('priority')
    # assert model.completed == request_data('completed')
    
    
def test_update_todo(test_todo):
    request_data = {
        'title': 'updated todo!',
        'description': 'updated todo description',
        'priority':'5',
        'completed':True
    }
    
    create_response = client.post("todos/todos", json=request_data)
    json = create_response.json()
    todo_id = json['id']
    
    # 2. Update the todo
    update_data = {
        "title": "Updated title",
        "description": "Updated desc",
        "priority": 2,
        "owner_id":1
    }
    response = client.put(f"/todos/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    
    
def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'updated todo!',
        'description': 'updated todo description',
        'priority':'5',
        'completed':True
    }
    
    create_response = client.post("/todos/todos", json=request_data)
    json = create_response.json()
    todo_id = json['id']
    
    
    update_data = {
        "title": "Updated title",
        "description": "Updated desc",
        "priority": 2,
        "owner_id":1
    }
    response = client.put(f"/todos/todos/999", json=update_data)
    print(response.json())
    assert response.status_code == 404
    
    assert response.json() == {"detail": "Todo not found!"}
    
# def test_delete_todo(test_todo):
#     response = client.delete("/todo/18")
#     assert response.status_code == 204
#     db = TestingSessionLocal()
#     try:
#         model = db.query(Todo).filter(Todo.id == 18).first()
#     finally:
#         db.close()
#     assert model is None

