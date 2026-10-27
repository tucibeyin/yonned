import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.asset import AssetResponse


class AssetSessionBase(BaseModel):
    status: str = Field("checked_in", description="checked_in, in_service, ready_for_pickup, completed, cancelled")


class AssetSessionCreate(BaseModel):
    tenant_id: uuid.UUID
    branch_asset_id: uuid.UUID
    subject_asset_id: uuid.UUID
    current_location_asset_id: Optional[uuid.UUID] = None


class AssetSessionResponse(AssetSessionBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    branch_asset_id: uuid.UUID
    subject_asset_id: uuid.UUID
    current_location_asset_id: Optional[uuid.UUID] = None
    tracking_token: str
    check_in_at: datetime
    check_out_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerTrackerStep(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    is_instant: bool
    started_at: datetime
    ended_at: Optional[datetime] = None
    photos: List[str] = Field(default_factory=list)
    customer_notes: Optional[str] = None


class CustomerLiveTrackerResponse(BaseModel):
    tracking_token: str
    subject_name: str
    subject_type: str
    identifier: Optional[str] = None
    branch_name: str
    session_status: str
    current_location_name: Optional[str] = None
    check_in_at: datetime
    steps: List[CustomerTrackerStep] = Field(default_factory=list)
