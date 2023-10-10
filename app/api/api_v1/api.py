from fastapi import APIRouter
from app.api.api_v1.endpoints import load

api_v1_router = APIRouter()

api_v1_router.include_router(load.router, prefix="/load", tags=["document loader"])
