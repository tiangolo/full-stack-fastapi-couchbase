# -*- coding: utf-8 -*-

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
from app.crud.user import (
    check_if_user_is_active,
    check_if_user_is_superuser,
    get_user,
    get_users,
    create_or_get_user,
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
    elif not check_if_user_is_superuser(current_user):
        abort(400, "Not a superuser")
    users = get_users(bucket, skip=skip, limit=limit)
    return users


@docs.register
@doc(description="Create new user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/", methods=["POST"])
@use_kwargs(
    {"username": fields.Str(required=True), "password": fields.Str(required=True)}
)
@marshal_with(UserSchema())
@jwt_required
def route_users_post(username=None, password=None):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_superuser(current_user):
        abort(400, "Not a superuser")
    user = get_user(bucket, username)
    if user:
        return abort(400, f"The user with this username already exists in the system.")
    user = create_or_get_user(bucket, username, password, email=username)
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
@app.route(f"{config.API_V1_STR}/users/<string:username>", methods=["GET"])
@marshal_with(UserSchema())
@jwt_required
def route_users_id_get(username):
    current_user = get_current_user()  # type: User
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    user = get_user(bucket, username)
    if user == current_user:
        return user
    if not check_if_user_is_superuser(current_user):
        abort(400, "Not a superuser")
    return user


@docs.register
@doc(description="Create new user without the need to be logged in", tags=["users"])
@app.route(f"{config.API_V1_STR}/users/open", methods=["POST"])
@use_kwargs(
    {"username": fields.Str(required=True), "password": fields.Str(required=True)}
)
@marshal_with(UserSchema())
def route_users_post_open(username=None, password=None):
    if not config.USERS_OPEN_REGISTRATION:
        abort(403, "Open user resgistration is forbidden on this server")
    user = get_user(bucket, username)
    if user:
        return abort(400, f"The user with this username already exists in the system")
    user = create_or_get_user(bucket, username, password, email=username)
    return user
