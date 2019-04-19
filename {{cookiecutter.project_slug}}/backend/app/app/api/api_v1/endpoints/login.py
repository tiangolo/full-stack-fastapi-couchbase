from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.utils.security import get_current_user
from app.core import config
from app.core.jwt import create_access_token
from app.db.database import get_default_bucket
from app.models.msg import Msg
from app.models.token import Token
from app.models.user import User, UserInDB, UserUpdate
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    bucket = get_default_bucket()
    user = crud.user.authenticate(
        bucket, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data={"username": user.username}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=User)
def test_token(current_user: UserInDB = Depends(get_current_user)):
    """
    Test access token.
    """
    return current_user


@router.post("/password-recovery/{username}", response_model=Msg)
def recover_password(username: str):
    """
    Password Recovery.
    """
    bucket = get_default_bucket()
    user = crud.user.get(bucket, username=username)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(username=username)
    send_reset_password_email(
        email_to=user.email, username=username, token=password_reset_token
    )
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=Msg)
def reset_password(token: str, new_password: str):
    """
    Reset password.
    """
    username = verify_password_reset_token(token)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid token")
    bucket = get_default_bucket()
    user = crud.user.get(bucket, username=username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    user_in = UserUpdate(name=username, password=new_password)
    user = crud.user.update(bucket, username=username, user_in=user_in)
    return {"msg": "Password updated successfully"}
