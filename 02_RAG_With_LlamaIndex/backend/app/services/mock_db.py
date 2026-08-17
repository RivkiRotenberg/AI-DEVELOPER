from typing import List, Dict, Optional
from ..schemas.task import Task, TaskCreate

# This is a mock database implemented as an in-memory dictionary.
# In a real application, this would be replaced with a database connection (e.g., SQLAlchemy).
MOCK_TASKS: Dict[int, Dict] = {
    1: {
        "id": 1,
        "title": "Initial project setup",
        "description": "Create the initial project structure and documentation.",
        "priority": "high",
        "status": "completed",
        "project_id": 1,
        "assignee_id": 1,
    },
    2: {
        "id": 2,
        "title": "Design API endpoints",
        "description": "Define the RESTful API endpoints in architecture-plan.md.",
        "priority": "medium",
        "status": "in_progress",
        "project_id": 1,
        "assignee_id": None,
    },
}

class MockTaskService:
    """
    A mock service to simulate database operations for tasks.
    """
    def __init__(self):
        self.tasks = MOCK_TASKS
        self.next_id = len(self.tasks) + 1

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieves a single task by its ID."""
        if task_id in self.tasks:
            return Task(**self.tasks[task_id])
        return None

    def get_tasks(self) -> List[Task]:
        """Retrieves a list of all tasks."""
        return [Task(**task) for task in self.tasks.values()]

    def create_task(self, task_data: TaskCreate) -> Task:
        """Creates a new task and adds it to the mock database."""
        new_task_id = self.next_id
        new_task = Task(id=new_task_id, **task_data.dict())
        self.tasks[new_task_id] = new_task.dict()
        self.next_id += 1
        return new_task

# Instantiate the service for the router to use
task_service = MockTaskService()
