from fastapi import APIRouter, Depends
from services.staff_service.app.core.deps import (
    require_supervisor,
    get_supervisor_service,
)
from services.staff_service.app.schemas.flight import FlightCreateIn, FlightOut
from services.staff_service.app.schemas.staff import StaffUserCreateIn
from services.staff_service.app.services.supervisor import SupervisorService

router = APIRouter(
    prefix="/supervisor",
    tags=["supervisor"],
    dependencies=[Depends(require_supervisor)],
)


@router.post("/flights", response_model=FlightOut)
async def create_flight(
    data: FlightCreateIn,
    svc: SupervisorService = Depends(get_supervisor_service),
):
    return await svc.create_flight(data)


@router.get("/flights")
async def get_flights(svc: SupervisorService = Depends(get_supervisor_service)):
    return await svc.get_all_flights()


@router.delete("/flights/{flight_id}")
async def delete_flight(
    flight_id: str,
    svc: SupervisorService = Depends(get_supervisor_service),
):
    await svc.delete_flight(flight_id)


@router.post("/staff-users")
async def add_staff(
    data: StaffUserCreateIn,
    svc: SupervisorService = Depends(get_supervisor_service),
):
    return await svc.add_staff(data)


@router.delete("/staff-users/{staff_id}")
async def delete_staff(
    staff_id: str,
    svc: SupervisorService = Depends(get_supervisor_service),
):
    return await svc.delete_staff(staff_id)


@router.get("/revenue")
async def get_revenue(
    flight_id: str | None = None,
    svc: SupervisorService = Depends(get_supervisor_service),
):
    return await svc.get_revenue(flight_id)
