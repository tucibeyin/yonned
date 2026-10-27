import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.person import Person


class Vasif(Base, UUIDMixin, TimestampMixin):
    """
    VASIF / ASSET SHARE (The Universal Permission Grant Contract).
    Bir Varlık Sahibi (İnsan), varlığını dilediği başka bir İnsanla paylaşır.
    Yetkiler birbirinden bağımsız 4 temel fiilden ibarettir:
    1. Görüntüle (can_view)
    2. Değiştir / Güncelle (can_edit)
    3. Ekle (can_add)
    4. Sil (can_delete)
    """
    __tablename__ = "asset_shares"
    __table_args__ = (
        UniqueConstraint("asset_id", "shared_with_person_id", name="uq_asset_shares_asset_person"),
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    shared_with_person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # 4 Atomic Verbs:
    can_view: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_add: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="shares")
    person: Mapped["Person"] = relationship("Person", foreign_keys=[shared_with_person_id], back_populates="shares_received")

    def __repr__(self) -> str:
        return (
            f"<Vasif asset_id={self.asset_id} person_id={self.shared_with_person_id} "
            f"V={int(self.can_view)} E={int(self.can_edit)} A={int(self.can_add)} D={int(self.can_delete)}>"
        )
