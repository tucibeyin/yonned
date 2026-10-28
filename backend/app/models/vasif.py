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
    VASIF / ASSET SHARE (The Universal CRUD Permission Contract).
    Bir Varlık Sahibi (İnsan), varlığını dilediği başka bir İnsanla paylaşır.
    Yetkiler birbirinden bağımsız 4 temel CRUD fiilinden ibarettir:
    1. can_create: Ekle / Yeni süreç, alt mekan, sarf veya kayıt oluşturabilme
    2. can_read:   Oku / Varlık durumunu, canlı takibi, geçmişi ve fotoğrafları görüntüleyebilme
    3. can_update: Güncelle / Var olan süreç notlarını, durumları veya varlık detaylarını değiştirebilme
    4. can_delete: Sil / Varlığı, süreci veya kaydı iptal edebilme/silebilme
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

    # 4 Atomic CRUD Verbs:
    can_create: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_read: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_update: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="shares")
    person: Mapped["Person"] = relationship("Person", foreign_keys=[shared_with_person_id], back_populates="shares_received")

    def __repr__(self) -> str:
        return (
            f"<Vasif asset_id={self.asset_id} person_id={self.shared_with_person_id} "
            f"C={int(self.can_create)} R={int(self.can_read)} U={int(self.can_update)} D={int(self.can_delete)}>"
        )


# English alias
AssetShare = Vasif
