from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin
from app.models.category import Category
from app.models.user import User


class ListingType(StrEnum):
    LOST = "lost"
    FOUND = "found"


class ListingStatus(StrEnum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class Listing(TimestampMixin, Base):
    __tablename__ = "listings"
    __table_args__ = (
        CheckConstraint("type IN ('lost', 'found')", name="type_values"),
        CheckConstraint(
            "status IN ('active', 'resolved', 'archived')",
            name="status_values",
        ),
        CheckConstraint("x >= 0 AND x <= 100", name="x_range"),
        CheckConstraint("y >= 0 AND y <= 100", name="y_range"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    type: Mapped[ListingType] = mapped_column(
        Enum(
            ListingType,
            name="listing_type",
            native_enum=False,
            values_callable=lambda enum_type: [item.value for item in enum_type],
            validate_strings=True,
        ),
        nullable=False,
        index=True,
    )
    status: Mapped[ListingStatus] = mapped_column(
        Enum(
            ListingStatus,
            name="listing_status",
            native_enum=False,
            values_callable=lambda enum_type: [item.value for item in enum_type],
            validate_strings=True,
        ),
        default=ListingStatus.ACTIVE,
        server_default=ListingStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)

    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    author: Mapped[User] = relationship(back_populates="listings", lazy="selectin")
    category: Mapped[Category] = relationship(back_populates="listings", lazy="selectin")
