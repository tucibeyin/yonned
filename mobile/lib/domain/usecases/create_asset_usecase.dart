import '../entities/asset.dart';
import '../repositories/i_asset_repository.dart';

/// Yeni Varlık Oluşturma İş Mantığı (UseCase)
class CreateAssetUseCase {
  final IAssetRepository repository;

  const CreateAssetUseCase(this.repository);

  Future<Asset> execute(Asset asset) async {
    return await repository.createAsset(asset);
  }
}
