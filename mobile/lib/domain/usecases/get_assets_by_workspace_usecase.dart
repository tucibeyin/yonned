import '../entities/asset.dart';
import '../entities/workspace.dart';
import '../repositories/i_asset_repository.dart';

/// Seçili Çalışma Alanına Göre Varlıkları Getiren İş Mantığı (UseCase)
class GetAssetsByWorkspaceUseCase {
  final IAssetRepository repository;

  const GetAssetsByWorkspaceUseCase(this.repository);

  Future<List<Asset>> execute(Workspace workspace) async {
    return await repository.getAssetsByWorkspace(workspace);
  }
}
