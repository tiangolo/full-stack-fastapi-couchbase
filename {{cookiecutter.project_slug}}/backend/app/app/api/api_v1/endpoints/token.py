# Import standard library
from datetime import timedelta

# Import installed modules
from flask import abort
from flask_apispec import doc, use_kwargs, marshal_with
from flask_jwt_extended import create_access_token, get_current_user, jwt_required
from webargs import fields

# Import app code
from app.main import app
from app.db.database import get_default_bucket
from ..api_docs import docs, security_params
from app.core import config
from app.crud.user import authenticate_user, check_if_user_is_active, check_if_user_is_superuser, get_user, update_user
from app.utils import send_reset_password_email, generate_password_reset_token, verify_password_reset_token
from app.models.user import UserInUpdate

# Import Schemas
from app.schemas.token import TokenSchema
from app.schemas.user import UserSchema
from app.schemas.msg import MsgSchema


@docs.register
@doc(
    description="OAuth2 compatible token login, get an access token for future requests",
    tags=["login"],
)
@app.route(f"{config.API_V1_STR}/login/access-token", methods=["POST"])
@use_kwargs(
    {"username": fields.Str(required=True), "password": fields.Str(required=True)}
)
@marshal_with(TokenSchema())
def route_login_access_token(username, password):
    bucket = get_default_bucket()
    user = authenticate_user(bucket, username, password)
    if not user:
        abort(400, "Incorrect email or password")
    elif not check_if_user_is_active(user):
        abort(400, "Inactive user")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            identity=username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


# OAuth2 compatible token login, get an access token for future requests has a test in test_token
@docs.register
@doc(description="Test access token", tags=["login"], security=security_params)
@app.route(f"{config.API_V1_STR}/login/test-token", methods=["POST"])
@use_kwargs({"test": fields.Str(required=True)})
@marshal_with(UserSchema())
@jwt_required
def route_test_token(test):
    current_user = get_current_user()
    if current_user:
        return current_user
    else:
        abort(400, "No user")
    return current_user


@docs.register
@doc(
    description='Test access token manually, same as the endpoint to "Test access token" but copying and adding the Authorization: Bearer <token>',
    params={
        "Authorization": {
            "description": "Authorization HTTP header with JWT token, like: Authorization: Bearer asdf.qwer.zxcv",
            "in": "header",
            "type": "string",
            "required": True,
        }
    },
    tags=["login"],
)
@app.route(f"{config.API_V1_STR}/login/manual-test-token", methods=["POST"])
@use_kwargs({"test": fields.Str(required=True)})
@marshal_with(UserSchema())
@jwt_required
def route_manual_test_token(test):
    current_user = get_current_user()
    if current_user:
        return current_user
    else:
        abort(400, "No user")
    return current_user


@docs.register
@doc(description="Recover password", tags=["login"])
@app.route(f"{config.API_V1_STR}/password-recovery/<name>", methods=["POST"])
@marshal_with(MsgSchema())
def route_recover_password(name):
    bucket = get_default_bucket()
    user = get_user(bucket, name)

    if not user:
        return abort(404, f"The user with this username does not exist in the system.")
    password_reset_token = generate_password_reset_token(name)
    send_reset_password_email(email_to=user.email, username=name, token=password_reset_token)
    return {"msg": "Password recovery email sent"}


@docs.register
@doc(description="Reset password", tags=["login"])
@app.route(f"{config.API_V1_STR}/reset-password/", methods=["POST"])
@use_kwargs({
    "token": fields.Str(required=True),
    "new_password": fields.Str(required=True)})
@marshal_with(MsgSchema())
def route_reset_password(token, new_password):
    name = verify_password_reset_token(token)
    if not name:
        abort(400, "Invalid token")
    bucket = get_default_bucket()
    user = get_user(bucket, name)
    if not user:
        return abort(404, f"The user with this username does not exist in the system.")
    elif not check_if_user_is_active(user):
        abort(400, "Inactive user")
    user_in = UserInUpdate(
        name=name,
        password=new_password,
    )
    user = update_user(bucket, user_in)
    return {"msg": "Password updated successfully"}
