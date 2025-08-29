import uuid

from app.core.database import Base
from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique user identifier",
    )

    # Authentication Fields
    email = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="User's email address for login",
    )

    hashed_password = Column(
        String(255), nullable=False, comment="Bcrypt hashed password"
    )

    # Profile Fields
    display_name = Column(String(100), nullable=True, comment="User's display name")

    first_name = Column(String(50), nullable=True, comment="User's first name")

    last_name = Column(String(50), nullable=True, comment="User's last name")

    # Account Status Management
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the user account is active",
    )

    is_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the user's email is verified",
    )

    is_superuser = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the user has admin privileges",
    )

    # Audit Fields
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Account creation timestamp",
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last profile update timestamp",
    )

    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last successful login timestamp",
    )

    # Profile Enhancement Fields
    bio = Column(Text, nullable=True, comment="User's biographical information")

    avatar_url = Column(
        String(500), nullable=True, comment="URL to user's profile picture"
    )

    # Login tracking for security
    failed_login_attempts = Column(
        Integer, nullable=False, default=0, comment="Count of failed login attempts"
    )

    last_failed_login = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of last failed login attempt",
    )

    # Database Indexes for Performance
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_active", "is_active"),
        Index("idx_users_active_verified", "is_active", "is_verified"),
        Index("idx_users_created_at", "created_at"),
        Index("idx_users_display_name", "display_name"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, active={self.is_active})>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "display_name": self.display_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
        }

    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.email.split("@")[0]

    def is_account_locked(self) -> bool:
        return self.failed_login_attempts >= 5

    def reset_failed_attempts(self) -> None:
        self.failed_login_attempts = 0
        self.last_failed_login = None
