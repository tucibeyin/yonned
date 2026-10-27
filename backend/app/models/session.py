import secrets
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.process import LiveProcess


def generate_tracking_token() -> str:
    """Generates a secure, URL-safe magic link token for customer live tracking."""
    return secrets.token_urlsafe(32)


class AssetSession(Base, UUIDMixin, TimestampMixin):
    """
    HİZMET OTURUMU / GEÇİCİ ZİLYETLİK (Check-in & Service Session).
    Kalıcı mülkiyet (owner_person_id) asla değişmez!
    Bir Varlık (Kedi, Araba) bir şubeye geldiğinde oturum açılır,
    müşteriye tracking_token üretilir ve tüm canlı süreçler bu oturum altında icra edilir.
    """
    __tablename__ = "asset_sessions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    branch_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False
    )
    subject_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    status: Mapped[str] = mapped_column(
        String(50),
        default="checked_in",
        index=True,
        nullable=False
    )  # 'checked_in', 'in_service', 'ready_for_pickup', 'completed', 'cancelled'

    current_location_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True
    )
    tracking_token: Mapped[str] = mapped_column(
        String(100),
        default=generate_tracking_token,
        unique=True,
        index=True,
        nullable=False
    )
    
    check_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    check_out_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    subject_asset: Mapped["Asset"] = relationship(
        "Asset",
        foreign_keys=[subject_asset_id],
        back_populates="subject_sessions"
    )
    branch_asset: Mapped["Asset"] = relationship(
        "Asset",
        foreign_keys=[branch_asset_id]
    )
    current_location: Mapped[Optional["Asset"]] = relationship(
        "Asset",
        foreign_keys=[current_location_asset_id]
    )
    processes: Mapped[List["LiveProcess"]] = relationship(
        "LiveProcess",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="LiveProcess.started_at"
    )

    def __repr__(self) -> str:
        return f"<AssetSession id={self.id} subject_id={self.subject_asset_id} status='{self.status}' token='{self.tracking_token[:8]}...'>"
