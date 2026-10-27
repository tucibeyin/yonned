import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.person import Person
    from app.models.process import LiveProcess


class ProcessConsumable(Base, UUIDMixin, TimestampMixin):
    """
    SARF VE İLAÇ TÜKETİMİ (Consumables & Medicine Tracking).
    Sıfır Blokaj İlkesi: Sistemde tanımlı olmayan bir ilaç gelirse
    'custom_name' ile anında kaydedilir; operasyon asla durdurulmaz!
    """
    __tablename__ = "process_consumables"

    process_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("live_processes.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    consumable_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True
    )
    custom_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)  # JIT Girişi (Sıfır Blokaj)
    barcode_scanned: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1.0, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="adet", nullable=False)  # adet, ml, mg, lt, doz
    
    administered_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="SET NULL"),
        nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    process: Mapped["LiveProcess"] = relationship("LiveProcess", back_populates="consumables")
    consumable_asset: Mapped[Optional["Asset"]] = relationship("Asset", foreign_keys=[consumable_asset_id])
    administered_by: Mapped[Optional["Person"]] = relationship("Person", foreign_keys=[administered_by_id])

    @property
    def display_name(self) -> str:
        """Katalog adını veya JIT girilen serbest adı döner."""
        if self.consumable_asset:
            return self.consumable_asset.name
        return self.custom_name or "Tanımsız Sarf"
