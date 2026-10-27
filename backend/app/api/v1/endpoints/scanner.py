from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_person
from app.core.database import get_db
from app.models.person import Person
from app.schemas.scanner import ScanResolveRequest, ScanResolveResponse
from app.services.scanner_service import ScannerService

router = APIRouter(prefix="/scanner", tags=["Universal Camera Scanner"])


@router.post("/resolve", response_model=ScanResolveResponse)
async def resolve_scanned_code(
    payload: ScanResolveRequest,
    current_person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db)
):
    """
    EVRENSEL VİZÖR ÇÖZÜMLEME UÇ NOKTASI.
    Kameradan okutulan ham metin / QR string'ini çözümler.
    Kafes QR'ı ise konum, hasta/araç ise özne, ilaç ise sarf döner.
    """
    return await ScannerService.resolve(
        db=db,
        raw_code=payload.raw_code,
        context_branch_id=payload.context_branch_asset_id
    )
