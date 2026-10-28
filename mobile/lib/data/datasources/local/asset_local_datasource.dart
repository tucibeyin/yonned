import 'package:sqflite/sqflite.dart';
import '../../../core/database/app_database.dart';
import '../../../core/database/database_tables.dart';
import '../../models/asset_dto.dart';
import '../../models/asset_share_dto.dart';

/// Yerel SQLite Veri Kaynağı (Clean DAO / Local DataSource)
class AssetLocalDataSource {
  final AppDatabase appDatabase;

  const AssetLocalDataSource({required this.appDatabase});

  Future<Database> get _db => appDatabase.database;

  /// Kök organizasyonları (işletmeleri) getirir
  Future<List<AssetDto>> getOrganizations() async {
    final db = await _db;
    final results = await db.query(
      DatabaseTables.tableAssets,
      where: 'asset_type = ? AND is_active = 1',
      whereArgs: ['organization'],
      orderBy: 'name ASC',
    );
    return results.map(AssetDto.fromDb).toList();
  }

  /// Bir organizasyona bağlı şubeleri (bayileri) getirir
  Future<List<AssetDto>> getBranchesByOrgId(String orgId) async {
    final db = await _db;
    final results = await db.query(
      DatabaseTables.tableAssets,
      where: 'parent_id = ? AND asset_type = ? AND is_active = 1',
      whereArgs: [orgId, 'branch'],
      orderBy: 'name ASC',
    );
    return results.map(AssetDto.fromDb).toList();
  }

  /// Bir şubeye bağlı istasyonları (kafesler, liftler, peronlar) getirir
  Future<List<AssetDto>> getStationsByBranchId(String branchId) async {
    final db = await _db;
    final results = await db.query(
      DatabaseTables.tableAssets,
      where: 'parent_id = ? AND is_active = 1',
      whereArgs: [branchId],
      orderBy: 'name ASC',
    );
    return results.map(AssetDto.fromDb).toList();
  }

  /// Bireysel kullanıcıya ait kişisel varlıkları (kedi, köpek, araç) getirir
  Future<List<AssetDto>> getCustomerAssets() async {
    final db = await _db;
    final results = await db.query(
      DatabaseTables.tableAssets,
      where: 'owner_type = ? AND is_active = 1',
      whereArgs: ['customer'],
      orderBy: 'created_at DESC',
    );
    return results.map(AssetDto.fromDb).toList();
  }

  /// Yeni varlık ekler
  Future<void> insertAsset(AssetDto asset) async {
    final db = await _db;
    await db.insert(
      DatabaseTables.tableAssets,
      asset.toDbMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// Varlık günceller
  Future<void> updateAsset(AssetDto asset) async {
    final db = await _db;
    await db.update(
      DatabaseTables.tableAssets,
      asset.toDbMap(),
      where: 'id = ?',
      whereArgs: [asset.id],
    );
  }

  /// Varlık siler
  Future<void> deleteAsset(String assetId) async {
    final db = await _db;
    await db.delete(
      DatabaseTables.tableAssets,
      where: 'id = ?',
      whereArgs: [assetId],
    );
  }

  /// Paylaşım (Vasıf) ekler
  Future<void> insertShare(AssetShareDto share) async {
    final db = await _db;
    await db.insert(
      DatabaseTables.tableAssetShares,
      share.toDbMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  /// Varlığa ait paylaşımları getirir
  Future<List<AssetShareDto>> getSharesByAssetId(String assetId) async {
    final db = await _db;
    final results = await db.query(
      DatabaseTables.tableAssetShares,
      where: 'asset_id = ?',
      whereArgs: [assetId],
    );
    return results.map(AssetShareDto.fromDb).toList();
  }

  /// İlk açılışta zengin ve gerçekçi demonstrasyon verilerini tohumlar (Seed Data)
  Future<void> seedInitialDataIfNeeded() async {
    final db = await _db;
    final count = Sqflite.firstIntValue(
      await db.rawQuery('SELECT COUNT(*) FROM ${DatabaseTables.tableAssets}'),
    );

    if (count != null && count > 0) return; // Zaten veri var

    final now = DateTime.now().toIso8601String();

    // 1. İŞLETME: Pati Veteriner Grubu (4 Şubeli)
    final orgVet = AssetDto(
      id: 'org_vet_1',
      tenantId: 'tenant_vet_1',
      ownerType: 'business',
      assetType: 'organization',
      name: 'Pati Veteriner Kliniği',
      capacity: 100,
      metadata: {'industry': 'veterinary'},
      isActive: true,
      createdAt: now,
      updatedAt: now,
    );
    await insertAsset(orgVet);

    // 4 Şube
    final branchesVet = [
      AssetDto(
        id: 'branch_vet_besiktas',
        tenantId: 'tenant_vet_1',
        parentId: 'org_vet_1',
        ownerType: 'business',
        assetType: 'branch',
        name: 'Beşiktaş Merkez Şubesi',
        capacity: 30,
        metadata: {'address': 'Beşiktaş Çarşı No:12'},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'branch_vet_kadikoy',
        tenantId: 'tenant_vet_1',
        parentId: 'org_vet_1',
        ownerType: 'business',
        assetType: 'branch',
        name: 'Kadıköy Şubesi',
        capacity: 20,
        metadata: {'address': 'Moda Cad. No:45'},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'branch_vet_nisantasi',
        tenantId: 'tenant_vet_1',
        parentId: 'org_vet_1',
        ownerType: 'business',
        assetType: 'branch',
        name: 'Nişantaşı Şubesi',
        capacity: 15,
        metadata: {'address': 'Valikonağı No:88'},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'branch_vet_bursa',
        tenantId: 'tenant_vet_1',
        parentId: 'org_vet_1',
        ownerType: 'business',
        assetType: 'branch',
        name: 'Bursa Nilüfer Şubesi',
        capacity: 25,
        metadata: {'address': 'FSM Bulvarı No:10'},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
    ];
    for (var b in branchesVet) {
      await insertAsset(b);
    }

    // Beşiktaş Şubesindeki İstasyonlar (Kafesler & Ameliyathane)
    final besiktasStations = [
      AssetDto(
        id: 'cage_101',
        tenantId: 'tenant_vet_1',
        parentId: 'branch_vet_besiktas',
        ownerType: 'business',
        assetType: 'cage',
        name: 'Kafes #1 (Yoğun Bakım)',
        capacity: 1,
        metadata: {
          'is_occupied': true,
          'active_subject_name': 'Pamuk (Kedi)',
          'status_note': 'Serum Takılı - Dinleniyor',
        },
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'cage_102',
        tenantId: 'tenant_vet_1',
        parentId: 'branch_vet_besiktas',
        ownerType: 'business',
        assetType: 'cage',
        name: 'Kafes #2 (Standart)',
        capacity: 1,
        metadata: {'is_occupied': false},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'cage_103',
        tenantId: 'tenant_vet_1',
        parentId: 'branch_vet_besiktas',
        ownerType: 'business',
        assetType: 'cage',
        name: 'Kafes #3 (Büyük Boy)',
        capacity: 1,
        metadata: {'is_occupied': false},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'station_op_1',
        tenantId: 'tenant_vet_1',
        parentId: 'branch_vet_besiktas',
        ownerType: 'business',
        assetType: 'station',
        name: 'Ameliyathane Masası #1',
        capacity: 1,
        metadata: {
          'is_occupied': true,
          'active_subject_name': 'Tarçın (Köpek)',
          'status_note': 'Kısırlaştırma Operasyonu Tamamlandı',
        },
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
    ];
    for (var s in besiktasStations) {
      await insertAsset(s);
    }

    // 2. İŞLETME: Demir Detailing & Yıkama (2 Şubeli)
    final orgDetailing = AssetDto(
      id: 'org_auto_1',
      tenantId: 'tenant_auto_1',
      ownerType: 'business',
      assetType: 'organization',
      name: 'Demir Oto Detailing',
      capacity: 50,
      metadata: {'industry': 'auto_detailing'},
      isActive: true,
      createdAt: now,
      updatedAt: now,
    );
    await insertAsset(orgDetailing);

    final branchesAuto = [
      AssetDto(
        id: 'branch_auto_kadikoy',
        tenantId: 'tenant_auto_1',
        parentId: 'org_auto_1',
        ownerType: 'business',
        assetType: 'branch',
        name: 'Kadıköy Yıkama Merkezi',
        capacity: 10,
        metadata: {'address': 'Fikirtepe Sanayi'},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'branch_auto_maslak',
        tenantId: 'tenant_auto_1',
        parentId: 'org_auto_1',
        ownerType: 'business',
        assetType: 'branch',
        name: 'Maslak Restorasyon Şubesi',
        capacity: 15,
        metadata: {'address': 'Atatürk Oto Sanayi 2. Kısım'},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
    ];
    for (var b in branchesAuto) {
      await insertAsset(b);
    }

    // Kadıköy Oto İstasyonları (Peronlar)
    final autoStations = [
      AssetDto(
        id: 'bay_1',
        tenantId: 'tenant_auto_1',
        parentId: 'branch_auto_kadikoy',
        ownerType: 'business',
        assetType: 'bay',
        name: 'Yıkama Peronu #1',
        capacity: 1,
        metadata: {
          'is_occupied': true,
          'active_subject_name': '34 YZ 999 (Mercedes C200)',
          'status_note': 'Köpüklü Yıkama Sürüyor',
        },
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'bay_2',
        tenantId: 'tenant_auto_1',
        parentId: 'branch_auto_kadikoy',
        ownerType: 'business',
        assetType: 'bay',
        name: 'Yıkama Peronu #2',
        capacity: 1,
        metadata: {'is_occupied': false},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'lift_1',
        tenantId: 'tenant_auto_1',
        parentId: 'branch_auto_kadikoy',
        ownerType: 'business',
        assetType: 'lift',
        name: 'Alt Yıkama Lifti #1',
        capacity: 1,
        metadata: {'is_occupied': false},
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
    ];
    for (var s in autoStations) {
      await insertAsset(s);
    }

    // 3. KİŞİSEL CÜZDAN: Bireyin Kendi Varlıkları
    final personalAssets = [
      AssetDto(
        id: 'pet_tarcin',
        tenantId: 'tenant_personal_ali',
        ownerType: 'customer',
        assetType: 'pet',
        name: 'Tarçın',
        identifier: 'Çip: 90021300012',
        qrCode: 'YONNED-PET-TARCIN-01',
        capacity: 1,
        metadata: {
          'species': 'Köpek',
          'breed': 'Golden Retriever',
          'age': '3 Yaş',
          'status': 'Pati Kliniğinde Ameliyat Oldu',
        },
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'pet_pamuk',
        tenantId: 'tenant_personal_ali',
        ownerType: 'customer',
        assetType: 'pet',
        name: 'Pamuk',
        identifier: 'Çip: 90021300099',
        qrCode: 'YONNED-PET-PAMUK-02',
        capacity: 1,
        metadata: {
          'species': 'Kedi',
          'breed': 'Van Kedisi',
          'age': '1.5 Yaş',
          'status': 'Evde Mışıl Mışıl',
        },
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
      AssetDto(
        id: 'vehicle_bmw',
        tenantId: 'tenant_personal_ali',
        ownerType: 'customer',
        assetType: 'vehicle',
        name: 'BMW 3.20i',
        identifier: 'Plaka: 34 ABC 123',
        qrCode: 'YONNED-CAR-BMW-03',
        capacity: 5,
        metadata: {
          'model_year': '2023',
          'color': 'Mineral Gri',
          'status': 'Kapıda Park Halinde',
        },
        isActive: true,
        createdAt: now,
        updatedAt: now,
      ),
    ];
    for (var p in personalAssets) {
      await insertAsset(p);
    }

    // Tarçın için örnek eş paylaşımı (Vasıf - Full Access)
    final shareTarcin = AssetShareDto(
      id: 'share_1',
      assetId: 'pet_tarcin',
      sharedWithPersonId: 'person_ayse_99',
      canCreate: true,
      canRead: true,
      canUpdate: true,
      canDelete: true,
      createdAt: now,
    );
    await insertShare(shareTarcin);
  }
}
