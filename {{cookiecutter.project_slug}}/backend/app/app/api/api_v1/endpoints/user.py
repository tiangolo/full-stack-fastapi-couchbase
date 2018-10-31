# Import standard library modules

# Import installed modules
# # Import installed packages
from flask import abort
from webargs import fields
from flask_apispec import doc, use_kwargs, marshal_with
from flask_jwt_extended import get_current_user, jwt_required

# Import app code
from app.main import app
from app.db.bucket import bucket
from app.api.api_v1.api_docs import docs, security_params
from app.core import config
from app.models.user import UserInCreate, UserInUpdate, UserStored
from app.crud.user import (
    check_if_user_is_active,
    check_if_user_is_admin_or_superuser,
    get_user,
    get_users,
    upsert_user,
    update_user,
)


# Import Schemas
from app.schemas.user import UserSchema


@docs.register
@doc(description="Retrieve users", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/", methods=["GET"])
@use_kwargs(
    {"skip": fields.Int(default=0), "limit": fields.Int(default=100)},
    locations=["query"],
)
@marshal_with(UserSchema(many=True))
@jwt_required
def route_users_get(skip=0, limit=100):
    current_user = get_current_user()
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_admin_or_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    users = get_users(bucket, skip=skip, limit=limit)
    return users


@docs.register
@doc(description="Create new user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/", methods=["POST"])
@use_kwargs(
    {
        "name": fields.Str(required=True),
        "password": fields.Str(required=True),
        "admin_channels": fields.List(fields.Str()),
        "admin_roles": fields.List(fields.Str()),
        "disabled": fields.Boolean(),
        "email": fields.Str(),
        "human_name": fields.Str(),
    }
)
@marshal_with(UserSchema())
@jwt_required
def route_users_post(
    *,
    name,
    password,
    admin_channels=[],
    admin_roles=[],
    disabled=False,
    email=None,
    human_name=None,
):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_admin_or_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    user = get_user(bucket, name)
    if user:
        return abort(400, f"The user with this username already exists in the system.")
    user_in = UserInCreate(
        name=name,
        password=password,
        admin_channels=admin_channels,
        admin_roles=admin_roles,
        disabled=disabled,
        email=email,
        human_name=human_name,
    )
    user = upsert_user(bucket, user_in)
    return user


@docs.register
@doc(description="Update a user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/<name>", methods=["PUT"])
@use_kwargs(
    {
        "password": fields.Str(),
        "admin_channels": fields.List(fields.Str()),
        "admin_roles": fields.List(fields.Str()),
        "disabled": fields.Boolean(),
        "email": fields.Str(),
        "human_name": fields.Str(),
    }
)
@marshal_with(UserSchema())
@jwt_required
def route_users_put(
    *,
    name,
    password=None,
    admin_channels=None,
    admin_roles=None,
    disabled=None,
    email=None,
    human_name=None,
):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_admin_or_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    user = get_user(bucket, name)

    if not user:
        return abort(404, f"The user with this username does not exist in the system.")
    user_in = UserInUpdate(
        name=name,
        password=password,
        admin_channels=admin_channels,
        admin_roles=admin_roles,
        disabled=disabled,
        email=email,
        human_name=human_name,
    )
    user = update_user(bucket, user_in)
    return user


@docs.register
@doc(description="Update own user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/me", methods=["PUT"])
@use_kwargs(
    {
        "password": fields.Str(),
        "human_name": fields.Str(),
        "email": fields.Str(),
    }
)
@marshal_with(UserSchema())
@jwt_required
def route_users_me_put(
    *,
    password=None,
    human_name=None,
    email=None,
):
    current_user: UserStored = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    user_in = UserInUpdate(
        **current_user.json_dict()
    )
    if password is not None:
        user_in.password = password
    if human_name is not None:
        user_in.human_name = human_name
    if email is not None:
        user_in.email = email
    
    user = update_user(bucket, user_in)
    return user


@docs.register
@doc(description="Get current user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/me", methods=["GET"])
@marshal_with(UserSchema())
@jwt_required
def route_users_me_get():
    current_user = get_current_user()
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    return current_user


@docs.register
@doc(
    description="Get a specific user by username (email)",
    security=security_params,
    tags=["users"],
)
@app.route(f"{config.API_V1_STR}/users/<name>", methods=["GET"])
@marshal_with(UserSchema())
@jwt_required
def route_users_id_get(name):
    current_user = get_current_user()  # type: User
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    user = get_user(bucket, name)
    if user == current_user:
        return user
    if not check_if_user_is_admin_or_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    return user


@docs.register
@doc(description="Create new user without the need to be logged in", tags=["users"])
@app.route(f"{config.API_V1_STR}/users/open", methods=["POST"])
@use_kwargs(
    {
        "name": fields.Str(required=True),
        "password": fields.Str(required=True),
        "email": fields.Str(),
        "human_name": fields.Str(),
    }
)
@marshal_with(UserSchema())
def route_users_post_open(*, name, password, email=None, human_name=None):
    if not config.USERS_OPEN_REGISTRATION:
        abort(403, "Open user resgistration is forbidden on this server")
    user = get_user(bucket, name)
    if user:
        return abort(400, f"The user with this username already exists in the system")
    user_in = UserInCreate(name=name, password=password, email=email, human_name=human_name)
    user = upsert_user(bucket, user_in)
    return user
