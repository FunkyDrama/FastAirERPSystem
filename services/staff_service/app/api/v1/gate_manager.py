from fastapi import APIRouter, Depends

from services.staff_service.app.core.deps import get_gate_service, require_gate_manager
from services.staff_service.app.services.gate_manager import GateManagerService

router = APIRouter(
    prefix="/gate",
    tags=["gate management"],
    dependencies=[Depends(require_gate_manager)],
)


@router.post("/boarding/{ticket_number}")
async def boarding(
    ticket_number: str,
    gms: GateManagerService = Depends(get_gate_service),
):
    return await gms.registry_ticket_boarding(ticket_number)


@router.get("/flights/{flight_id}/passengers/boarding")
async def list_passengers_on_flight(
    flight_id: str,
    gms: GateManagerService = Depends(get_gate_service),
):
    return await gms.list_passengers_on_flight(flight_id)
