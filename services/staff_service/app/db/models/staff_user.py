import enum
import uuid
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from services.staff_service.app.db.base import Base


class StaffRole(str, enum.Enum):
    """
    Enumeration for various staff roles.

    This class serves as a collection of constant values representing specific
    staff roles within an organization. It is implemented as a subclass of
    both `str` and `enum.Enum`, allowing the string representation of the roles
    while maintaining the benefits of enumerations.

    :ivar GATE_MANAGER: Represents the role of a gate manager in the organization.
                        This role might involve responsibilities like overseeing
                        gate operations.
    :type GATE_MANAGER: str
    :ivar CHECKIN_MANAGER: Represents the role of a check-in manager. This role
                           might include responsibilities like managing check-in
                           operations and ensuring a smooth process for passengers.
    :type CHECKIN_MANAGER: str
    :ivar SUPERVISOR: Represents the role of a supervisor. This role likely
                      involves oversight responsibilities, supervising other
                      roles, and ensuring overall process efficiency.
    :type SUPERVISOR: str
    """

    GATE_MANAGER = "gate_manager"
    CHECKIN_MANAGER = "checkin_manager"
    SUPERVISOR = "supervisor"


class StaffUser(Base):
    """
    Represents a staff user in the system.

    This class defines the structure of a staff user, including their basic
    information such as email, role, and their unique user identifier within
    the organization. It is primarily used to manage and store information
    about staff users and their responsibilities within the system.

    :ivar user_id: Unique identifier for the staff user.
    :type user_id: uuid.UUID
    :ivar email: The email address associated with the staff user. Must be
        unique and cannot be null.
    :type email: str
    :ivar password_hash: The hashed password associated with the staff user.
        Helps ensure user authentication data remains secure.
    :type password_hash: str
    :ivar role: The role assigned to the staff user within the organization.
        Defined using the `StaffRole` enumeration.
    :type role: StaffRole
    """

    __tablename__ = "staff_users"

    user_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[StaffRole] = mapped_column(
        Enum(StaffRole, name="staff_role_enum", native_enum=False),
        nullable=False,
        default=StaffRole.GATE_MANAGER,
    )
