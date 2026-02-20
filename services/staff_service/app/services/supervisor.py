import uuid

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services.staff_service.app.db.models.flight import FlightStatus, Flight
from services.staff_service.app.messaging.task_manager import StaffTaskManager
from services.staff_service.app.repositories.airplane_repo import AirplaneRepository
from services.staff_service.app.repositories.flight_repo import FlightRepository
from services.staff_service.app.repositories.staff_repo import StaffUserRepository
from services.staff_service.app.repositories.ticket_repo import TicketRepository
from services.staff_service.app.schemas.flight import FlightCreateIn, FlightOut
from services.staff_service.app.schemas.staff import StaffUserCreateIn, StaffUserOut
from services.staff_service.app.schemas.ticket import RevenueSchema
from services.staff_service.app.services.auth import StaffAuthService


class SupervisorService:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sm = sessionmaker
        self.tm = StaffTaskManager()

    async def create_flight(self, data: FlightCreateIn) -> FlightOut:
        async with self._sm() as session:
            flight_repo = FlightRepository(session)
            airplane_repo = AirplaneRepository(session)

            if data.origin == data.destination:
                raise ValueError("Origin and destination airports must be different")

            airplane_id: uuid.UUID
            if data.airplane_id:
                airplane = await airplane_repo.get_airplane(data.airplane_id)
                if not airplane:
                    raise ValueError(f"Airplane {data.airplane_id} not found")
                airplane_id = airplane.airplane_id
            elif data.airplane:
                airplane = await airplane_repo.add_airplane(
                    model=data.airplane.model,
                    total_seats=data.airplane.total_seats,
                )
                airplane_id = airplane.airplane_id
                await airplane_repo.save()
            else:
                raise ValueError("Either airplane_id or airplane must be provided")

            flight = Flight(
                flight_id=uuid.uuid4(),
                flight_number=data.flight_number,
                origin=data.origin,
                destination=data.destination,
                departure_time=data.departure_time,
                arrival_time=data.arrival_time,
                airplane_id=airplane_id,
                status=FlightStatus.SCHEDULED,
            )

            await flight_repo.create_flight(flight)
            await flight_repo.save()

            self.tm.create_flight(FlightOut.model_validate(flight).model_dump())
            return FlightOut.model_validate(flight)

    async def delete_flight(self, flight_id: uuid.UUID) -> dict:
        async with self._sm() as session:
            repo = FlightRepository(session)
            await repo.cancel_flight(flight_id)
            await repo.save()
            self.tm.cancel_flight(flight_id)
            return {"message": "Flight deleted"}

    async def cancel_flight(self, flight_id: uuid.UUID) -> dict:
        async with self._sm() as session:
            repo = FlightRepository(session)
            await repo.cancel_flight(flight_id)
            await repo.save()
            self.tm.cancel_flight(flight_id)
            return {"message": "Flight cancelled"}

    async def get_all_flights(self) -> list[FlightOut]:
        async with self._sm() as session:
            repo = FlightRepository(session)
            completed_ids = await repo.complete_overdue_flights()
            await repo.save()
            for flight_id in completed_ids:
                self.tm.complete_flight(flight_id)
            flights = await repo.get_all_flights()
            return [FlightOut.model_validate(flight) for flight in flights]

    async def get_all_staff_users(self) -> list[StaffUserOut]:
        async with self._sm() as session:
            repo = StaffUserRepository(session)
            staff = await repo.get_all_staff()
            return [StaffUserOut.model_validate(s) for s in staff]

    async def add_staff(self, data: StaffUserCreateIn) -> dict:
        async with self._sm() as session:
            repo = StaffUserRepository(session)
            if await repo.get_staff_by_email(str(data.email)):
                raise ValueError("Staff user already exists")
            hashed = await StaffAuthService.hash_password(data.password)
            payload = data.model_dump()
            payload["password_hash"] = hashed
            del payload["password"]
            await repo.create_staff(payload)
            await repo.save()
            return {"message": "Staff user created"}

    async def delete_staff(self, staff_id: uuid.UUID) -> dict:
        async with self._sm() as session:
            repo = StaffUserRepository(session)
            staff = await repo.get_staff_by_id(staff_id)
            if not staff:
                raise ValueError("Staff user not found")
            await repo.delete_staff(staff)
            await repo.save()
            return {"message": "Staff user deleted"}

    async def get_revenue(self, flight_id: str | None) -> RevenueSchema:
        async with self._sm() as session:
            repo = TicketRepository(session)
            if flight_id:
                revenue = await repo.get_revenue_by_flight(flight_id)
                return RevenueSchema(flight_id=flight_id, revenue=revenue)
            revenue = await repo.get_total_revenue()
            return RevenueSchema(flight_id="total", revenue=revenue)
