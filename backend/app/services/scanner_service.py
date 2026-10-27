import uuid
from typing import Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.models.session import AssetSession
from app.schemas.scanner import ScanResolveResponse


class ScannerService:
    """
    Evrensel Kamera Vizörü Çözümleyici (Universal Scanner Resolver).
    Tek bir vizörden kafes QR'ı, hasta/araç etiketi veya ilaç barkodunu çözer.
    Sistemde kayıtlı değilse asla personeli bloklamaz (prompt_create = True).
    """

    LOCATION_TYPES = {"organization", "branch", "floor", "room", "station", "cage", "bay"}
    SUBJECT_TYPES = {"pet", "vehicle"}
    CONSUMABLE_TYPES = {"consumable", "device", "part", "medicine"}

    @classmethod
    async def resolve(
        cls,
        db: AsyncSession,
        raw_code: str,
        context_branch_id: Optional[uuid.UUID] = None
    ) -> ScanResolveResponse:
        # 1. QR Kodu veya Tanımlayıcı (Barkod/Plaka/Çip) ile Aset Ara
        stmt = select(Asset).where(
            or_(
                Asset.qr_code == raw_code,
                Asset.identifier == raw_code
            )
        )
        result = await db.execute(stmt)
        asset = result.scalar_one_or_none()

        # 2. Varlık Bulunamadıysa: SIFIR BLOKAJ İLKESİ (JIT Kayıt İstemcisi)
        if not asset:
            return ScanResolveResponse(
                match_type="unknown",
                prompt_create=True,
                details={
                    "scanned_code": raw_code,
                    "message": "Bu kod sistemde henüz kayıtlı değil. Hızlıca tanımlayıp işleme devam edebilirsiniz."
                }
            )

        # 3. Varlık Tipine Göre Eşleşme Ayrıştırması
        match_type = "unknown"
        if asset.asset_type in cls.LOCATION_TYPES:
            match_type = "location"
        elif asset.asset_type in cls.SUBJECT_TYPES:
            match_type = "subject"
        elif asset.asset_type in cls.CONSUMABLE_TYPES:
            match_type = "consumable"

        # 4. Eğer bir özne ise (Kedi, Araba), aktif bir oturumu (AssetSession) var mı kontrol et:
        active_session_id = None
        if match_type == "subject":
            session_stmt = select(AssetSession.id).where(
                AssetSession.subject_asset_id == asset.id,
                AssetSession.status.in_(["checked_in", "in_service", "ready_for_pickup"])
            ).order_by(AssetSession.check_in_at.desc())
            session_result = await db.execute(session_stmt)
            active_session_id = session_result.scalar_one_or_none()

        return ScanResolveResponse(
            match_type=match_type,
            asset_id=asset.id,
            name=asset.name,
            asset_type=asset.asset_type,
            identifier=asset.identifier,
            active_session_id=active_session_id,
            prompt_create=False,
            details={
                "current_location_id": str(asset.current_location_asset_id) if asset.current_location_asset_id else None,
                "capacity": asset.capacity,
                "owner_person_id": str(asset.owner_person_id) if asset.owner_person_id else None
            }
        )
