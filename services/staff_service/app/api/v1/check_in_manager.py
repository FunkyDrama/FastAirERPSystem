from fastapi import APIRouter, Depends

from services.staff_service.app.core.deps import (
    require_checkin_manager,
    get_checkin_service,
)
from services.staff_service.app.schemas.ticket import QRScanIn
from services.staff_service.app.services.check_in_manager import CheckInManagerService

router = APIRouter(
    prefix="/checkin",
    dependencies=[Depends(require_checkin_manager)],
    tags=["check-in management"],
)


@router.post("/scan")
async def scan_ticket(
    data: QRScanIn,
    cm: CheckInManagerService = Depends(get_checkin_service),
):
    return await cm.handle_qr_code(data.ticket_number)


@router.get("/flights/{flight_number}/passengers")
async def list_passengers_on_flight(
    flight_number: str,
    cm: CheckInManagerService = Depends(get_checkin_service),
):
    return await cm.get_all_passengers_on_flight(flight_number)


@router.post("/{ticket_number}")
async def checkin(
    ticket_number: str,
    cm: CheckInManagerService = Depends(get_checkin_service),
):
    return await cm.check_in_ticket(ticket_number)
