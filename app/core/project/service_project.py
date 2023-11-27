from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.base import get_db
from app.crud import projectCRUD, userCRUD
from app.helper.enum import constant
from app.schema.schema_project import ProjectCreate, ProjectUpdate
from app.schema.schema_user import UserBase, User


def get_all_project(db: Session):
    db_projects = projectCRUD.get_all(db)
    if db_projects is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    for db_project in db_projects:
        owner = userCRUD.get_by_id(db_project.owner_id, db)
        if owner is None:
            return constant.ERROR, 404, {"message": "Owner not found"}
        response = db_project
        owner = User(**owner.__dict__)
        response.owner = owner
    return constant.SUCCESS, 200, db_projects

def get_project_user_collab_by_user_id(user_id: int, db: Session):
    user = userCRUD.get_by_id(user_id, db)
    if user is None:
        return constant.ERROR, 404, {"message": "User not found"}
    db_projects = projectCRUD.get_project_user_collab_by_user_id(user_id, db)
    if db_projects is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    response = db_projects
    return constant.SUCCESS, 200, response


def get_project_by_id(id: int, db: Session):
    db_project = projectCRUD.get_by_id(id, db)
    if db_project is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    owner = userCRUD.get_by_id(db_project.owner_id, db)
    if owner is None:
        return constant.ERROR, 404, {"message": "Owner not found"}
    response = db_project
    owner = User(**owner.__dict__)
    response.owner = owner
    return constant.SUCCESS, 200, db_project

def get_collaborators_by_project_id(id: int, db: Session):
    db_project = projectCRUD.get_by_id(id, db)
    if db_project is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    collaborators = db_project.collaborators
    if collaborators is None:
        return constant.ERROR, 404, {"message": "Collaborators not found"}
    # response = collaborators
    response = [UserBase(**collaborator.__dict__) for collaborator in collaborators]
    return constant.SUCCESS, 200, response


def get_project_by_user_id(user_id: int, db: Session):
    user = userCRUD.get_by_id(user_id, db)
    if user is None:
        return constant.ERROR, 404, {"message": "User not found"}
    db_projects = projectCRUD.get_by_user_id(user_id, db)
    if db_projects is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    response = db_projects
    return constant.SUCCESS, 200, response


def create_project(data: dict, user_id: int, db: Session):
    try:
        project = ProjectCreate(**data)
    except Exception as e:
        error = [f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()]
        return constant.ERROR, 400, error
    db_project = projectCRUD.get_by_name(data.get("name"), db)
    if db_project is not None:
        return constant.ERROR, 400, {"message": "Project already exist"}
    db_project = projectCRUD.create(project, user_id, db)
    return constant.SUCCESS, 201, db_project


def update_project(data: dict, current_user, id: int, db: Session):
    if current_user is None:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    try:
        project = ProjectUpdate(**data)
    except Exception as e:
        error = [f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()]
        return constant.ERROR, 400, error
    db_project = projectCRUD.get_by_id(id, db)
    if db_project is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    if db_project.owner_id != current_user.id:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_project = projectCRUD.update(id, project, db)
    return constant.SUCCESS, 200, db_project


def delete_project(current_user, id: int, db: Session):
    if current_user is None:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_project = projectCRUD.get_by_id(id, db)
    if db_project is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    if db_project.owner_id != current_user.id:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_project = projectCRUD.delete(id, db)
    return constant.SUCCESS, 200, {"message": "Delete project successfully"}


def add_user_to_project(data: dict, id: int, current_user, db: Session):
    if current_user is None:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_project = projectCRUD.get_by_id(id, db)
    collaborators = db_project.collaborators

    if db_project is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    if db_project.owner_id != current_user.id:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    collaborators_list = data.get("username", [])
    user = userCRUD.get_by_username(collaborators_list, db)
    if user is None:
        return constant.ERROR, 404, {"message": "User not found"}
    if user.id == db_project.owner_id:
        return constant.ERROR, 400, {"message": "Cannot add owner to collaborators"}
    if user in collaborators:
        return constant.ERROR, 400, {"message": "User already in collaborators"}
    db_project.collaborators.append(user)
    db.commit()
    db.refresh(db_project)
    print(user.id)
    user = User(**user.__dict__)
    response = constant.SUCCESS, 200, user
    return response


def remove_user_from_project(data: dict, id: int, current_user, db: Session):
    db_project = projectCRUD.get_by_id(id, db)
    if db_project is None:
        return constant.ERROR, 404, {"message": "Project not found"}
    if db_project.owner_id != current_user.id:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    collaborators_list = data.get("username", [])
    user = userCRUD.get_by_username(collaborators_list, db)
    if user is None:
            return constant.ERROR, 404, {"message": "User not found"}
    if current_user.id == user.id:
            return (
                constant.ERROR,
                400,
                {"message": "Cannot remove owner from collaborators"},
            )
    if user not in db_project.collaborators:
            return constant.ERROR, 400, {"message": "User not in collaborators"}
    db_project.collaborators.remove(user)
    db.commit()
    db.refresh(db_project)
    return constant.SUCCESS, 200, {"message": "Remove user from project successfully"}
