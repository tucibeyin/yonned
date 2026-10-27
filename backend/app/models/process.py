import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.person import Person
    from app.models.session import AssetSession
    from app.models.consumable import ProcessConsumable


class ProcessDefinition(Base, UUIDMixin, TimestampMixin):
    """Süreç Şablon Kütüphanesi (Process Blueprints)."""
    __tablename__ = "process_definitions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_instant: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 0 saniyelik anlık olay mı?
    default_location_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_customer_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    customer_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metadata_schema: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class ProcessDefinitionRelation(Base, UUIDMixin):
    """Süreç Şablonları Arasındaki Ebeveyn-Çocuk İlişkisi."""
    __tablename__ = "process_definition_relations"

    parent_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("process_definitions.id", ondelete="CASCADE"),
        nullable=False
    )
    child_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("process_definitions.id", ondelete="CASCADE"),
        nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class LiveProcess(Base, UUIDMixin, TimestampMixin):
    """
    CANLI SÜREÇ / ZAMANSAL EYLEM (Temporal Asset / Action).
    Bir operatörün (İnsan) bir varlık üzerinde icra ettiği süreç.
    Başlar, duraklar, tamamlanır veya anlık (0 sn) olay olarak işlenir.
    """
    __tablename__ = "live_processes"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    definition_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("process_definitions.id", ondelete="SET NULL"),
        nullable=True
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("live_processes.id", ondelete="CASCADE"),
        nullable=True
    )
    previous_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("live_processes.id", ondelete="SET NULL"),
        nullable=True
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_instant: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="queued",
        index=True,
        nullable=False
    )  # 'queued', 'running', 'paused', 'completed', 'cancelled'

    location_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True
    )
    assigned_person_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="SET NULL"),
        nullable=True
    )
    completed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="SET NULL"),
        nullable=True
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    is_customer_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    customer_notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photos: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    session: Mapped["AssetSession"] = relationship("AssetSession", back_populates="processes")
    location: Mapped[Optional["Asset"]] = relationship("Asset", foreign_keys=[location_asset_id])
    assigned_person: Mapped[Optional["Person"]] = relationship("Person", foreign_keys=[assigned_person_id])
    completed_by: Mapped[Optional["Person"]] = relationship("Person", foreign_keys=[completed_by_id])
    
    operators: Mapped[List["LiveProcessOperator"]] = relationship(
        "LiveProcessOperator",
        back_populates="process",
        cascade="all, delete-orphan"
    )
    consumables: Mapped[List["ProcessConsumable"]] = relationship(
        "ProcessConsumable",
        back_populates="process",
        cascade="all, delete-orphan"
    )

    def calculate_duration(self) -> int:
        """Hesaplanan saniye süresini günceller."""
        if self.is_instant:
            self.duration_seconds = 0
            return 0
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
            return self.duration_seconds
        return 0


class LiveProcessOperator(Base, UUIDMixin):
    """Süreçte Görev Alan Operatörler / Asistanlar."""
    __tablename__ = "live_process_operators"

    process_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("live_processes.id", ondelete="CASCADE"),
        nullable=False
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="operator", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    process: Mapped["LiveProcess"] = relationship("LiveProcess", back_populates="operators")
    person: Mapped["Person"] = relationship("Person", back_populates="process_participations")
