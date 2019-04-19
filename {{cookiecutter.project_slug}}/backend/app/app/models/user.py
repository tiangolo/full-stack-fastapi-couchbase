from typing import List, Optional, Union

from pydantic import BaseModel

from app.models.config import USERPROFILE_DOC_TYPE
from app.models.role import RoleEnum


# Shared properties in Couchbase and Sync Gateway
class UserBase(BaseModel):
    email: Optional[str] = None
    admin_roles: Optional[List[Union[str, RoleEnum]]] = None
    admin_channels: Optional[List[Union[str, RoleEnum]]] = None
    disabled: Optional[bool] = None


# Shared properties in Couchbase
class UserBaseInDB(UserBase):
    username: Optional[str] = None
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBaseInDB):
    username: str
    password: str
    admin_roles: List[Union[str, RoleEnum]] = []
    admin_channels: List[Union[str, RoleEnum]] = []
    disabled: bool = False


# Properties to receive via API on update
class UserUpdate(UserBaseInDB):
    password: Optional[str] = None


# Additional properties to return via API
class User(UserBaseInDB):
    pass


# Additional properties stored in DB
class UserInDB(UserBaseInDB):
    type: str = USERPROFILE_DOC_TYPE
    hashed_password: str
    username: str


# Additional properties in Sync Gateway
class UserSyncIn(UserBase):
    name: str
    password: Optional[str] = None
