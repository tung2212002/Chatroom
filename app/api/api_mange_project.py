from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.db.base import get_db
from app.crud import projectCRUD
from app.helper.enum import constant
from app.core.project import service_project
from app.core.auth.service_auth import get_current_user
from app.schema.schema_user import User


router = APIRouter()


@router.get("")
@router.post("")
@router.put("")
@router.delete("")
def handle(
    request: Request,
    data: dict = {},
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    args = {item[0]: item[1] for item in request.query_params.multi_items()}
    if request.method == "GET":
        id = args.get("id", None)
        user_id = args.get("user_id", None)
        collab = args.get("collab", False)
        if user_id and collab:
            status, status_code, response = service_project.get_project_user_collab_by_user_id(user_id, db)
        elif user_id:
            status, status_code, response = service_project.get_project_by_user_id(user_id, db)
        elif id:
            status, status_code, response = service_project.get_collaborators_by_project_id(id, db)
    elif request.method == "POST":
        id = args.get("id", None)
        status, status_code, response = service_project.add_user_to_project(
            {**args, **data}, id, current_user, db
        )
    elif request.method == "DELETE":
        id = args.get("id", None)
        status, status_code, response = service_project.remove_user_from_project({**args, **data}, id, current_user, db)

    if status == constant.ERROR:
        raise HTTPException(status_code=status_code, detail=response)
    elif status == constant.SUCCESS:
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(response)
        )
