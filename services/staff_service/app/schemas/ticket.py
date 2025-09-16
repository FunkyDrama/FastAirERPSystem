import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class PassengerOnFlight(BaseModel):
    passenger_name: str
    ticket_number: str
    flight_number: str
    seat_number: str | None = None
    seat_type: str


class UpdateTicketStatus(BaseModel):
    ticket_number: str
    status: str


class PassengersOnFlight(BaseModel):
    passengers: list[PassengerOnFlight]


class QRScanIn(BaseModel):
    booking_id: str
    ticket_number: str


class QRScanOut(BaseModel):
    passenger_name: str
    flight_id: uuid.UUID
    seat_number: str
    seat_type: str
    status: str


class RevenueSchema(BaseModel):
    flight_id: str = Field(..., description="Flight ID or 'total' for overall revenue")
    revenue: Decimal = Field(..., description="Total revenue amount or flight revenue")
