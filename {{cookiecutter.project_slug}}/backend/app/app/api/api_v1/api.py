from fastapi import APIRouter

from app.api.api_v1.endpoints import role, token, user, utils

api_router = APIRouter()
api_router.include_router(role.router)
api_router.include_router(token.router)
api_router.include_router(user.router)
api_router.include_router(utils.router)
