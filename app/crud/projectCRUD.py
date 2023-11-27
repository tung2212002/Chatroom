from sqlalchemy.orm import Session

from app.core.user import service_user
from app.schema.schema_project import ProjectCreate, ProjectUpdate, ProjectBase
from app.model import Project



def get_all(db: Session):
    return db.query(Project).all()

def get_by_id(id: int, db: Session):
    return db.query(Project).filter(Project.id == id).first()

def get_by_user_id(user_id: int, db: Session):
    return db.query(Project).filter(Project.owner_id == user_id).all()

def get_project_user_collab_by_user_id(user_id: int, db: Session):
    return db.query(Project).filter(Project.collaborators.any(id=user_id)).all()

def get_by_name(name: str, db: Session):
    return db.query(Project).filter(Project.name == name).first()


def create(project: ProjectCreate, user_id: int, db: Session):
    db_project = Project(**project.dict(), owner_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update(id: int, project: ProjectUpdate, db: Session):
    db_project = get_by_id(id, db)
    db_project.name = project.name
    db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    return db_project

def delete(id: int, db: Session):
    db_project = get_by_id(id, db)
    db.delete(db_project)
    db.commit()
    return db_project

