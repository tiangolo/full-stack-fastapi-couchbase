from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.utils.security import get_current_active_user
from app.db.database import get_default_bucket
from app.models.item import Item, ItemCreate, ItemUpdate
from app.models.user import UserInDB

router = APIRouter()


@router.get("/", response_model=List[Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Retrieve items.

    If superuser, all the items.

    If normal user, the items owned by this user.
    """
    bucket = get_default_bucket()
    if crud.user.is_superuser(current_user):
        docs = crud.item.get_multi(bucket, skip=skip, limit=limit)
    else:
        docs = crud.item.get_multi_by_owner(
            bucket=bucket, owner_username=current_user.username, skip=skip, limit=limit
        )
    return docs


@router.get("/search/", response_model=List[Item])
def search_items(
    q: str,
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Search items, use Bleve Query String syntax:
    http://blevesearch.com/docs/Query-String-Query/

    For typeahead suffix with `*`. For example, a query with: `title:foo*` will match
    items containing `football`, `fool proof`, etc.
    """
    bucket = get_default_bucket()
    if crud.user.is_superuser(current_user):
        docs = crud.item.search(bucket=bucket, query_string=q, skip=skip, limit=limit)
    else:
        docs = crud.item.search_with_owner(
            bucket=bucket,
            query_string=q,
            username=current_user.username,
            skip=skip,
            limit=limit,
        )
    return docs


@router.post("/", response_model=Item)
def create_item(
    *, item_in: ItemCreate, current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Create new item.
    """
    bucket = get_default_bucket()
    id = crud.utils.generate_new_id()
    doc = crud.item.upsert(
        bucket=bucket, id=id, doc_in=item_in, owner_username=current_user.username
    )
    return doc


@router.put("/{id}", response_model=Item)
def update_item(
    *,
    id: str,
    item_in: ItemUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Update an item.
    """
    bucket = get_default_bucket()
    doc = crud.item.get(bucket=bucket, id=id)
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (
        doc.owner_username != current_user.username
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    doc = crud.item.update(
        bucket=bucket, id=id, doc_in=item_in, owner_username=doc.owner_username
    )
    return doc


@router.get("/{id}", response_model=Item)
def read_item(id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """
    Get item by ID.
    """
    bucket = get_default_bucket()
    doc = crud.item.get(bucket=bucket, id=id)
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (
        doc.owner_username != current_user.username
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return doc


@router.delete("/{id}", response_model=Item)
def delete_item(id: str, current_user: UserInDB = Depends(get_current_active_user)):
    """
    Delete an item by ID.
    """
    bucket = get_default_bucket()
    doc = crud.item.get(bucket=bucket, id=id)
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (
        doc.owner_username != current_user.username
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    doc = crud.item.remove(bucket=bucket, id=id)
    return doc
