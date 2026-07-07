from fastapi import APIRouter
from app.api.v1.endpoints import auth, menu, order

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
