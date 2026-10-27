import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_person
from app.core.database import get_db
from app.models.consumable import ProcessConsumable
from app.models.person import Person
from app.models.process import LiveProcess
from app.schemas.process import LiveProcessCreate, LiveProcessResponse, LiveProcessUpdate

router = APIRouter(prefix="/processes", tags=["Live Processes"])


class ConsumableLogRequest(BaseModel):
    consumable_asset_id: Optional[uuid.UUID] = None
    custom_name: Optional[str] = None
    barcode_scanned: Optional[str] = None
    quantity: float = Field(1.0, ge=0.01)
    unit: str = "adet"
    notes: Optional[str] = None


@router.post("", response_model=LiveProcessResponse, status_code=status.HTTP_201_CREATED)
async def start_process(
    payload: LiveProcessCreate,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """
    CANLI SÜREÇ BAŞLATMA.
    Operatör (Person) bir varlık üzerinde ameliyat, bakım, tıraş veya anlık olay başlatır.
    Araya acil müdahale girdiyse 'parent_id' ile ana sürece bağlanır.
    """
    proc = LiveProcess(
        session_id=payload.session_id,
        definition_id=payload.definition_id,
        parent_id=payload.parent_id,
        name=payload.name,
        is_instant=payload.is_instant,
        status="completed" if payload.is_instant else "running",
        location_asset_id=payload.location_asset_id,
        assigned_person_id=payload.assigned_person_id or current_person.id,
        is_customer_visible=payload.is_customer_visible,
        customer_notes=payload.customer_notes,
        notes=payload.notes,
        metadata_=payload.metadata
    )
    if payload.is_instant:
        proc.ended_at = proc.started_at
        proc.duration_seconds = 0
        proc.completed_by_id = current_person.id

    db.add(proc)
    await db.flush()
    await db.refresh(proc)
    return LiveProcessResponse.model_validate(proc)


@router.patch("/{process_id}", response_model=LiveProcessResponse)
async def update_process(
    process_id: uuid.UUID,
    payload: LiveProcessUpdate,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """Süreç durumunu, fotoğraflarını veya notlarını günceller."""
    stmt = select(LiveProcess).where(LiveProcess.id == process_id)
    result = await db.execute(stmt)
    proc = result.scalar_one_or_none()

    if not proc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Süreç bulunamadı.")

    if payload.status:
        proc.status = payload.status
    if payload.location_asset_id:
        proc.location_asset_id = payload.location_asset_id
    if payload.notes is not None:
        proc.notes = payload.notes
    if payload.customer_notes is not None:
        proc.customer_notes = payload.customer_notes
    if payload.photos is not None:
        proc.photos = payload.photos
    if payload.metadata is not None:
        proc.metadata_ = payload.metadata

    await db.flush()
    await db.refresh(proc)
    return LiveProcessResponse.model_validate(proc)


@router.post("/{process_id}/complete", response_model=LiveProcessResponse)
async def complete_process(
    process_id: uuid.UUID,
    notes: Optional[str] = None,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """Süreci başarıyla tamamlar ve harcanan süreyi hesaplar."""
    stmt = select(LiveProcess).where(LiveProcess.id == process_id)
    result = await db.execute(stmt)
    proc = result.scalar_one_or_none()

    if not proc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Süreç bulunamadı.")

    proc.status = "completed"
    proc.ended_at = datetime.now(timezone.utc)
    proc.completed_by_id = current_person.id
    if notes:
        proc.notes = f"{proc.notes or ''}\n{notes}".strip()
    proc.calculate_duration()

    await db.flush()
    await db.refresh(proc)
    return LiveProcessResponse.model_validate(proc)


@router.post("/{process_id}/consumables", status_code=status.HTTP_201_CREATED)
async def log_consumable_used(
    process_id: uuid.UUID,
    payload: ConsumableLogRequest,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """
    SÜRECE SARF / İLAÇ TÜKETİMİ EKLEME (Zero Blockage).
    Eğer ilaç/sarf sistemde kayıtlı değilse bile 'custom_name' ile kabul edilir.
    """
    item = ProcessConsumable(
        process_id=process_id,
        consumable_asset_id=payload.consumable_asset_id,
        custom_name=payload.custom_name,
        barcode_scanned=payload.barcode_scanned,
        quantity=payload.quantity,
        unit=payload.unit,
        administered_by_id=current_person.id,
        notes=payload.notes
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return {
        "id": str(item.id),
        "name": item.display_name,
        "quantity": float(item.quantity),
        "unit": item.unit
    }
