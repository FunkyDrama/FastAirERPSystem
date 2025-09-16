from pydantic import BaseModel, EmailStr

from services.staff_service.app.db.models.staff_user import StaffRole


class StaffUserCreateIn(BaseModel):
    email: EmailStr
    password: str
    role: StaffRole
