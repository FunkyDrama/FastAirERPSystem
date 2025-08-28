from fastapi import APIRouter
from .auth import router as auth_router
from .flights import router as flights_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(flights_router)

__all__ = ["router"]
