from app.core.config import ROLE_SUPERUSER

from enum import Enum


class RoleEnum(Enum):
    superuser = ROLE_SUPERUSER
    admin = "admin"
