import uuid
import datetime as dt
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from scripts.db import session_ctx
from scripts.seed.common import (
    AIRPORTS,
    pick,
    flight_number,
    rand_datetime_within_days,
)

from services.users_service.app.db.models.seat_type import SeatType
from services.users_service.app.db.models.option import Option
from services.users_service.app.db.models.discount import Discount
from services.users_service.app.db.models.flight_ref import FlightRef, FlightStatus


async def _truncate_if_required(session: AsyncSession, flush: bool) -> None:
    """
    Truncates specified tables in the database if the flush flag is set to True.

    This coroutine checks the value of the `flush` parameter and proceeds to delete
    all records from the given models in the database when the flag is True. The
    affected models are FlightRef, Option, SeatType, and Discount. The changes are
    immediately committed to the database. If `flush` is False, the function
    returns without performing any operations.

    :param session: Database session to be used for executing deletion queries.
                    It should be an instance of AsyncSession.
    :param flush: Determines if truncation should be applied. When set to True,
                  the specified tables are truncated.
    :return: This function does not return a value.
    """
    if not flush:
        return
    for model in (FlightRef, Option, SeatType, Discount):
        await session.execute(delete(model))
    await session.commit()


async def seed_seat_types(session: AsyncSession) -> None:
    """
    Seeds the `SeatType` table with predefined seat types if they do not already exist.
    The predefined seat types include "ECONOMY", "PREMIUM_ECONOMY", and "BUSINESS".
    This function ensures that missing entries in the database are supplemented with
    these preconfigured seat types.

    :param session: AsyncSession instance used to execute database operations.
    :type session: AsyncSession
    :return: This function does not return a value.
    :rtype: None
    """
    wanted = [
        ("ECONOMY", "Standard economy seat"),
        ("PREMIUM_ECONOMY", "Extra legroom"),
        ("BUSINESS", "Business seat"),
    ]
    existing: Sequence[str] = list(
        (await session.execute(select(SeatType.type_name))).scalars().all()
    )
    to_add = [
        SeatType(type_name=n, description=d) for n, d in wanted if n not in existing
    ]
    session.add_all(to_add)
    await session.commit()


async def seed_options(session: AsyncSession) -> None:
    """
    Seeds options into the database for predefined items if they do not already exist.
    This function compares a predefined set of options with the ones present in the
    database and adds any missing options to the database.

    :param session: The database session used for querying and adding options.
    :type session: AsyncSession
    :return: None
    """
    wanted = [
        ("BAG_10KG", Decimal("25.00")),
        ("BAG_20KG", Decimal("40.00")),
        ("MEAL_STD", Decimal("12.00")),
        ("MEAL_VEG", Decimal("12.00")),
        ("SEAT_CHOICE", Decimal("8.00")),
        ("PRIORITY", Decimal("15.00")),
    ]
    existing: Sequence[str] = list(
        (await session.execute(select(Option.name))).scalars().all()
    )
    to_add = [Option(name=n, price=p) for n, p in wanted if n not in existing]
    session.add_all(to_add)
    await session.commit()


async def seed_discounts(session: AsyncSession) -> None:
    """
    Seeds the database with predefined discount codes if they do not already exist.

    This function checks for the existence of pre-defined discount codes in the database.
    If any of the specified discount codes are not present, it adds them to the database
    and commits the changes. The function ensures no duplicate discount codes are inserted.

    :param session: The database session used to execute queries and commit changes.
    :type session: AsyncSession
    :return: This function does not return any value.
    """
    wanted = [
        ("WELCOME10", "Welcome 10% off", 10),
        ("SPRING15", "Spring sale 15% off", 15),
    ]
    existing: Sequence[str] = list(
        (await session.execute(select(Discount.discount_code))).scalars().all()
    )
    to_add = [
        Discount(discount_code=c, description=desc, percent_off=percent)
        for c, desc, percent in wanted
        if c not in existing
    ]
    session.add_all(to_add)
    await session.commit()


async def seed_flights(
    session: AsyncSession, *, flights_count: int, days_window: int
) -> None:
    """
    Seeds the database with randomly generated flight records. The function ensures that
    unique flight numbers and departure times are created while taking into account the
    specified number of flights and days window. Flight data is randomized and includes
    details such as origin, destination, departure time, arrival time, and flight status.

    :param session: Async database session used to interact and commit the created flight
        records to the underlying database.
    :type session: AsyncSession
    :param flights_count: The target number of flights to seed into the database.
    :type flights_count: int
    :param days_window: The span of days within which flight departure and arrival
        times should be generated.
    :type days_window: int
    :return: None, as the function performs actions directly on the database without
        returning data.
    :rtype: None
    """
    existing_pairs = set(
        (
            await session.execute(
                select(FlightRef.flight_number, FlightRef.departure_time)
            )
        ).all()
    )
    created = 0
    attempts = 0
    max_attempts = flights_count * 10

    while created < flights_count and attempts < max_attempts:
        attempts += 1
        origin = pick(AIRPORTS)
        dest = pick([a for a in AIRPORTS if a != origin])
        dep, arr = rand_datetime_within_days(days_window)
        fn = flight_number()
        key = (fn, dep.replace(tzinfo=dt.timezone.utc))
        if key in existing_pairs:
            continue

        fr = FlightRef(
            flight_id=uuid.uuid4(),
            flight_number=fn,
            origin=origin,
            destination=dest,
            departure_time=dep,
            arrival_time=arr,
            status=FlightStatus.SCHEDULED,
        )
        session.add(fr)
        existing_pairs.add(key)
        created += 1

    await session.commit()


async def seed_users_db(
    *,
    dsn: str,
    flush: bool,
    flights_count: int,
    days_window: int,
) -> None:
    """
    Seed the users database with necessary data, including seat types, options,
    discounts, and flights. Allows toggling of flushing existing data prior to seeding.

    :param dsn: The data source name used to connect to the database.
    :type dsn: str
    :param flush: Indicates whether to truncate existing data in the database
        before seeding the new data.
    :type flush: bool
    :param flights_count: Number of flights records to seed in the database.
    :type flights_count: int
    :param days_window: The range of days used to determine the scheduling of
        seeded flights.
    :type days_window: int

    :return: None
    """
    async with session_ctx(dsn) as session:
        await _truncate_if_required(session, flush)
        await seed_seat_types(session)
        await seed_options(session)
        await seed_discounts(session)
        await seed_flights(
            session, flights_count=flights_count, days_window=days_window
        )
        print(
            f"[users] seeded: seat_types, options, discounts, flights({flights_count})"
        )
