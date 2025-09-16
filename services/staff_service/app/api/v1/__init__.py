from fastapi import APIRouter

from .auth import router as auth_router
from .gate_manager import router as gate_manager_router
from .check_in_manager import router as check_in_manager_router
from .supervisor import router as supervisor_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(gate_manager_router)
router.include_router(check_in_manager_router)
router.include_router(supervisor_router)

__all__ = ["router"]
