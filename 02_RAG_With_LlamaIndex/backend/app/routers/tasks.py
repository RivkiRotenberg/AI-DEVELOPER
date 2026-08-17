from typing import List
from fastapi import APIRouter, HTTPException

from ..schemas.task import Task, TaskCreate
from ..services.mock_db import task_service

router = APIRouter()

@router.post("/tasks/", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    """
    Create a new task.
    """
    new_task = task_service.create_task(task)
    return new_task

@router.get("/tasks/", response_model=List[Task])
def read_tasks():
    """
    Retrieve all tasks.
    """
    return task_service.get_tasks()

@router.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int):
    """
    Retrieve a single task by its ID.
    """
    db_task = task_service.get_task(task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
