from fastapi import APIRouter, Depends
from services.users_service.app.core.deps import get_me_service
from services.users_service.app.schemas.me import MeOut
from services.users_service.app.services.me import MeService

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=MeOut)
async def get_me(
    svc: MeService = Depends(get_me_service),
) -> MeOut:
    """
    Handles the retrieval of user information.

    This function acts as an endpoint to get the current user's data, leveraging
    the service layer to fetch and return the required details.

    :param svc: Dependency-injected service to handle operations for retrieving
        user-related information.
    :return: The user information data model.
    """
    return await svc.get_me()
