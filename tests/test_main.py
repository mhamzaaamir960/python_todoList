from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session
from todo_list.main import app, get_session
from todo_list import settings
import pytest



connection_string = str(settings.TEST_DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={"sslmode": "require"}, pool_recycle=300,pool_size=10, echo=True)


def test_create_tables():
    SQLModel.metadata.create_all(engine)


def test_status():
    client = TestClient(app=app)
    response = client.get('/')
    data = response.json()
    assert response.status_code == 200
    assert data == {"message": "Welcome to todo app!"}

def test_create_todo():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def db_session_overide():
            return session
    app.dependency_overrides[get_session] = db_session_overide
    client = TestClient(app=app)

    test_todo = {"content" : "test create todo","is_completed" : False}
    response = client.post('/todos/', json=test_todo)
    data = response.json()
    assert response.status_code == 200
    assert data["content"]  == test_todo["content"] 





