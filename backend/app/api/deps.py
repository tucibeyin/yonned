import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_token
from app.models.person import Person

security = HTTPBearer(auto_error=False)


async def get_current_person(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Person:
    """JWT Token üzerinden giriş yapmış olan kişiyi (Person) doğrular."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Giriş yapılması gerekiyor (Eksik veya geçersiz token)"
        )

    person_id_str = verify_token(credentials.credentials)
    if not person_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş oturum"
        )

    try:
        person_uuid = uuid.UUID(person_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kimlik formatı"
        )

    stmt = select(Person).where(Person.id == person_uuid, Person.is_active.is_(True))
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı veya hesabı askıya alınmış"
        )

    return person
