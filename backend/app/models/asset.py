import uuid
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.vasif import Vasif
    from app.models.session import AssetSession


class Asset(Base, UUIDMixin, TimestampMixin):
    """
    EVRENSEL VARLIK (Universal Asset / Property / Subject / Spatial Container).
    Özyinelemeli ağaç (parent_id) yapısıyla mekanları, donanımları, sarfları ve
    üzerinde işlem yapılan özneleri (kedi, araba) modeller.
    Varlıklar asla başka bir varlığı paylaşamaz ve süreç başlatamaz!
    """
    __tablename__ = "assets"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    owner_person_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    owner_type: Mapped[str] = mapped_column(String(20), default="business", nullable=False)  # 'business' | 'customer'
    asset_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    # Types: 'organization', 'branch', 'floor', 'room', 'station', 'cage', 'bay', 'device', 'consumable', 'pet', 'vehicle'

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    identifier: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)  # Plaka, Çip No, IMEI
    qr_code: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    
    current_location_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True
    )
    capacity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    owner: Mapped[Optional["Person"]] = relationship("Person", foreign_keys=[owner_person_id], back_populates="owned_assets")
    
    parent: Mapped[Optional["Asset"]] = relationship(
        "Asset",
        foreign_keys=[parent_id],
        remote_side=lambda: [Asset.id],
        back_populates="children"
    )
    children: Mapped[List["Asset"]] = relationship(
        "Asset",
        foreign_keys=[parent_id],
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    current_location: Mapped[Optional["Asset"]] = relationship(
        "Asset",
        foreign_keys=[current_location_asset_id],
        remote_side=lambda: [Asset.id],
        post_update=True
    )

    shares: Mapped[List["Vasif"]] = relationship(
        "Vasif",
        back_populates="asset",
        cascade="all, delete-orphan"
    )

    subject_sessions: Mapped[List["AssetSession"]] = relationship(
        "AssetSession",
        foreign_keys="AssetSession.subject_asset_id",
        back_populates="subject_asset"
    )

    def __repr__(self) -> str:
        return f"<Asset id={self.id} name='{self.name}' type='{self.asset_type}' qr='{self.qr_code}'>"
