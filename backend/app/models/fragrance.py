import uuid
from typing import List, Optional

from app.core.database import Base
from sqlalchemy import (
    ARRAY, Boolean, Column, DateTime, Numeric, Index, Integer, 
    String, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Brand(Base):
    __tablename__ = "brands"

    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique brand identifier"
    )

    # Brand Information
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Brand name"
    )

    country = Column(
        String(100),
        nullable=True,
        comment="Country of origin"
    )

    website = Column(
        String(255),
        nullable=True,
        comment="Official website URL"
    )

    # Audit Fields
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Brand creation timestamp"
    )

    # Relationships
    fragrances = relationship("Fragrance", back_populates="brand")

    def __repr__(self) -> str:
        return f"<Brand(id={self.id}, name={self.name})>"


class FragranceFamily(Base):
    __tablename__ = "fragrance_families"

    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique family identifier"
    )

    # Family Information
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="Fragrance family name"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Family description"
    )

    # Audit Fields
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Family creation timestamp"
    )

    def __repr__(self) -> str:
        return f"<FragranceFamily(id={self.id}, name={self.name})>"


class Fragrance(Base):
    __tablename__ = "fragrances"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique fragrance identifier"
    )

    # Basic Information
    name = Column(
        String(255),
        nullable=False,
        comment="Fragrance name"
    )

    brand_name = Column(
        String(255),
        nullable=True,
        comment="Brand name as text (for scraping flexibility)"
    )

    brand_id = Column(
        Integer,
        ForeignKey("brands.id"),
        nullable=True,
        comment="Optional normalized brand reference"
    )

    # Product Details
    release_year = Column(
        Integer,
        nullable=True,
        comment="Year of release"
    )

    gender = Column(
        String(20),
        nullable=True,
        comment="masculine, feminine, unisex"
    )

    concentration = Column(
        String(50),
        nullable=True,
        comment="EDT, EDP, Parfum, Cologne, etc."
    )

    perfumer = Column(
        String(255),
        nullable=True,
        comment="Perfumer/nose who created it"
    )

    # Scraped Notes Arrays
    top_notes = Column(
        ARRAY(String),
        nullable=True,
        default=list,
        comment="Array of top note names"
    )

    middle_notes = Column(
        ARRAY(String),
        nullable=True,
        default=list,
        comment="Array of middle note names"
    )

    base_notes = Column(
        ARRAY(String),
        nullable=True,
        default=list,
        comment="Array of base note names"
    )

    main_accords = Column(
        ARRAY(String),
        nullable=True,
        default=list,
        comment="Array of main scent categories"
    )

    # Ratings and Performance
    average_rating = Column(
        Numeric(3, 2),
        nullable=False,
        default=0.00,
        comment="Average user rating (0.00-5.00)"
    )

    total_ratings = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of ratings"
    )

    longevity_rating = Column(
        Numeric(3, 2),
        nullable=True,
        comment="Average longevity rating"
    )

    sillage_rating = Column(
        Numeric(3, 2),
        nullable=True,
        comment="Average sillage/projection rating"
    )

    # Descriptive Content
    description = Column(
        Text,
        nullable=True,
        comment="Fragrance description"
    )

    image_url = Column(
        String(500),
        nullable=True,
        comment="Main product image URL"
    )

    # Status
    discontinued = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether fragrance is discontinued"
    )

    # Audit Fields
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp"
    )

    # Relationships
    brand = relationship("Brand", back_populates="fragrances")
    reviews = relationship("ScrapedReview", back_populates="fragrance")
    scraping_logs = relationship("FragranceScrapingLog", back_populates="fragrance")

    # Database Indexes for Performance
    __table_args__ = (
        Index("idx_fragrances_brand_name", "brand_name"),
        Index("idx_fragrances_gender", "gender"),
        Index("idx_fragrances_rating", "average_rating"),
        Index("idx_fragrances_updated", "updated_at"),
        Index("idx_fragrances_top_notes", "top_notes", postgresql_using="gin"),
        Index("idx_fragrances_middle_notes", "middle_notes", postgresql_using="gin"),
        Index("idx_fragrances_base_notes", "base_notes", postgresql_using="gin"),
        # Unique constraint
        Index("uq_fragrance_name_brand", "name", "brand_name", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Fragrance(id={self.id}, name={self.name}, brand={self.brand_name})>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "brand_name": self.brand_name,
            "gender": self.gender,
            "concentration": self.concentration,
            "release_year": self.release_year,
            "perfumer": self.perfumer,
            "top_notes": self.top_notes or [],
            "middle_notes": self.middle_notes or [],
            "base_notes": self.base_notes or [],
            "main_accords": self.main_accords or [],
            "average_rating": float(self.average_rating) if self.average_rating else 0.0,
            "total_ratings": self.total_ratings,
            "longevity_rating": float(self.longevity_rating) if self.longevity_rating else None,
            "sillage_rating": float(self.sillage_rating) if self.sillage_rating else None,
            "description": self.description,
            "image_url": self.image_url,
            "discontinued": self.discontinued,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def all_notes(self) -> List[str]:
        """Get all notes combined"""
        all_notes = []
        if self.top_notes:
            all_notes.extend(self.top_notes)
        if self.middle_notes:
            all_notes.extend(self.middle_notes)
        if self.base_notes:
            all_notes.extend(self.base_notes)
        return all_notes

    def has_note(self, note_name: str) -> bool:
        """Check if fragrance contains a specific note"""
        note_name_lower = note_name.lower()
        return any(
            note_name_lower in (note.lower() for note in notes)
            for notes in [self.top_notes or [], self.middle_notes or [], self.base_notes or []]
            if notes
        )


class ScrapedReview(Base):
    __tablename__ = "scraped_reviews"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique review identifier"
    )

    # Foreign Key
    fragrance_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fragrances.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to fragrance"
    )

    # Review Content
    rating = Column(
        Integer,
        nullable=True,
        comment="Rating 1-5 scale"
    )

    review_text = Column(
        Text,
        nullable=True,
        comment="Review text content"
    )

    review_title = Column(
        String(255),
        nullable=True,
        comment="Review title"
    )

    # Performance Ratings
    longevity = Column(
        Integer,
        nullable=True,
        comment="Longevity rating 1-10"
    )

    sillage = Column(
        Integer,
        nullable=True,
        comment="Sillage rating 1-10"
    )

    # Context
    season = Column(
        String(50),
        nullable=True,
        comment="Season context"
    )

    occasion = Column(
        String(100),
        nullable=True,
        comment="Occasion context"
    )

    age_group = Column(
        String(50),
        nullable=True,
        comment="Age group of reviewer"
    )

    # Reviewer Info (anonymized)
    reviewer_username = Column(
        String(100),
        nullable=True,
        comment="Anonymized reviewer username"
    )

    reviewer_gender = Column(
        String(20),
        nullable=True,
        comment="Reviewer gender"
    )

    # Sentiment Analysis
    sentiment_score = Column(
        Numeric(3, 2),
        nullable=True,
        comment="Sentiment score -1 to 1"
    )

    # Source Tracking
    source_site = Column(
        String(50),
        nullable=True,
        comment="Source website"
    )

    source_url = Column(
        String(500),
        nullable=True,
        comment="Source URL"
    )

    external_review_id = Column(
        String(100),
        nullable=True,
        comment="External review ID for deduplication"
    )

    # Timestamps
    review_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Original review date"
    )

    scraped_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When review was scraped"
    )

    # Relationships
    fragrance = relationship("Fragrance", back_populates="reviews")

    # Database Indexes
    __table_args__ = (
        Index("idx_reviews_fragrance", "fragrance_id"),
        Index("idx_reviews_rating", "rating"),
        Index("idx_reviews_source", "source_site"),
        Index("idx_reviews_scraped", "scraped_at"),
        # Prevent duplicate scraping
        Index("uq_review_source_external", "source_site", "external_review_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<ScrapedReview(id={self.id}, fragrance_id={self.fragrance_id}, rating={self.rating})>"


class FragranceScrapingLog(Base):
    __tablename__ = "fragrance_scraping_log"

    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique log entry identifier"
    )

    # Foreign Key
    fragrance_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fragrances.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to fragrance"
    )

    # Scraping Details
    source_site = Column(
        String(50),
        nullable=False,
        comment="Source website name"
    )

    source_url = Column(
        String(500),
        nullable=True,
        comment="Source URL"
    )

    external_id = Column(
        String(255),
        nullable=True,
        comment="External fragrance ID"
    )

    # Status
    scraped_successfully = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether scraping was successful"
    )

    scrape_error_message = Column(
        Text,
        nullable=True,
        comment="Error message if scraping failed"
    )

    reviews_scraped = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of reviews scraped"
    )

    # Timestamp
    last_scrape_attempt = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Last scrape attempt timestamp"
    )

    # Relationships
    fragrance = relationship("Fragrance", back_populates="scraping_logs")

    # Database Indexes
    __table_args__ = (
        Index("idx_scraping_log_fragrance", "fragrance_id"),
        Index("idx_scraping_log_source", "source_site"),
        Index("idx_scraping_log_success", "scraped_successfully"),
        # Unique constraint
        Index("uq_scraping_log_fragrance_source", "fragrance_id", "source_site", unique=True),
    )

    def __repr__(self) -> str:
        return f"<FragranceScrapingLog(fragrance_id={self.fragrance_id}, source={self.source_site}, success={self.scraped_successfully})>"