from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["authentication"]
)

# Future routes will be added here:
# api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
# api_router.include_router(annotations.router, prefix="/annotations", tags=["annotations"])
