import '../entities/workspace.dart';
import '../repositories/i_asset_repository.dart';

/// Kullanıcının Çalışma Alanlarını Getiren İş Mantığı (UseCase)
class GetWorkspacesUseCase {
  final IAssetRepository repository;

  const GetWorkspacesUseCase(this.repository);

  Future<List<Workspace>> execute() async {
    return await repository.getWorkspaces();
  }
}
