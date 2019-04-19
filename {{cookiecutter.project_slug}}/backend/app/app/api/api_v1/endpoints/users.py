from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic.types import EmailStr

from app import crud
from app.api.utils.security import get_current_active_superuser, get_current_active_user
from app.core import config
from app.db.database import get_default_bucket
from app.models.user import User, UserCreate, UserInDB, UserUpdate
from app.utils import send_new_account_email

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_superuser),
):
    """
    Retrieve users.
    """
    bucket = get_default_bucket()
    users = crud.user.get_multi(bucket, skip=skip, limit=limit)
    return users


@router.get("/search/", response_model=List[User])
def search_users(
    q: str,
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_superuser),
):
    """
    Search users, use Bleve Query String syntax:
    http://blevesearch.com/docs/Query-String-Query/

    For typeahead suffix with `*`. For example, a query with: `email:johnd*` will match
    users with email `johndoe@example.com`, `johndid@example.net`, etc.
    """
    bucket = get_default_bucket()
    users = crud.user.search(bucket=bucket, query_string=q, skip=skip, limit=limit)
    return users


@router.post("/", response_model=User)
def create_user(
    *,
    user_in: UserCreate,
    current_user: UserInDB = Depends(get_current_active_superuser),
):
    """
    Create new user.
    """
    bucket = get_default_bucket()
    user = crud.user.get(bucket, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    if config.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.username, password=user_in.password
        )
    return user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Update own user.
    """
    user_in = UserUpdate(**current_user.dict())
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    bucket = get_default_bucket()
    user = crud.user.update(bucket, username=current_user.username, user_in=user_in)
    return user


@router.get("/me", response_model=User)
def read_user_me(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=User)
def create_user_open(
    *,
    username: str = Body(...),
    password: str = Body(...),
    email: EmailStr = Body(None),
    full_name: str = Body(None),
):
    """
    Create new user without the need to be logged in.
    """
    if not config.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user resgistration is forbidden on this server",
        )
    bucket = get_default_bucket()
    user = crud.user.get(bucket, username=username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = UserCreate(
        username=username, password=password, email=email, full_name=full_name
    )
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    if config.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.username, password=user_in.password
        )
    return user


@router.get("/{username}", response_model=User)
def read_user(username: str, current_user: UserInDB = Depends(get_current_active_user)):
    """
    Get a specific user by username (email).
    """
    bucket = get_default_bucket()
    user = crud.user.get(bucket, username=username)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{username}", response_model=User)
def update_user(
    *,
    username: str,
    user_in: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_superuser),
):
    """
    Update a user.
    """
    bucket = get_default_bucket()
    user = crud.user.get(bucket, username=username)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(bucket, username=username, user_in=user_in)
    return user
