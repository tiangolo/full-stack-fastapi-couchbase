from typing import List, Optional, Union
from app.models.base import CustomBaseModel
from app.models.role import RoleEnum
from app.models.config import USERPROFILE_DOC_TYPE

# Shared properties
class UserBase(CustomBaseModel):
    name: str
    email: Optional[str] = None
    admin_roles: Optional[List[Union[str, RoleEnum]]] = None
    admin_channels: Optional[List[Union[str, RoleEnum]]] = None
    disabled: Optional[bool] = None


class UserBaseStore(UserBase):
    human_name: Optional[str] = None

# Additional properties to receive via API
class UserInCreate(UserBaseStore):
    password: str
    
    admin_roles: List[Union[str, RoleEnum]] = []
    admin_channels: List[Union[str, RoleEnum]] = []
    disabled: bool = False


class UserInUpdate(UserBaseStore):
    password: Optional[str] = None


# Additional properties to return via API
class UserOut(UserBaseStore):
    pass

# Additional properties stored in DB
class UserStored(UserBaseStore):
    type: str = USERPROFILE_DOC_TYPE
    hashed_password: str

    class Meta:
        key: Optional[str] = None


class UserSyncIn(UserBase):
    password: Optional[str] = None
