import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class LiveProcessCreate(BaseModel):
    session_id: uuid.UUID
    definition_id: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = None  # Alt süreç (Acil Müdahale)
    name: str = Field(..., min_length=1, max_length=150)
    is_instant: bool = False
    location_asset_id: Optional[uuid.UUID] = None
    assigned_person_id: Optional[uuid.UUID] = None
    is_customer_visible: bool = True
    customer_notes: Optional[str] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LiveProcessUpdate(BaseModel):
    status: Optional[str] = None  # 'queued', 'running', 'paused', 'completed', 'cancelled'
    location_asset_id: Optional[uuid.UUID] = None
    completed_by_id: Optional[uuid.UUID] = None
    ended_at: Optional[datetime] = None
    customer_notes: Optional[str] = None
    notes: Optional[str] = None
    photos: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class LiveProcessResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    definition_id: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = None
    name: str
    is_instant: bool
    status: str
    location_asset_id: Optional[uuid.UUID] = None
    assigned_person_id: Optional[uuid.UUID] = None
    completed_by_id: Optional[uuid.UUID] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    is_customer_visible: bool
    customer_notes: Optional[str] = None
    notes: Optional[str] = None
    photos: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
