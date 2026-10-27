import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_person
from app.core.database import get_db
from app.models.asset import Asset
from app.models.person import Person
from app.models.process import LiveProcess
from app.models.session import AssetSession
from app.schemas.session import (
    AssetSessionCreate,
    AssetSessionResponse,
    CustomerLiveTrackerResponse,
    CustomerTrackerStep,
)

router = APIRouter(prefix="/sessions", tags=["Asset Sessions & Live Tracker"])


@router.post("/check-in", response_model=AssetSessionResponse, status_code=status.HTTP_201_CREATED)
async def check_in_asset(
    payload: AssetSessionCreate,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """
    HİZMET OTURUMU BAŞLATMA (Check-in / Geçici Zilyetlik).
    Kalıcı mülkiyet (owner_person_id) asla değişmez!
    Varlık tesise kabul edilir, müşteriye tracking_token üretilir ve konum güncellenir.
    """
    session = AssetSession(
        tenant_id=payload.tenant_id,
        branch_asset_id=payload.branch_asset_id,
        subject_asset_id=payload.subject_asset_id,
        current_location_asset_id=payload.current_location_asset_id,
        status="checked_in"
    )
    db.add(session)

    # Eğer varlığın konumu belirtilmişse, varlığın anlık konumunu da güncelle:
    if payload.current_location_asset_id:
        asset_stmt = select(Asset).where(Asset.id == payload.subject_asset_id)
        asset_res = await db.execute(asset_stmt)
        asset = asset_res.scalar_one_or_none()
        if asset:
            asset.current_location_asset_id = payload.current_location_asset_id

    await db.flush()
    await db.refresh(session)
    return AssetSessionResponse.model_validate(session)


@router.post("/{session_id}/check-out", response_model=AssetSessionResponse)
async def check_out_asset(
    session_id: uuid.UUID,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """Hizmet oturumunu tamamlar ve varlığı müşteriye iade eder."""
    stmt = select(AssetSession).where(AssetSession.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oturum bulunamadı.")

    session.status = "completed"
    session.check_out_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(session)
    return AssetSessionResponse.model_validate(session)


@router.get("/tracker/{token}", response_model=CustomerLiveTrackerResponse)
async def get_public_customer_tracker(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    MÜŞTERİ CANLI TAKİP SİHİRLİ LİNKİ (Public Magic Link).
    Müşterinin uygulama indirmesine veya şifre girmesine gerek yoktur.
    SMS/WhatsApp'tan gelen token ile canlı durumu, adımları ve fotoğrafları izler.
    """
    stmt = select(AssetSession).options(
        selectinload(AssetSession.subject_asset),
        selectinload(AssetSession.branch_asset),
        selectinload(AssetSession.current_location),
        selectinload(AssetSession.processes)
    ).where(AssetSession.tracking_token == token)

    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Takip bağlantısı geçersiz veya bulunamadı.")

    steps = []
    for proc in session.processes:
        if proc.is_customer_visible:
            steps.append(CustomerTrackerStep(
                id=proc.id,
                name=proc.name,
                status=proc.status,
                is_instant=proc.is_instant,
                started_at=proc.started_at,
                ended_at=proc.ended_at,
                photos=proc.photos,
                customer_notes=proc.customer_notes
            ))

    return CustomerLiveTrackerResponse(
        tracking_token=session.tracking_token,
        subject_name=session.subject_asset.name,
        subject_type=session.subject_asset.asset_type,
        identifier=session.subject_asset.identifier,
        branch_name=session.branch_asset.name,
        session_status=session.status,
        current_location_name=session.current_location.name if session.current_location else None,
        check_in_at=session.check_in_at,
        steps=steps
    )
