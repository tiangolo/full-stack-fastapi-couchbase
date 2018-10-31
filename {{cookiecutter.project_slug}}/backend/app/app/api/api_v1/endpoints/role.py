# Import standard library modules

# Import installed modules
# # Import installed packages
from flask import abort
from flask_apispec import doc, marshal_with
from flask_jwt_extended import get_current_user, jwt_required

# Import app code
from app.main import app
from app.api.api_v1.api_docs import docs, security_params
from app.core import config
from app.models.role import RoleEnum
from app.crud.utils import ensure_enums_to_strs
from app.crud.user import (
    check_if_user_is_active,
    check_if_user_is_admin,
    check_if_user_is_superuser,
)

# Import Schemas
from app.schemas.role import RolesSchema


@docs.register
@doc(description="Retrieve roles", security=security_params, tags=["roles"])
@app.route(f"{config.API_V1_STR}/roles/", methods=["GET"])
@marshal_with(RolesSchema())
@jwt_required
def route_roles_get():
    current_user = get_current_user()
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not (
        check_if_user_is_admin(current_user) or check_if_user_is_superuser(current_user)
    ):
        abort(400, "The current user does not have enogh privileges")
    roles = ensure_enums_to_strs(RoleEnum)
    return {"roles": roles}
