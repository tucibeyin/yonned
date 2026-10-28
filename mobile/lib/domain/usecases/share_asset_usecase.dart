import '../entities/asset_share.dart';
import '../repositories/i_asset_repository.dart';

/// Varlık Paylaşma İş Mantığı (UseCase)
class ShareAssetUseCase {
  final IAssetRepository repository;

  const ShareAssetUseCase(this.repository);

  Future<AssetShare> execute(AssetShare share) async {
    return await repository.shareAsset(share);
  }
}
