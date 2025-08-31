from fastapi import APIRouter
from .auth import router as auth_router
from .flights import router as flights_router
from .booking import router as booking_router
from .me import router as me_router
from .payments import router as payments_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(flights_router)
router.include_router(booking_router)
router.include_router(me_router)
router.include_router(payments_router)

__all__ = ["router"]
