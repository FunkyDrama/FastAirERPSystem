import uuid
import datetime as dt
from pydantic import BaseModel, Field

from services.staff_service.app.schemas.airplane import AirplaneCreateIn


class FlightCreateIn(BaseModel):
    flight_number: str = Field(..., examples=["FA1234"])
    origin: str = Field(..., examples=["KBP"])
    destination: str = Field(..., examples=["WAW"])
    departure_time: dt.datetime
    arrival_time: dt.datetime
    airplane_id: uuid.UUID | None = Field(
        None,
        examples=["8f3f6b93-4a6d-4f92-9ad5-6e6ff7f39abc"],
    )
    airplane: AirplaneCreateIn | None = None


class FlightOut(BaseModel):
    flight_id: uuid.UUID
    flight_number: str
    origin: str
    destination: str
    departure_time: dt.datetime
    arrival_time: dt.datetime
    airplane_id: uuid.UUID
    status: str

    class Config:
        from_attributes = True
