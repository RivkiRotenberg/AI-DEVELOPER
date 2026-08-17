from typing import Optional
from pydantic import BaseModel
from datetime import date

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"

class TaskCreate(TaskBase):
    project_id: int

class Task(TaskBase):
    id: int
    project_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None

    class Config:
        orm_mode = True
