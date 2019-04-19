from pydantic import BaseModel

from app.models.config import ITEM_DOC_TYPE


# Shared properties
class ItemBase(BaseModel):
    title: str = None
    description: str = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties to return to client
class Item(ItemBase):
    id: str
    title: str
    owner_username: str


# Properties properties stored in DB
class ItemInDB(ItemBase):
    type: str = ITEM_DOC_TYPE
    id: str
    title: str
    owner_username: str
