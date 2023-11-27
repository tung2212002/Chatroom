from pydantic import BaseModel, ConfigDict, Field, validator

# from app.model.user import User

class ProjectBase(BaseModel):
    name: str
    description: str = None

    @validator("name")
    def name_alphanumeric(cls, v):
        if len(v) < 8:
            raise ValueError("name must be at least 8 characters")
        return v

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    model_config = ConfigDict(from_attribute=True)

    id: int
    owner_id: int

    