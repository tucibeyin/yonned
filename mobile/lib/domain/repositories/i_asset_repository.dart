import '../entities/asset.dart';
import '../entities/asset_share.dart';
import '../entities/workspace.dart';

/// Varlık ve Çalışma Alanı Veri Sözleşmesi (Domain Repository Interface)
abstract class IAssetRepository {
  /// Kullanıcının erişebildiği tüm çalışma alanlarını (şubeler + kişisel cüzdan) getirir
  Future<List<Workspace>> getWorkspaces();

  /// Seçili çalışma alanına ait varlıkları (şube istasyonları veya kişisel evcil hayvan/araçlar) getirir
  Future<List<Asset>> getAssetsByWorkspace(Workspace workspace);

  /// Yeni bir varlık oluşturur (kedi, köpek, araç veya istasyon)
  Future<Asset> createAsset(Asset asset);

  /// Bir varlığı başka bir kullanıcıyla 4 atomik CRUD izniyle paylaşır
  Future<AssetShare> shareAsset(AssetShare share);

  /// Varlık durumunu günceller (örn: kafes doluluğu, ameliyat notu)
  Future<Asset> updateAsset(Asset asset);

  /// Varlığı siler / arşivler
  Future<void> deleteAsset(String assetId);
}
