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
from app.api.api_v1.api_docs import docs, security_params
from app.core import config
from app.db.database import get_db_users, get_client
from app.db.utils import (
    create_user_with_default_db,
    check_if_user_is_active,
    check_if_user_is_superuser,
    get_user,
    get_database_id_for_user,
)

# Import Schemas
from app.schemas.user import UserSchema
from app.schemas.msg import MsgSchema


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
    db_users = get_db_users()
    result = db_users.get_query_result(selector={"type": "user"})
    return result[skip : skip + limit]


# Retrieve users has a test in test_user


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
    user = get_user(username)
    if user:
        return abort(400, f"The user with this username already exists in the system.")
    user = create_user_with_default_db(username, password)
    return user


# Create new user has tests in test_user


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


# Get current user has a test in test_user


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
    user = get_user(username)
    if user == current_user:
        return user
    if not check_if_user_is_superuser(current_user):
        abort(400, "Not a superuser")
    return user


# Get a specific user by username (email) has a test in test_user


@docs.register
@doc(
    description="Get a specific user database ID by username (email)",
    security=security_params,
    tags=["users"],
)
@app.route(f"{config.API_V1_STR}/users/<string:username>/dbid", methods=["GET"])
@marshal_with(MsgSchema())
@jwt_required
def route_users_username_dbid_get(username):
    current_user = get_current_user()  # type: User
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    user = get_user(username)
    user_db_id = get_database_id_for_user(username)
    response = {"msg": user_db_id}
    if user == current_user:
        return response
    if not check_if_user_is_superuser(current_user):
        abort(400, "Not a superuser")
    return response


# Get a specific user database ID by username (email) has a test in test_user


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
    client = get_client()
    db_users = get_db_users(client)

    user = get_user(username, db_users, client)

    if user:
        return abort(400, f"The user with this username already exists in the system")

    user = create_user_with_default_db(username, password, db_users, client)
    return user
