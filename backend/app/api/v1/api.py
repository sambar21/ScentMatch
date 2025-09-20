﻿from fastapi import APIRouter
from app.api.v1.endpoints import auth, recomender  

api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["authentication"]
)


api_router.include_router(recomender.router)  

