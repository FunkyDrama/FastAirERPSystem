import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from scripts.db import session_ctx

from services.staff_service.app.db.models.airplane import Airplane
from services.staff_service.app.db.models.flight import (
    Flight as StaffFlight,
    FlightStatus as StaffFlightStatus,
)
from services.staff_service.app.db.models.staff_user import StaffUser, StaffRole
from services.staff_service.app.services.auth import StaffAuthService

from services.users_service.app.db.models.flight_ref import (
    FlightRef as UsersFlightRef,
    FlightStatus as UsersFlightStatus,
)


async def _truncate_if_required_staff(session: AsyncSession, flush: bool) -> None:
    if not flush:
        return
    for model in (StaffFlight, Airplane, StaffUser):
        await session.execute(delete(model))
    await session.commit()


async def seed_staff_users(session: AsyncSession) -> None:
    if (await session.execute(select(StaffUser))).first():
        return
    session.add_all(
        [
            StaffUser(
                user_id=uuid.uuid4(),
                email="gate_manager@example.com",
                password_hash=await StaffAuthService.hash_password("hashed_pwd"),
                role=StaffRole.GATE_MANAGER,
            ),
            StaffUser(
                user_id=uuid.uuid4(),
                email="checkin_manager@example.com",
                password_hash=await StaffAuthService.hash_password("hashed_pwd"),
                role=StaffRole.CHECKIN_MANAGER,
            ),
            StaffUser(
                user_id=uuid.uuid4(),
                email="supervisor@example.com",
                password_hash=await StaffAuthService.hash_password("hashed_pwd"),
                role=StaffRole.SUPERVISOR,
            ),
        ]
    )
    await session.commit()


async def seed_airplanes(session: AsyncSession) -> None:
    if (await session.execute(select(Airplane))).first():
        return
    session.add_all(
        [
            Airplane(airplane_id=uuid.uuid4(), model="Airbus A320", total_seats=180),
            Airplane(airplane_id=uuid.uuid4(), model="Boeing 737", total_seats=160),
            Airplane(airplane_id=uuid.uuid4(), model="Embraer E190", total_seats=110),
        ]
    )
    await session.commit()


def _map_status(u_status: UsersFlightStatus) -> StaffFlightStatus:
    try:
        return StaffFlightStatus[u_status.name]
    except Exception:
        return StaffFlightStatus.SCHEDULED


async def _mirror_flights_from_users(
    users_dsn: str, staff_session: AsyncSession
) -> None:
    async with session_ctx(users_dsn) as users_sess:
        result = await users_sess.execute(
            select(
                UsersFlightRef.flight_id,
                UsersFlightRef.flight_number,
                UsersFlightRef.origin,
                UsersFlightRef.destination,
                UsersFlightRef.departure_time,
                UsersFlightRef.arrival_time,
                UsersFlightRef.status,
            )
        )
        users_flights = result.all()

    planes = (await staff_session.execute(select(Airplane))).scalars().all()
    if not planes:
        await seed_airplanes(staff_session)
        planes = (await staff_session.execute(select(Airplane))).scalars().all()

    def choose_plane(flight_number: str) -> uuid.UUID:
        idx = abs(hash(flight_number)) % len(planes)
        return planes[idx].airplane_id

    existing_ids = set(
        (await staff_session.execute(select(StaffFlight.flight_id))).scalars().all()
    )

    created = 0
    for fid, fnum, orig, dest, dep, arr, st in users_flights:
        if fid in existing_ids:
            continue
        staff_session.add(
            StaffFlight(
                flight_id=fid,
                flight_number=fnum,
                origin=orig,
                destination=dest,
                departure_time=dep,
                arrival_time=arr,
                status=_map_status(st),
                airplane_id=choose_plane(fnum),
            )
        )
        created += 1

    if created:
        await staff_session.commit()


async def seed_staff_db(
    *, staff_dsn: str, users_dsn: str, flush: bool, **_: object
) -> None:
    async with session_ctx(staff_dsn) as staff_session:
        await _truncate_if_required_staff(staff_session, flush)
        await seed_staff_users(staff_session)
        await seed_airplanes(staff_session)
        await _mirror_flights_from_users(users_dsn, staff_session)
        print("[staff] seeded: staff_users, airplanes, mirrored flights from users_db")
