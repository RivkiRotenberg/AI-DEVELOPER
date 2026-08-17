from fastapi import FastAPI
from .routers import tasks

app = FastAPI(
    title="Task and Team Management API",
    description="A modern, lightweight API for managing tasks and teams.",
    version="0.1.0",
)

app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"message": "Welcome to the Task and Team Management API!"}
