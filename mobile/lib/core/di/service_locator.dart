import 'package:http/http.dart' as http;
import '../database/app_database.dart';
import '../../data/datasources/local/asset_local_datasource.dart';
import '../../data/datasources/remote/asset_remote_datasource.dart';
import '../../data/repositories/asset_repository_impl.dart';
import '../../domain/repositories/i_asset_repository.dart';
import '../../domain/usecases/create_asset_usecase.dart';
import '../../domain/usecases/get_assets_by_workspace_usecase.dart';
import '../../domain/usecases/get_workspaces_usecase.dart';
import '../../domain/usecases/share_asset_usecase.dart';
import '../../presentation/viewmodels/asset_viewmodel.dart';
import '../../presentation/viewmodels/workspace_viewmodel.dart';

/// Bağımlılık Enjeksiyonu ve Servis Bulucu (Dependency Injection / Service Locator)
class ServiceLocator {
  ServiceLocator._();

  static late final AppDatabase database;
  static late final http.Client httpClient;

  static late final AssetLocalDataSource localDataSource;
  static late final AssetRemoteDataSource remoteDataSource;

  static late final IAssetRepository assetRepository;

  static late final GetWorkspacesUseCase getWorkspacesUseCase;
  static late final GetAssetsByWorkspaceUseCase getAssetsByWorkspaceUseCase;
  static late final CreateAssetUseCase createAssetUseCase;
  static late final ShareAssetUseCase shareAssetUseCase;

  static void init() {
    // 1. Core / Database / Network
    database = AppDatabase();
    httpClient = http.Client();

    // 2. Data Sources
    localDataSource = AssetLocalDataSource(appDatabase: database);
    remoteDataSource = AssetRemoteDataSource(client: httpClient);

    // 3. Repositories
    assetRepository = AssetRepositoryImpl(
      localDataSource: localDataSource,
      remoteDataSource: remoteDataSource,
    );

    // 4. UseCases
    getWorkspacesUseCase = GetWorkspacesUseCase(assetRepository);
    getAssetsByWorkspaceUseCase = GetAssetsByWorkspaceUseCase(assetRepository);
    createAssetUseCase = CreateAssetUseCase(assetRepository);
    shareAssetUseCase = ShareAssetUseCase(assetRepository);
  }

  /// ViewModel Fabrikaları
  static WorkspaceViewModel createWorkspaceViewModel() {
    return WorkspaceViewModel(getWorkspacesUseCase: getWorkspacesUseCase);
  }

  static AssetViewModel createAssetViewModel() {
    return AssetViewModel(
      getAssetsUseCase: getAssetsByWorkspaceUseCase,
      createAssetUseCase: createAssetUseCase,
      shareAssetUseCase: shareAssetUseCase,
      assetRepository: assetRepository,
    );
  }
}
