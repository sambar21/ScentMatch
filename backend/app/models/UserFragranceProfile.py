import uuid
from app.core.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

class UserScentProfile(Base):
    __tablename__ = "user_scent_profiles"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
        comment="User this profile belongs to"
    )
    
    
    liked_notes = Column(
        JSONB,
        nullable=True,
        comment="Notes user manually selected: ['vanilla', 'bergamot', 'rose']"
    )
    
    liked_accords = Column(
        JSONB,
        nullable=True,
        comment="Accords user manually selected: ['fresh', 'woody', 'citrus']"
    )
    
    
    onboarding_complete = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Has user completed full onboarding"
    )
    
    onboarding_complete_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When they finished onboarding"
    )
    
    
    top_notes_from_ratings = Column(
        JSONB,
        nullable=True,
        comment="Notes aggregated from their actual ratings: {'vanilla': 8, 'rose': 5}"
    )
    
    top_accords_from_ratings = Column(
        JSONB,
        nullable=True,
        comment="Accords aggregated from their actual ratings: {'fresh': 7}"
    )
    
    profile_last_computed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When rating-based aggregates were last computed"
    )
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_user_fragrance_profiles_onboarding', 'onboarding_complete'),
    )

class UserFragrance(Base):
    """User's owned/liked fragrances"""
    __tablename__ = "user_fragrances"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    fragrance_id = Column(UUID(as_uuid=True), ForeignKey('fragrances.id', ondelete='CASCADE'))
    
    source = Column(String(50), comment="'onboarding', 'added_later', 'wishlist'")
    owned = Column(Boolean, default=True)
    
    added_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'fragrance_id'),
    )