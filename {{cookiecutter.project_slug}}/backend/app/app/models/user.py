from typing import List, overload
from app.models.base import CustomBaseModel
from app.models.role import RoleEnum
from app.models.config import USERPROFILE_DOC_TYPE

class User(CustomBaseModel):
    type: str = USERPROFILE_DOC_TYPE
    name: str
    password: str
    human_name: str = None
    email: str = None
    admin_roles: List[RoleEnum] = []
    admin_channels: List[str] = []
    disabled: bool = False

    class Meta:
        key: str = None
    
    def __init__(
        self,
        *,
        type=USERPROFILE_DOC_TYPE,
        name: str,
        password: str,
        human_name: str = None,
        email: str = None,
        admin_roles: List[RoleEnum] = [],
        admin_channels: List[str] = [],
        disabled: bool = False,
    ):
        super().__init__(
            type=type,
            name=name,
            password=password,
            human_name=human_name,
            email=email,
            admin_roles=admin_roles,
            admin_channels=admin_channels,
            disabled=disabled,
        )
