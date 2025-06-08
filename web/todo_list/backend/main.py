from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

app = FastAPI()

# Enable CORS so your React frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Todo model for the API
class Todo(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    due_date: Optional[str] = None
    created_at: str
    completed: bool = False

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    due_date: Optional[str] = None

# In-memory storage (will reset when server restarts)
todos_db = {}

@app.get("/")
def read_root():
    return {"message": "Todo API is running!"}

@app.get("/todos")
def get_todos():
    return {"todos": list(todos_db.values())}

@app.post("/todos")
def create_todo(todo: TodoCreate):
    todo_id = str(uuid.uuid4())
    new_todo = Todo(
        id=todo_id,
        title=todo.title,
        description=todo.description,
        due_date=todo.due_date,
        created_at=datetime.now().isoformat(),
        completed=False
    )
    todos_db[todo_id] = new_todo.dict()
    return new_todo

@app.get("/todos/{todo_id}")
def get_todo(todo_id: str):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos_db[todo_id]

@app.put("/todos/{todo_id}")
def update_todo(todo_id: str, todo: TodoCreate):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todos_db[todo_id].update({
        "title": todo.title,
        "description": todo.description,
        "due_date": todo.due_date
    })
    return todos_db[todo_id]

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: str):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    deleted_todo = todos_db.pop(todo_id)
    return {"message": "Todo deleted", "todo": deleted_todo}

@app.patch("/todos/{todo_id}/toggle")
def toggle_todo(todo_id: str):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todos_db[todo_id]["completed"] = not todos_db[todo_id]["completed"]
    return todos_db[todo_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)