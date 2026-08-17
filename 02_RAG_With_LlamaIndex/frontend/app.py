
import gradio as gr
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.mock_db import MockTaskService
from backend.app.schemas.task import TaskCreate

# Initialize services
task_service = MockTaskService()

# Mock team members for now
mock_team_members = {1: "Alice", 2: "Bob", 3: "Charlie"}

def get_tasks_df():
    """Retrieves tasks and formats them for display."""
    tasks = task_service.get_tasks()
    if not tasks:
        return None
    
    task_list = []
    for task in tasks:
        assignee_name = mock_team_members.get(task.assignee_id, "Unassigned")
        task_list.append([
            task.id,
            task.title,
            task.description,
            task.status,
            assignee_name
        ])
    return task_list

def add_task(title, description, priority, status, assignee_name):
    """Adds a new task."""
    assignee_id = None
    for id, name in mock_team_members.items():
        if name == assignee_name:
            assignee_id = id
            break
            
    task_data = TaskCreate(
        title=title,
        description=description,
        priority=priority,
        status=status,
        project_id=1,  # Mock project_id
        assignee_id=assignee_id
    )
    task_service.create_task(task_data)
    return get_tasks_df()

def update_task_status(task_id, status):
    """Updates a task's status."""
    task_id = int(task_id)
    if task_id in task_service.tasks:
        task_service.tasks[task_id]['status'] = status
        return get_tasks_df(), f"Task {task_id} status updated to {status}."
    return get_tasks_df(), f"Task {task_id} not found."

def get_team_members_list():
    """Returns a list of team members."""
    return [[name] for name in mock_team_members.values()]

def add_team_member(name):
    """Adds a new team member."""
    if name and name not in mock_team_members.values():
        new_id = max(mock_team_members.keys()) + 1
        mock_team_members[new_id] = name
        return get_team_members_list(), f"Team member '{name}' added."
    return get_team_members_list(), f"'{name}' is already a team member or invalid."

with gr.Blocks(theme=gr.themes.Soft(), title="Project Dashboard") as demo:
    gr.Markdown("# Project Management Dashboard")

    with gr.Tabs():
        with gr.TabItem("Task Management"):
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("### All Tasks")
                    task_list_df = gr.DataFrame(
                        headers=["ID", "Title", "Description", "Status", "Assignee"],
                        value=get_tasks_df,
                        interactive=False,
                        row_count=(10, "dynamic")
                    )
                with gr.Column(scale=2):
                    with gr.Accordion("Add New Task", open=False):
                        task_title = gr.Textbox(label="Title")
                        task_desc = gr.Textbox(label="Description", lines=3)
                        task_priority = gr.Dropdown(["low", "medium", "high"], label="Priority", value="medium")
                        task_status_add = gr.Dropdown(["pending", "in_progress", "completed"], label="Status", value="pending")
                        task_assignee = gr.Dropdown(list(mock_team_members.values()), label="Assignee")
                        add_task_btn = gr.Button("Add Task", variant="primary")
                    
                    with gr.Accordion("Update Task Status", open=False):
                        task_ids = [str(t.id) for t in task_service.get_tasks()]
                        update_task_id = gr.Dropdown(task_ids, label="Select Task ID")
                        update_task_status_val = gr.Dropdown(["pending", "in_progress", "completed"], label="New Status")
                        update_task_btn = gr.Button("Update Status", variant="primary")
                        update_status_msg = gr.Textbox(label="Result", interactive=False)


        with gr.TabItem("Team Members"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Current Team")
                    team_list_df = gr.DataFrame(
                        headers=["Name"],
                        value=get_team_members_list,
                        interactive=False
                    )
                with gr.Column():
                    gr.Markdown("### Add New Member")
                    new_member_name = gr.Textbox(label="Member Name")
                    add_member_btn = gr.Button("Add Member", variant="primary")
                    add_member_status = gr.Textbox(label="Status", interactive=False)

    # Event Handlers
    add_task_btn.click(
        fn=add_task,
        inputs=[task_title, task_desc, task_priority, task_status_add, task_assignee],
        outputs=[task_list_df]
    )

    update_task_btn.click(
        fn=update_task_status,
        inputs=[update_task_id, update_task_status_val],
        outputs=[task_list_df, update_status_msg]
    )
    
    add_member_btn.click(
        fn=add_team_member,
        inputs=[new_member_name],
        outputs=[team_list_df, add_member_status]
    ).then(
        # This is a bit of a hack to update the assignee dropdown on the other tab
        lambda: gr.Dropdown(choices=list(mock_team_members.values())),
        None,
        [task_assignee]
    )


if __name__ == "__main__":
    demo.launch()
