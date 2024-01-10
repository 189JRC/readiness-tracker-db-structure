import os
from website import db, create_app
from website.models import (
    User,
    Organisation,
    OrganisationHeirarchy,
    User_Organisation,
    OrganisationOrganisation,
    Project,
    ProjectOrganisation,
    Task,
    TaskStatus,
    TaskProgress,
    BlockedSuggestions,
    Email,
    EmailsSent,
)

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError, DataError
from faker import Faker
import random

fake = Faker()

# Create the Flask app
app = create_app()


def get_user_projects(user_id, org_id):
    user_project_info = (
        db.session.query(User.name, Project.name)
        .join(User_Organisation, User.id == User_Organisation.user_id)
        .join(
            ProjectOrganisation,
            User_Organisation.organisation_id == ProjectOrganisation.organisation_id,
        )
        .join(Project, ProjectOrganisation.project_id == Project.id)
        .filter(User.id == user_id)
        .first()
    )
    if user_project_info:
        user_name, project_name = user_project_info
        print(f"{user_name} has got {project_name}")
    else:
        print("User not found or not associated with a project")

    get_project_tasks(project_name, org_id)


def get_project_tasks(project_name, org_id):
    # project_tasks_info = (
    #     db.session.query(Task.name).join(Project, Project.name == project_name).all()
    # )
    project_tasks_info = (
        db.session.query(Task)
        .join(Project, Task.project_id == Project.id)
        .filter(Project.name == project_name)
        .all()
    )
    for task in project_tasks_info:
        print(task.name)

    get_task_progress(project_tasks_info[0].id, org_id)
    return


def get_task_progress(task_id, org_id):
    task_progress_info = (
        db.session.query(TaskProgress)
        .join(Task, Task.id == TaskProgress.task_id)
        .join(Organisation, Organisation.id == TaskProgress.organisation_id)
        .filter(Task.id == task_id)
        .filter(Organisation.id == org_id)
        .first()
    )

    if task_progress_info:
        task_status_id = task_progress_info.task_status_id
        print(
            f"Task Status ID for Task {task_id} in Organisation {org_id}: {task_status_id}"
        )
    else:
        print(
            f"No task progress information found for Task {task_id} in Organisation {org_id}"
        )

    return task_progress_info


if __name__ == "__main__":
    with app.app_context():
        get_user_projects(user_id=902, org_id=4774)
