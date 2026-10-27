from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.person import Person
from app.schemas.person import PersonResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


class PhoneLoginRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=50)
    name: str = Field("Yeni Kullanıcı", min_length=2, max_length=150)


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    person: PersonResponse


@router.post("/login/phone", response_model=AuthTokenResponse)
async def login_by_phone(
    payload: PhoneLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Telefon Numarası ile Giriş / Hızlı Kayıt.
    Numara varsa oturum açar, yoksa anında yeni Person kaydeder (Sıfır Blokaj).
    """
    stmt = select(Person).where(Person.phone == payload.phone)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if not person:
        person = Person(
            name=payload.name,
            phone=payload.phone,
            is_active=True
        )
        db.add(person)
        await db.flush()
        await db.refresh(person)

    token = create_access_token(subject=str(person.id))
    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        person=PersonResponse.model_validate(person)
    )
