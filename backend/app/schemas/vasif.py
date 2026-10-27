import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class VasifBase(BaseModel):
    can_view: bool = Field(True, description="Görüntüle")
    can_edit: bool = Field(False, description="Değiştir / Güncelle")
    can_add: bool = Field(False, description="Ekle (Yeni süreç, acil müdahale, sarf)")
    can_delete: bool = Field(False, description="Sil (Kayıt, süreç veya varlık kaldırma)")


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
