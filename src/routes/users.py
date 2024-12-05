from fastapi_limiter.depends import RateLimiter

from src.entity.model import User
from fastapi import APIRouter, Depends
from src.schemas.user import UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse, description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user

