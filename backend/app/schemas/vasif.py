import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class VasifBase(BaseModel):
    can_create: bool = Field(False, description="Oluştur / Ekle (Create)")
    can_read: bool = Field(True, description="Görüntüle / Oku (Read)")
    can_update: bool = Field(False, description="Güncelle / Değiştir (Update)")
    can_delete: bool = Field(False, description="Sil / Kaldır (Delete)")


class VasifCreate(VasifBase):
    asset_id: uuid.UUID
    shared_with_person_id: uuid.UUID


class VasifUpdate(VasifBase):
    pass


class VasifResponse(VasifBase):
    id: uuid.UUID
    asset_id: uuid.UUID
    shared_with_person_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
