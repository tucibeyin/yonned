import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ScanResolveRequest(BaseModel):
    raw_code: str = Field(..., min_length=1, max_length=255, description="QR string or barcode scanned by camera")
    context_branch_asset_id: Optional[uuid.UUID] = None


class ScanResolveResponse(BaseModel):
    match_type: str = Field(
        ...,
        description="'location' (cage, room, lift), 'subject' (pet, car), 'consumable' (medicine, part), 'unknown'"
    )
    asset_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    asset_type: Optional[str] = None
    identifier: Optional[str] = None
    active_session_id: Optional[uuid.UUID] = None
    prompt_create: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)
