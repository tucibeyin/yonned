import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.models.person import Person
from app.models.vasif import Vasif
from app.services.permission_service import PermissionService


@pytest.mark.asyncio
async def test_owner_has_all_four_crud_verbs(db_session: AsyncSession):
    """Varlık sahibinin 4 CRUD fiilinin tümüne (Create, Read, Update, Delete) sahip olduğunu doğrular."""
    tenant_id = uuid.uuid4()
    owner = Person(name="Dr. Ali", phone="+905551112233")
    db_session.add(owner)
    await db_session.flush()

    clinic = Asset(
        tenant_id=tenant_id,
        owner_person_id=owner.id,
        owner_type="business",
        asset_type="organization",
        name="Pati Veteriner Kliniği"
    )
    db_session.add(clinic)
    await db_session.flush()

    perms = await PermissionService.resolve_permissions(db_session, clinic.id, owner.id)
    assert perms["can_create"] is True
    assert perms["can_read"] is True
    assert perms["can_update"] is True
    assert perms["can_delete"] is True


@pytest.mark.asyncio
async def test_vasif_crud_delegation(db_session: AsyncSession):
    """
    Vasıf ile devredilen 4 CRUD fiilinin bağımsız çalıştığını doğrular.
    Örnek: Stajyere yalnızca Read ve Create yetkisi verilir, Update ve Delete kapalıdır.
    """
    tenant_id = uuid.uuid4()
    owner = Person(name="Patron", phone="+905550000001")
    intern = Person(name="Stajyer Özge", phone="+905550000002")
    db_session.add_all([owner, intern])
    await db_session.flush()

    clinic = Asset(
        tenant_id=tenant_id,
        owner_person_id=owner.id,
        asset_type="organization",
        name="Pati Kliniği"
    )
    db_session.add(clinic)
    await db_session.flush()

    # Stajyere Vasıf Ata: can_read=True, can_create=True, can_update=False, can_delete=False
    vasif = Vasif(
        asset_id=clinic.id,
        shared_with_person_id=intern.id,
        can_create=True,
        can_read=True,
        can_update=False,
        can_delete=False
    )
    db_session.add(vasif)
    await db_session.flush()

    perms = await PermissionService.resolve_permissions(db_session, clinic.id, intern.id)
    assert perms["can_read"] is True
    assert perms["can_create"] is True
    assert perms["can_update"] is False
    assert perms["can_delete"] is False


@pytest.mark.asyncio
async def test_crud_permission_cascade_to_child_assets(db_session: AsyncSession):
    """
    Üst mekanda (Şube) verilen CRUD vasfının alt mekana (Kafes) miras kaldığını (Cascade) doğrular.
    """
    tenant_id = uuid.uuid4()
    owner = Person(name="Patron", phone="+905550000010")
    nurse = Person(name="Hemşire Can", phone="+905550000020")
    db_session.add_all([owner, nurse])
    await db_session.flush()

    branch = Asset(
        tenant_id=tenant_id,
        owner_person_id=owner.id,
        asset_type="branch",
        name="Kadıköy Şubesi"
    )
    db_session.add(branch)
    await db_session.flush()

    cage = Asset(
        tenant_id=tenant_id,
        parent_id=branch.id,
        owner_person_id=owner.id,
        asset_type="cage",
        name="Kafes #1"
    )
    db_session.add(cage)
    await db_session.flush()

    # Şubeye Vasıf Ver: can_create=True, can_read=True
    vasif = Vasif(
        asset_id=branch.id,
        shared_with_person_id=nurse.id,
        can_create=True,
        can_read=True
    )
    db_session.add(vasif)
    await db_session.flush()

    # Kafes üzerinde doğrudan kayıt olmamasına rağmen şubeden miras almalıdır:
    cage_perms = await PermissionService.resolve_permissions(db_session, cage.id, nurse.id)
    assert cage_perms["can_read"] is True
    assert cage_perms["can_create"] is True
    assert cage_perms["can_update"] is False
    assert cage_perms["can_delete"] is False
