from fastapi import APIRouter

from app.api.routes.categories import router as categories_router
from app.api.routes.listings import router as listings_router
from app.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(users_router)
api_router.include_router(categories_router)
api_router.include_router(listings_router)
