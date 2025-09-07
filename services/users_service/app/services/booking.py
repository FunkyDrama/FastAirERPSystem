import datetime as dt
import uuid
from decimal import Decimal
from collections.abc import Iterable, Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.users_service.app.db.models.booking import BookingStatus
from services.users_service.app.db.models.discount import Discount
from services.users_service.app.db.models.flight_ref import FlightRef, FlightStatus
from services.users_service.app.db.models.option import Option, ticket_options
from services.users_service.app.db.models.pricing import PricingConfig
from services.users_service.app.db.models.seat_type import SeatType
from services.users_service.app.db.models.ticket import Ticket, TicketStatus
from services.users_service.app.db.models.user import UserAccount
from services.users_service.app.repositories.booking_repo import BookingRepository
from services.users_service.app.schemas.booking import (
    QuoteIn,
    QuoteOut,
    PriceBreakdownPerTicket,
    DiscountInfo,
    CreateBookingIn,
    BookingOut,
    TicketOut,
    FlightBrief,
    MyBookingsOut,
    BookingShortOut,
    PassengerRef,
    PassengerCreate,
)
from services.users_service.app.schemas.booking import PassengerRefOrCreate, OptionPick


class BookingService:
    """
    Handles booking-related operations such as generating quotes, creating bookings, and
    managing ticket options. It interacts with a repository and session for data access
    and management.

    This service is built to support asynchronous operations, ensuring non-blocking
    interactions, and is designed to handle various scenarios such as calculating pricing,
    resolving passengers, and applying booking options efficiently.

    :ivar session: The asynchronous database session used for data operations.
    :type session: AsyncSession
    :ivar current_user: Represents the currently authenticated user performing the booking
        operations.
    :type current_user: UserAccount
    :ivar repo: Provides repository access for interacting with flight, booking, and
        related entities.
    :type repo: BookingRepository
    """

    def __init__(self, session: AsyncSession, current_user: UserAccount) -> None:
        self.session = session
        self.current_user = current_user
        self.repo = BookingRepository(session)

    async def _load_refs(
        self,
        *,
        flight_id: UUID,
        seat_type_name: str,
        option_ids: Iterable[UUID],
        discount_code: str | None,
    ) -> tuple[FlightRef, SeatType, list[Option], Discount | None]:
        flight = await self.repo.get_flight(flight_id)
        if not flight or flight.status != FlightStatus.SCHEDULED:
            raise ValueError("Flight not found or not scheduled")

        seat = (
            await self.session.execute(
                select(SeatType).where(SeatType.type_name == seat_type_name)
            )
        ).scalar_one_or_none()
        if not seat:
            raise ValueError("Seat type not found")

        opts: list[Option] = []
        if option_ids:
            opts = list(
                (
                    await self.session.execute(
                        select(Option).where(Option.option_id.in_(list(option_ids)))
                    )
                )
                .scalars()
                .all()
            )

        disc = None
        if discount_code:
            disc = (
                await self.session.execute(
                    select(Discount).where(Discount.discount_code == discount_code)
                )
            ).scalar_one_or_none()

        return flight, seat, opts, disc

    def _calc_quote(
        self,
        *,
        passengers_count: int,
        options: Sequence[OptionPick],
        option_rows: Sequence[Option],
        per_passenger_options: bool,
        seat_type_name: str,
        discount: Discount | None,
        _base_price: Decimal,
        _currency: str,
        _multiplier: Decimal,
    ) -> QuoteOut:
        base_per_ticket = _base_price
        mult = _multiplier

        base_total = base_per_ticket * mult * passengers_count

        price_map = {o.option_id: o.price for o in option_rows}
        opt_total = Decimal("0.00")
        for op in options:
            price = price_map.get(op.option_id)
            if not price:
                continue
            opt_total += price * (
                op.qty * passengers_count if per_passenger_options else op.qty
            )

        subtotal = base_total + opt_total

        disc_info = None
        total = subtotal
        if discount:
            disc_amount = (
                subtotal * Decimal(discount.percent_off) / Decimal("100")
            ).quantize(Decimal("0.01"))
            disc_info = DiscountInfo(
                code=discount.discount_code,
                percent_off=discount.percent_off,
                amount=disc_amount,
            )
            total = subtotal - disc_amount

        total = total.quantize(Decimal("0.01"))
        per_ticket_share_opt = (
            (opt_total / passengers_count) if passengers_count else Decimal("0.00")
        )

        breakdown = [
            PriceBreakdownPerTicket(
                passenger_index=i,
                price=(base_per_ticket * mult + per_ticket_share_opt).quantize(
                    Decimal("0.01")
                ),
            )
            for i in range(passengers_count)
        ]

        return QuoteOut(
            currency=_currency,
            base_price_per_ticket=base_per_ticket.quantize(Decimal("0.01")),
            seat_type_multiplier=mult,
            options_total=opt_total.quantize(Decimal("0.01")),
            subtotal=subtotal.quantize(Decimal("0.01")),
            discount=disc_info,
            total=total,
            breakdown_per_ticket=breakdown,
        )

    async def quote(self, data: QuoteIn) -> QuoteOut:
        try:
            flight, seat, opts, disc = await self._load_refs(
                flight_id=data.flight_id,
                seat_type_name=data.seat_type_name,
                option_ids=[x.option_id for x in data.options],
                discount_code=data.discount_code,
            )

            base_price, currency, multiplier = await self._load_pricing(
                data.seat_type_name
            )

            return self._calc_quote(
                passengers_count=len(data.passengers),
                seat_type_name=data.seat_type_name,
                options=data.options,
                option_rows=opts,
                per_passenger_options=data.per_passenger_options,
                discount=disc,
                _base_price=base_price,
                _currency=currency,
                _multiplier=multiplier,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _resolve_passengers(
        self, items: list[PassengerRefOrCreate]
    ) -> list[uuid.UUID]:
        ids: list[uuid.UUID] = []

        for item in items:
            if isinstance(item, PassengerRef):
                p = await self.repo.get_passenger(item.passenger_id)
                if not p or p.owner_id != self.current_user.user_id:
                    raise ValueError("Passenger not found or not owned")
                ids.append(p.passenger_id)

            elif isinstance(item, PassengerCreate):
                p = await self.repo.create_passenger(
                    owner_id=self.current_user.user_id,
                    first_name=item.first_name,
                    last_name=item.last_name,
                    contact_info=item.contact_info,
                )
                ids.append(p.passenger_id)

            else:
                raise ValueError("Unsupported passenger type")

        return ids

    async def create(self, data: CreateBookingIn) -> BookingOut:
        try:
            flight, seat, opts, disc = await self._load_refs(
                flight_id=data.flight_id,
                seat_type_name=data.seat_type_name,
                option_ids=[x.option_id for x in data.options],
                discount_code=data.discount_code,
            )
            passenger_ids = await self._resolve_passengers(data.passengers)

            base_price, currency, multiplier = await self._load_pricing(
                data.seat_type_name
            )

            q = self._calc_quote(
                passengers_count=len(passenger_ids),
                seat_type_name=data.seat_type_name,
                options=data.options,
                option_rows=opts,
                per_passenger_options=data.per_passenger_options,
                discount=disc,
                _base_price=base_price,
                _currency=currency,
                _multiplier=multiplier,
            )

            booking = await self.repo.create_booking(
                user_id=self.current_user.user_id,
                total_amount=q.total,
                discount_code=data.discount_code,
            )

            tickets: list[Ticket] = []
            for i, pid in enumerate(passenger_ids):
                price_i = (
                    q.breakdown_per_ticket[i].price
                    if i < len(q.breakdown_per_ticket)
                    else (q.total / len(passenger_ids))
                )
                t = Ticket(
                    ticket_number=self._gen_ticket_number(),
                    seat_number=None,
                    status=TicketStatus.BOOKED,
                    price=price_i,
                    booking_id=booking.booking_id,
                    passenger_id=pid,
                    flight_id=flight.flight_id,
                    seat_type_name=seat.type_name,
                )
                await self.repo.create_ticket(t)
                tickets.append(t)

            await self._apply_options_to_tickets(
                tickets, data.options, data.per_passenger_options
            )

            await self.repo.save()

            return BookingOut(
                booking_id=booking.booking_id,
                status=booking.status.value,
                total_amount=booking.total_amount,
                discount_code=booking.discount_code,
                flight=self._to_brief(flight),
                tickets=[
                    TicketOut(
                        ticket_number=t.ticket_number,
                        passenger_id=t.passenger_id,
                        seat_type_name=t.seat_type_name,
                        price=t.price,
                    )
                    for t in tickets
                ],
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _apply_options_to_tickets(
        self,
        tickets: Sequence[Ticket],
        options: Sequence[OptionPick],
        per_passenger: bool,
    ) -> None:
        if not options or not tickets:
            return

        ticket_numbers = [t.ticket_number for t in tickets]
        await self.session.execute(
            delete(ticket_options).where(
                ticket_options.c.ticket_number.in_(ticket_numbers)
            )
        )

        if per_passenger:
            rows = []
            for t in tickets:
                for op in options:
                    rows.append(
                        {
                            "ticket_number": t.ticket_number,
                            "option_id": op.option_id,
                            "qty": op.qty,
                            "price_override": None,
                        }
                    )
            if rows:
                await self.session.execute(insert(ticket_options), rows)
        else:
            rows = []
            for op in options:
                remaining = op.qty
                i = 0
                while remaining > 0:
                    t = tickets[i % len(tickets)]
                    take = min(remaining, 1)
                    rows.append(
                        {
                            "ticket_number": t.ticket_number,
                            "option_id": op.option_id,
                            "qty": take,
                            "price_override": None,
                        }
                    )
                    remaining -= take
                    i += 1
            if rows:
                await self.session.execute(insert(ticket_options), rows)

    async def get(self, booking_id: UUID) -> BookingOut:
        try:
            b = await self.repo.get_booking_for_owner(
                booking_id, self.current_user.user_id
            )
            if not b:
                raise ValueError("Booking not found")

            flight = (
                await self.repo.get_flight(b.tickets[0].flight_id)
                if b.tickets
                else None
            )
            if not flight:
                flight = (
                    await self.session.execute(
                        select(FlightRef).where(
                            FlightRef.flight_id == b.tickets[0].flight_id
                        )
                    )
                ).scalar_one_or_none()

            return BookingOut(
                booking_id=b.booking_id,
                status=b.status.value,
                total_amount=b.total_amount,
                discount_code=b.discount_code,
                flight=(
                    self._to_brief(flight)
                    if flight
                    else FlightBrief(
                        flight_id=uuid.uuid4(),
                        flight_number="N/A",
                        origin="N/A",
                        destination="N/A",
                        departure_time=dt.datetime.now(dt.timezone.utc),
                        arrival_time=dt.datetime.now(dt.timezone.utc),
                        status="scheduled",
                    )
                ),
                tickets=[
                    TicketOut(
                        ticket_number=t.ticket_number,
                        passenger_id=t.passenger_id,
                        seat_type_name=t.seat_type_name,
                        price=t.price,
                    )
                    for t in b.tickets
                ],
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def list_mine(self, *, limit: int = 50, offset: int = 0) -> MyBookingsOut:
        items, total = await self.repo.list_bookings_for_owner(
            self.current_user.user_id, limit=limit, offset=offset
        )
        result: list[BookingShortOut] = []
        for b in items:
            if b.tickets:
                f = await self.repo.get_flight(b.tickets[0].flight_id)
            else:
                f = None
            result.append(
                BookingShortOut(
                    booking_id=b.booking_id,
                    status=b.status.value,
                    total_amount=b.total_amount,
                    tickets_count=len(b.tickets),
                    flight=(
                        self._to_brief(f)
                        if f
                        else FlightBrief(
                            flight_id=uuid.uuid4(),
                            flight_number="N/A",
                            origin="N/A",
                            destination="N/A",
                            departure_time=dt.datetime.now(dt.timezone.utc),
                            arrival_time=dt.datetime.now(dt.timezone.utc),
                            status="scheduled",
                        )
                    ),
                )
            )
        return MyBookingsOut(items=result, total=total)

    async def confirm(self, booking_id: UUID) -> BookingOut:
        try:
            b = await self.repo.get_booking_for_owner(
                booking_id, self.current_user.user_id
            )
            if not b:
                raise ValueError("Booking not found")
            if b.status != BookingStatus.RESERVED:
                raise ValueError("Booking is not in RESERVED state")

            b.status = BookingStatus.PAID
            await self.repo.save()
            return await self.get(booking_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def cancel(self, booking_id: UUID) -> BookingOut:
        try:
            b = await self.repo.get_booking_for_owner(
                booking_id, self.current_user.user_id
            )
            if not b:
                raise ValueError("Booking not found")
            if b.status == BookingStatus.PAID:
                b.status = BookingStatus.REFUNDED
            elif b.status == BookingStatus.RESERVED:
                b.status = BookingStatus.CANCELED
            await self.repo.save()
            return await self.get(booking_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _load_pricing(self, seat_type_name: str) -> tuple[Decimal, str, Decimal]:
        cfg = (
            await self.session.execute(
                select(PricingConfig).where(PricingConfig.id == 1)
            )
        ).scalar_one_or_none()
        if not cfg:
            raise ValueError("Pricing configuration is not set")
        st = (
            await self.session.execute(
                select(SeatType).where(SeatType.type_name == seat_type_name)
            )
        ).scalar_one_or_none()
        if not st:
            raise ValueError("Seat type not found")

        return cfg.base_price, cfg.currency, st.multiplier

    @staticmethod
    def _gen_ticket_number() -> str:
        return f"FA{uuid.uuid4().hex[:10].upper()}"

    @staticmethod
    def _to_brief(f: FlightRef) -> FlightBrief:
        return FlightBrief(
            flight_id=f.flight_id,
            flight_number=f.flight_number,
            origin=f.origin,
            destination=f.destination,
            departure_time=f.departure_time,
            arrival_time=f.arrival_time,
            status=f.status.value if hasattr(f.status, "value") else str(f.status),
        )
