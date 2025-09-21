import uuid
from pydantic import BaseModel, EmailStr

from services.staff_service.app.db.models.staff_user import StaffRole


class StaffUserCreateIn(BaseModel):
    email: EmailStr
    password: str
    role: StaffRole


class StaffUserOut(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    role: StaffRole

    class Config:
        from_attributes = True
