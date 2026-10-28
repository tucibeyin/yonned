/// Yerel Veritabanı Tablo Şemaları ve İndeksleri (Clean SQLite Schema)
class DatabaseTables {
  DatabaseTables._();

  static const String tableAssets = 'assets';
  static const String tableAssetShares = 'asset_shares';
  static const String tablePersons = 'persons';

  // Assets Tablosu DDL (Özyinelemeli Ağaç Desteği)
  static const String createAssetsTable = '''
    CREATE TABLE IF NOT EXISTS $tableAssets (
      id TEXT PRIMARY KEY NOT NULL,
      tenant_id TEXT NOT NULL,
      parent_id TEXT,
      owner_person_id TEXT,
      owner_type TEXT NOT NULL DEFAULT 'business',
      asset_type TEXT NOT NULL,
      name TEXT NOT NULL,
      identifier TEXT,
      qr_code TEXT UNIQUE,
      capacity INTEGER NOT NULL DEFAULT 1,
      metadata TEXT NOT NULL DEFAULT '{}',
      is_active INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      FOREIGN KEY (parent_id) REFERENCES $tableAssets(id) ON DELETE CASCADE
    );
  ''';

  // İndeksler (Hızlı sorgulama ve hiyerarşi filtreleme)
  static const String createAssetsIndexes = '''
    CREATE INDEX IF NOT EXISTS idx_assets_parent ON $tableAssets(parent_id);
    CREATE INDEX IF NOT EXISTS idx_assets_type ON $tableAssets(asset_type);
    CREATE INDEX IF NOT EXISTS idx_assets_owner ON $tableAssets(owner_person_id);
  ''';

  // Asset Shares (Vasif) Tablosu DDL (4 Atomik CRUD İzni)
  static const String createAssetSharesTable = '''
    CREATE TABLE IF NOT EXISTS $tableAssetShares (
      id TEXT PRIMARY KEY NOT NULL,
      asset_id TEXT NOT NULL,
      shared_with_person_id TEXT NOT NULL,
      can_create INTEGER NOT NULL DEFAULT 0,
      can_read INTEGER NOT NULL DEFAULT 1,
      can_update INTEGER NOT NULL DEFAULT 0,
      can_delete INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL,
      FOREIGN KEY (asset_id) REFERENCES $tableAssets(id) ON DELETE CASCADE,
      UNIQUE(asset_id, shared_with_person_id)
    );
  ''';

  // Persons Tablosu DDL (Aktif Kullanıcı Bilgisi)
  static const String createPersonsTable = '''
    CREATE TABLE IF NOT EXISTS $tablePersons (
      id TEXT PRIMARY KEY NOT NULL,
      phone TEXT UNIQUE NOT NULL,
      full_name TEXT NOT NULL,
      email TEXT,
      created_at TEXT NOT NULL
    );
  ''';
}
