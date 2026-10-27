from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_person
from app.core.database import get_db
from app.models.asset import Asset
from app.models.person import Person
from app.models.vasif import Vasif
from app.schemas.asset import AssetResponse
from app.schemas.person import PersonResponse

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.get("/me", response_model=PersonResponse)
async def get_me(current_person: Person = Depends(get_current_person)):
    """Oturum açmış olan aktif kişinin profilini döner."""
    return PersonResponse.model_validate(current_person)


@router.get("/me/wallet")
async def get_my_asset_wallet(
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    KİŞİSEL VARLIK CÜZDANI (Dual Identity Wallet).
    Kişinin hem kendi sahip olduğu varlıkları (Patronu olduğu klinik, kedisi, arabası)
    hem de başkaları tarafından kendisine Vasıf ile paylaşılan varlıkları tek ekranda döner.
    """
    # 1. Sahip olduğu varlıklar
    owned_stmt = select(Asset).where(
        Asset.owner_person_id == current_person.id,
        Asset.is_active.is_(True)
    )
    owned_res = await db.execute(owned_stmt)
    owned_assets = owned_res.scalars().all()

    # 2. Kendisine paylaşılan varlıklar
    shared_stmt = select(Asset, Vasif).join(
        Vasif, Vasif.asset_id == Asset.id
    ).where(
        Vasif.shared_with_person_id == current_person.id,
        Asset.is_active.is_(True)
    )
    shared_res = await db.execute(shared_stmt)
    shared_rows = shared_res.all()

    shared_list = []
    for asset, vasif in shared_rows:
        shared_list.append({
            "asset": AssetResponse.model_validate(asset),
            "permissions": {
                "can_view": vasif.can_view,
                "can_edit": vasif.can_edit,
                "can_add": vasif.can_add,
                "can_delete": vasif.can_delete,
            }
        })

    return {
        "person": PersonResponse.model_validate(current_person),
        "owned_assets": [AssetResponse.model_validate(a) for a in owned_assets],
        "shared_assets": shared_list
    }
