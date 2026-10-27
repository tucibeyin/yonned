import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    asset_type: str = Field(
        ...,
        description="organization, branch, floor, room, station, cage, bay, device, consumable, pet, vehicle, custom"
    )
    owner_type: str = Field("business", description="'business' or 'customer'")
    identifier: Optional[str] = None
    qr_code: Optional[str] = None
    capacity: int = Field(1, ge=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class AssetCreate(AssetBase):
    tenant_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    owner_person_id: Optional[uuid.UUID] = None
    current_location_asset_id: Optional[uuid.UUID] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    current_location_asset_id: Optional[uuid.UUID] = None
    identifier: Optional[str] = None
    qr_code: Optional[str] = None
    capacity: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AssetResponse(AssetBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    owner_person_id: Optional[uuid.UUID] = None
    current_location_asset_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AssetBreadcrumb(BaseModel):
    id: uuid.UUID
    name: str
    asset_type: str
