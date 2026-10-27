import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.models.vasif import Vasif


class PermissionService:
    """
    4-Fiil Yetki Çözümleme Servisi (Universal 4-Verbs Permission Engine).
    Kurallar:
    1. Varlık Sahibi (owner_person_id == person_id) ise 4 fiilin tümü (Görüntüle, Değiştir, Ekle, Sil) AÇIKTIR.
    2. Doğrudan 'asset_shares' tablosunda bir vasıf kaydı varsa o izinler geçerlidir.
    3. Doğrudan kayıt yoksa, hiyerarşik olarak ebeveyn varlıklara (parent_id) bakılır (Cascade Yetki).
    """

    @classmethod
    async def resolve_permissions(
        cls,
        db: AsyncSession,
        asset_id: uuid.UUID,
        person_id: uuid.UUID
    ) -> dict[str, bool]:
        """
        Belirtilen varlık ve kişi için 4 temel fiili çözümler:
        {'can_view': bool, 'can_edit': bool, 'can_add': bool, 'can_delete': bool}
        """
        default_perms = {
            "can_view": False,
            "can_edit": False,
            "can_add": False,
            "can_delete": False,
        }

        # 1. Varlık ve Sahiplik Kontrolü
        current_asset_id: Optional[uuid.UUID] = asset_id
        
        while current_asset_id:
            asset_stmt = select(Asset).where(Asset.id == current_asset_id)
            result = await db.execute(asset_stmt)
            asset = result.scalar_one_or_none()
            
            if not asset:
                break

            # Eğer kişi bu varlığın doğrudan sahibiyse (patron veya evcil hayvan/araç sahibi):
            if asset.owner_person_id == person_id:
                return {
                    "can_view": True,
                    "can_edit": True,
                    "can_add": True,
                    "can_delete": True,
                }

            # 2. Vasıf (Asset Shares) Tablosunu Sorgula
            vasif_stmt = select(Vasif).where(
                Vasif.asset_id == current_asset_id,
                Vasif.shared_with_person_id == person_id
            )
            vasif_result = await db.execute(vasif_stmt)
            vasif = vasif_result.scalar_one_or_none()

            if vasif:
                return {
                    "can_view": vasif.can_view,
                    "can_edit": vasif.can_edit,
                    "can_add": vasif.can_add,
                    "can_delete": vasif.can_delete,
                }

            # 3. Üst varlığa tırman (Örn: Kafes -> Oda -> Kat -> Şube)
            current_asset_id = asset.parent_id

        return default_perms

    @classmethod
    async def check_permission(
        cls,
        db: AsyncSession,
        asset_id: uuid.UUID,
        person_id: uuid.UUID,
        verb: str  # 'view', 'edit', 'add', 'delete'
    ) -> bool:
        """Tek bir fiil için izin kontrolü yapar."""
        perms = await cls.resolve_permissions(db, asset_id, person_id)
        return perms.get(f"can_{verb}", False)
