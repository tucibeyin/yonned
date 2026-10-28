import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'database_tables.dart';

/// Yonned Yerel Veritabanı Yöneticisi (Clean Offline-First SQLite Database)
class AppDatabase {
  static const String _dbName = 'yonned_local.db';
  static const int _dbVersion = 1;

  static AppDatabase? _instance;
  static Database? _database;

  AppDatabase._internal();

  factory AppDatabase() {
    _instance ??= AppDatabase._internal();
    return _instance!;
  }

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, _dbName);

    return await openDatabase(
      path,
      version: _dbVersion,
      onCreate: _onCreate,
      onConfigure: _onConfigure,
    );
  }

  Future<void> _onConfigure(Database db) async {
    // Yabancı anahtar (Foreign Key) kısıtlamalarını etkinleştir
    await db.execute('PRAGMA foreign_keys = ON');
  }

  Future<void> _onCreate(Database db, int version) async {
    final batch = db.batch();

    // Tabloları oluştur
    batch.execute(DatabaseTables.createAssetsTable);
    batch.execute(DatabaseTables.createAssetSharesTable);
    batch.execute(DatabaseTables.createPersonsTable);

    await batch.commit();

    // İndeksleri ayrı ayrı çalıştır
    await db.execute('CREATE INDEX IF NOT EXISTS idx_assets_parent ON assets(parent_id)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type)');
    await db.execute('CREATE INDEX IF NOT EXISTS idx_assets_owner ON assets(owner_person_id)');
  }

  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }
}
