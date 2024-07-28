from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from todo_list import settings
from typing import Annotated
from contextlib import asynccontextmanager

class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(index=True, min_length=3, max_length=100)
    is_completed: bool = Field(default=False)


connection_string = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={"sslmode": "require"}, pool_recycle=300,pool_size=10, echo=True)

def create_tables():
    SQLModel.metadata.create_all(engine)  

async def get_session():
    with Session(engine) as session:
         yield session

@asynccontextmanager
async def life_span(app: FastAPI):
    create_tables()
    yield

app  : FastAPI = FastAPI(lifespan=life_span, title="Todo App", version='1.0.0')

@app.get('/')
async def status():
    return {"message": "Welcome to todo app!"}

@app.post('/todos/', response_model=Todo)
async def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get('/todos/', response_model=list[Todo])
async def get_todos(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all(), lambda x:x.id
    if todos:
        return todos
    else:
        raise HTTPException(status_code=404, detail="No task found")

@app.get('/todos/{id}', response_model=Todo)
async def get_todo(id: int, session: Annotated[Session, Depends(get_session)]):
    todo = session.exec(select(Todo).where(Todo.id == id)).first()
    if todo:
        return todo
    else:
        raise HTTPException(status_code=404, detail="No task found")

@app.put('/todos/{id}')
async def update_todo(id: int, todo: Todo, session: Annotated[Session, Depends(get_session)]):
    existing_todo = session.exec(select(Todo).where(Todo.id == id)).first()
    if existing_todo:
        existing_todo.content = todo.content
        existing_todo.is_completed = todo.is_completed
        session.add(existing_todo)
        session.commit()
        session.refresh(existing_todo)
        return existing_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found!")

@app.delete('/todos/{id}')
async def delete_todo(id: int, session: Annotated[Session, Depends(get_session)]):
    todo = session.exec(select(Todo).where(Todo.id == id)).first()
    if todo:
        session.delete(todo)
        session.commit()
        session.refresh(todo)
        return {"message": "Task is deleted Successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Todo not found!")
