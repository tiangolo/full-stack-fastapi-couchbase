from fastapi import APIRouter, Depends

from app import crud
from app.api.utils.security import get_current_active_superuser
from app.models.role import RoleEnum, Roles
from app.models.user import UserInDB

router = APIRouter()


@router.get("/", response_model=Roles)
def read_roles(current_user: UserInDB = Depends(get_current_active_superuser)):
    """
    Retrieve roles.
    """
    roles = crud.utils.ensure_enums_to_strs(RoleEnum)
    return {"roles": roles}
