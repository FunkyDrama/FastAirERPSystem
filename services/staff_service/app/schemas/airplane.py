from pydantic import BaseModel, Field


class AirplaneCreateIn(BaseModel):
    model: str = Field(..., examples=["Airbus A320"])
    total_seats: int = Field(..., examples=[180])
