import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_person
from app.core.database import get_db
from app.models.asset import Asset
from app.models.person import Person
from app.models.vasif import Vasif
from app.schemas.vasif import VasifCreate, VasifResponse, VasifUpdate

router = APIRouter(prefix="/vasifs", tags=["Vasif / Asset Shares"])


@router.post("", response_model=VasifResponse, status_code=status.HTTP_201_CREATED)
async def grant_vasif(
    payload: VasifCreate,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """
    VARLIK PAYLAŞIMI VE VASIF TANIMLAMA (4-Verb Share).
    Kişi kendi asetin patronudur. Paylaştığı kişinin haklarını
    Görüntüle, Değiştir, Ekle, Sil olarak belirler.
    Yalnızca varlığın asıl sahibi (owner_person_id) paylaşım yapabilir!
    """
    asset_stmt = select(Asset).where(Asset.id == payload.asset_id)
    asset_res = await db.execute(asset_stmt)
    asset = asset_res.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paylaşılmak istenen varlık bulunamadı.")

    if asset.owner_person_id != current_person.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yalnızca varlığın asıl sahibi paylaşım yapabilir ve vasıf atayabilir."
        )

    # Var olan vasıf kaydı var mı kontrol et (Upsert mantığı)
    vasif_stmt = select(Vasif).where(
        Vasif.asset_id == payload.asset_id,
        Vasif.shared_with_person_id == payload.shared_with_person_id
    )
    vasif_res = await db.execute(vasif_stmt)
    vasif = vasif_res.scalar_one_or_none()

    if vasif:
        vasif.can_view = payload.can_view
        vasif.can_edit = payload.can_edit
        vasif.can_add = payload.can_add
        vasif.can_delete = payload.can_delete
    else:
        vasif = Vasif(
            asset_id=payload.asset_id,
            shared_with_person_id=payload.shared_with_person_id,
            can_view=payload.can_view,
            can_edit=payload.can_edit,
            can_add=payload.can_add,
            can_delete=payload.can_delete
        )
        db.add(vasif)

    await db.flush()
    await db.refresh(vasif)
    return VasifResponse.model_validate(vasif)


@router.get("/asset/{asset_id}", response_model=List[VasifResponse])
async def list_asset_shares(
    asset_id: uuid.UUID,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """Bir varlığın kimlerle hangi vasıflarla paylaşıldığını listeler."""
    stmt = select(Vasif).where(Vasif.asset_id == asset_id)
    result = await db.execute(stmt)
    shares = result.scalars().all()
    return [VasifResponse.model_validate(s) for s in shares]


@router.delete("/{vasif_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_vasif(
    vasif_id: uuid.UUID,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """Vasıf yetkisini iptal eder (Paylaşımı sonlandırır)."""
    stmt = select(Vasif).where(Vasif.id == vasif_id)
    result = await db.execute(stmt)
    vasif = result.scalar_one_or_none()

    if not vasif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vasıf kaydı bulunamadı.")

    await db.delete(vasif)
