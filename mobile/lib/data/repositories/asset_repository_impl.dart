import '../../domain/entities/asset.dart';
import '../../domain/entities/asset_share.dart';
import '../../domain/entities/workspace.dart';
import '../../domain/repositories/i_asset_repository.dart';
import '../datasources/local/asset_local_datasource.dart';
import '../datasources/remote/asset_remote_datasource.dart';
import '../models/asset_dto.dart';
import '../models/asset_share_dto.dart';

/// Varlık Repository Gerçekleşimi (Offline-First Clean Repository)
class AssetRepositoryImpl implements IAssetRepository {
  final AssetLocalDataSource localDataSource;
  final AssetRemoteDataSource remoteDataSource;

  const AssetRepositoryImpl({
    required this.localDataSource,
    required this.remoteDataSource,
  });

  @override
  Future<List<Workspace>> getWorkspaces() async {
    // Veritabanının ilk açılışta tohumlandığından emin ol
    await localDataSource.seedInitialDataIfNeeded();

    final List<Workspace> workspaces = [];

    // 1. Her zaman en tepede veya ilk sırada Kişisel Varlık Cüzdanı yer alır
    workspaces.add(Workspace.personal(personId: 'me'));

    // 2. Kök işletmeleri getir (Örn: Pati Veteriner, Demir Oto Detailing)
    final orgs = await localDataSource.getOrganizations();

    for (var org in orgs) {
      // 3. Her işletmenin şubelerini getir
      final branches = await localDataSource.getBranchesByOrgId(org.id);
      for (var branch in branches) {
        String icon = '🏢';
        if (org.metadata['industry'] == 'veterinary') {
          icon = '🏥';
        } else if (org.metadata['industry'] == 'auto_detailing') {
          icon = '🚗';
        }

        workspaces.add(
          Workspace.branch(
            branchId: branch.id,
            branchName: branch.name,
            organizationId: org.id,
            organizationName: org.name,
            icon: icon,
          ),
        );
      }
    }

    return workspaces;
  }

  @override
  Future<List<Asset>> getAssetsByWorkspace(Workspace workspace) async {
    List<AssetDto> dtos = [];

    if (workspace.isPersonal) {
      // Kişisel varlıklar (kedi, köpek, araba)
      dtos = await localDataSource.getCustomerAssets();
    } else {
      // Seçili şubeye ait fiziksel istasyonlar (kafesler, peronlar, liftler)
      dtos = await localDataSource.getStationsByBranchId(workspace.branchId!);
    }

    final List<Asset> assets = [];
    for (var dto in dtos) {
      final sharesDto = await localDataSource.getSharesByAssetId(dto.id);
      final shares = sharesDto.map((s) => s.toDomain()).toList();
      assets.add(dto.toDomain().copyWith(shares: shares));
    }

    return assets;
  }

  @override
  Future<Asset> createAsset(Asset asset) async {
    final dto = AssetDto.fromDomain(asset);
    await localDataSource.insertAsset(dto);
    return asset;
  }

  @override
  Future<AssetShare> shareAsset(AssetShare share) async {
    final dto = AssetShareDto.fromDomain(share);
    await localDataSource.insertShare(dto);
    return share;
  }

  @override
  Future<Asset> updateAsset(Asset asset) async {
    final dto = AssetDto.fromDomain(asset);
    await localDataSource.updateAsset(dto);
    return asset;
  }

  @override
  Future<void> deleteAsset(String assetId) async {
    await localDataSource.deleteAsset(assetId);
  }
}
