import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.vasif import Vasif
    from app.models.process import LiveProcessOperator


class Person(Base, UUIDMixin, TimestampMixin):
    """
    KİŞİ (Universal Conscious Actor).
    Sisteme giriş yapan, iradesi olan, mülkiyet kurabilen ve paylaşım (Vasıf) yapabilen tekil insan.
    Asla başka bir insanın mülkiyeti (owner_id) olamaz!
    """
    __tablename__ = "persons"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(150), unique=True, index=True, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    owned_assets: Mapped[List["Asset"]] = relationship(
        "Asset",
        foreign_keys="Asset.owner_person_id",
        back_populates="owner"
    )
    shares_received: Mapped[List["Vasif"]] = relationship(
        "Vasif",
        foreign_keys="Vasif.shared_with_person_id",
        back_populates="person",
        cascade="all, delete-orphan"
    )
    process_participations: Mapped[List["LiveProcessOperator"]] = relationship(
        "LiveProcessOperator",
        back_populates="person",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Person id={self.id} name='{self.name}' phone='{self.phone}'>"
