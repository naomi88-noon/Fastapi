# from  utils import SessionTesting
# from ..router.admin import get_db, get_current_user, override_get_current_user
# import os
# from ..main import app
# from fastapi.testclient import TestClient
# from fastapi import status


# def override_get_db():
#     db = SessionTesting()  # your test session
#     try:
#         yield db
#     finally:
#         db.close()

# app.dependency_overrides[get_db] = override_get_db
# app.dependency_overrides[get_current_user] = override_get_current_user

# def test_admin_read_all_authentication(test_todo):
#     response = client.get('/admin/todos/')
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == [{'completed':0, 'description':'This is a test todo item', 'id':19, 'owner_id':1, 'priority':3, 'title':'Test Todo'}]