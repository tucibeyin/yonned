import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.models.consumable import ProcessConsumable
from app.models.person import Person
from app.models.process import LiveProcess
from app.models.session import AssetSession


@pytest.mark.asyncio
async def test_emergency_interruption_and_zero_blockage_medicine(db_session: AsyncSession):
    """
    Saha Simülasyonu: Sıfır Blokaj, Araya Giren Acil Müdahale ve Tanımsız İlaç Tüketimi.
    1. Müşteri (Ali) köpeğini (Tarçın) kliniğe bırakır.
    2. Hizmet oturumu açılır (Check-in). Mülkiyet Ali'de kalır!
    3. Hekim tıraş sürecini başlatır.
    4. Beklenmedik kesik oluşur: Tıraş duraklatılır, 'Acil Dikiş' alt süreci açılır.
    5. Ecza dolabından sisteme tanımlanmamış sprey 'custom_name' ile kaydedilir (Sıfır Blokaj!).
    6. Dikiş tamamlanır, tıraş devam eder.
    """
    tenant_id = uuid.uuid4()

    # Aktörler
    customer = Person(name="Ali Müşteri", phone="+905557778899")
    vet = Person(name="Dr. Mehmet", phone="+905553332211")
    db_session.add_all([customer, vet])
    await db_session.flush()

    # Varlıklar (Klinik ve Köpek)
    clinic = Asset(
        tenant_id=tenant_id,
        owner_person_id=vet.id,
        asset_type="organization",
        name="Kadıköy Veteriner"
    )
    dog = Asset(
        tenant_id=tenant_id,
        owner_person_id=customer.id,  # Kalıcı sahip daima müşteri!
        owner_type="customer",
        asset_type="pet",
        name="Tarçın",
        identifier="CHIP-98472910"
    )
    db_session.add_all([clinic, dog])
    await db_session.flush()

    # 1. Oturum Açılışı (Check-in)
    session = AssetSession(
        tenant_id=tenant_id,
        branch_asset_id=clinic.id,
        subject_asset_id=dog.id,
        status="checked_in"
    )
    db_session.add(session)
    await db_session.flush()

    # Doğrulama: Köpeğin mülkiyeti hala müşteridedir!
    assert dog.owner_person_id == customer.id

    # 2. Ana Süreç Başlar (Tıraş)
    grooming = LiveProcess(
        session_id=session.id,
        name="Genel Tıraş",
        status="running",
        assigned_person_id=vet.id
    )
    db_session.add(grooming)
    await db_session.flush()

    # 3. Kaza Oluşur: Tıraş duraklar, Acil Dikiş süreci (alt süreç) başlar
    grooming.status = "paused"
    emergency_stitch = LiveProcess(
        session_id=session.id,
        parent_id=grooming.id,  # Tıraşın altına bağlı acil müdahale
        name="Acil Kesi Dikişi",
        status="running",
        assigned_person_id=vet.id
    )
    db_session.add(emergency_stitch)
    await db_session.flush()

    # 4. Tanımsız İlaç Tüketimi (Sıfır Blokaj JIT girişi)
    spray = ProcessConsumable(
        process_id=emergency_stitch.id,
        custom_name="Terramycin Yara Spreyi",
        barcode_scanned="8699508009999",
        quantity=1.0,
        unit="adet",
        administered_by_id=vet.id,
        notes="Kesi bölgesine lokal uygulandı."
    )
    db_session.add(spray)
    await db_session.flush()

    # Doğrulama: İlaç kataloğu olmasa bile sarf kaydedilmiştir
    assert spray.display_name == "Terramycin Yara Spreyi"

    # 5. Acil Dikiş Tamamlanır
    emergency_stitch.status = "completed"
    grooming.status = "running"
    await db_session.flush()

    assert emergency_stitch.status == "completed"
    assert grooming.status == "running"
    assert dog.owner_person_id == customer.id
