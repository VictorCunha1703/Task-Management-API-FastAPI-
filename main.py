from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Dict
import uvicorn

class Task(BaseModel):
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    completed: bool = False

class TaskRepository:
    def __init__(self):
        self._storage: Dict[int, Task] = {}

    def get_all(self) -> List[Task]:
        return list(self._storage.values())

    def exists(self, task_id: int) -> bool:
        return task_id in self._storage

    def save(self, task: Task) -> None:
        self._storage[task.id] = task

    def delete(self, task_id: int) -> bool:
        if task_id in self._storage:
            del self._storage[task_id]
            return True
        return False

app = FastAPI(
    title="Project Management Service",
    version="1.0.0"
)

db = TaskRepository()

def get_repository() -> TaskRepository:
    return db

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

@app.get("/tasks", response_model=List[Task])
async def list_tasks(repo: TaskRepository = Depends(get_repository)):
    return repo.get_all()

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: Task, repo: TaskRepository = Depends(get_repository)):
    if repo.exists(task.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task ID already registered"
        )
    repo.save(task)
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, repo: TaskRepository = Depends(get_repository)):
    if not repo.delete(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)