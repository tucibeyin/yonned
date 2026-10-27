import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_person
from app.core.database import get_db
from app.models.asset import Asset
from app.models.person import Person
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """
    Yeni Varlık Tanımlama.
    Eğer üst mekan (parent_id) belirtilmişse, çağıran kişinin 'can_add' yetkisi kontrol edilir.
    Eğer müşteri kendi varlığını (kedi, araba) ekliyorsa, owner_person_id otomatik kendi ID'si olur.
    """
    if payload.parent_id:
        has_add_perm = await PermissionService.check_permission(
            db=db,
            asset_id=payload.parent_id,
            person_id=current_person.id,
            verb="add"
        )
        if not has_add_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu üst varlık altına yeni varlık ekleme yetkiniz (can_add) bulunmuyor."
            )

    owner_id = payload.owner_person_id
    if payload.owner_type == "customer" and not owner_id:
        owner_id = current_person.id

    asset = Asset(
        tenant_id=payload.tenant_id,
        parent_id=payload.parent_id,
        owner_person_id=owner_id,
        owner_type=payload.owner_type,
        asset_type=payload.asset_type,
        name=payload.name,
        identifier=payload.identifier,
        qr_code=payload.qr_code,
        current_location_asset_id=payload.current_location_asset_id,
        capacity=payload.capacity,
        metadata_=payload.metadata,
        is_active=payload.is_active
    )
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: uuid.UUID,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """Varlık detayını döner (can_view yetkisi kontrol edilir)."""
    has_view = await PermissionService.check_permission(
        db=db,
        asset_id=asset_id,
        person_id=current_person.id,
        verb="view"
    )
    if not has_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu varlığı görüntüleme yetkiniz (can_view) bulunmuyor."
        )

    stmt = select(Asset).where(Asset.id == asset_id, Asset.is_active.is_(True))
    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Varlık bulunamadı")

    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}/children", response_model=List[AssetResponse])
async def get_asset_children(
    asset_id: uuid.UUID,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """Bir üst mekanın altındaki tüm çocuk varlıkları (Kat ➔ Odalar, Oda ➔ Kafesler) döner."""
    stmt = select(Asset).where(
        Asset.parent_id == asset_id,
        Asset.is_active.is_(True)
    ).order_by(Asset.name)
    result = await db.execute(stmt)
    children = result.scalars().all()
    return [AssetResponse.model_validate(c) for c in children]
