import 'package:flutter/foundation.dart';
import '../../domain/entities/asset.dart';
import '../../domain/entities/asset_share.dart';
import '../../domain/entities/workspace.dart';
import '../../domain/usecases/create_asset_usecase.dart';
import '../../domain/usecases/get_assets_by_workspace_usecase.dart';
import '../../domain/usecases/share_asset_usecase.dart';
import '../../domain/repositories/i_asset_repository.dart';

/// Varlık Listesi ve İşlemleri (MVVM Asset ViewModel)
class AssetViewModel extends ChangeNotifier {
  final GetAssetsByWorkspaceUseCase getAssetsUseCase;
  final CreateAssetUseCase createAssetUseCase;
  final ShareAssetUseCase shareAssetUseCase;
  final IAssetRepository assetRepository;

  AssetViewModel({
    required this.getAssetsUseCase,
    required this.createAssetUseCase,
    required this.shareAssetUseCase,
    required this.assetRepository,
  });

  List<Asset> _assets = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<Asset> get assets => _assets;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  // İstatistikler (İşletme modu için)
  int get totalStations => _assets.where((a) => a.isStation).length;
  int get occupiedStations => _assets.where((a) => a.isStation && a.isOccupied).length;
  int get freeStations => totalStations - occupiedStations;

  /// Seçili çalışma alanına göre varlıkları yükler
  Future<void> loadAssets(Workspace workspace) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _assets = await getAssetsUseCase.execute(workspace);
    } catch (e) {
      _errorMessage = 'Varlıklar yüklenirken hata oluştu: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Yeni varlık ekler (kedi, köpek, araba veya yeni kafes/peron)
  Future<bool> addAsset(Asset asset, Workspace currentWorkspace) async {
    try {
      final created = await createAssetUseCase.execute(asset);
      _assets.insert(0, created);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Varlık eklenemedi: $e';
      notifyListeners();
      return false;
    }
  }

  /// İstasyonun doluluk durumunu değiştirir (Canlı Demo / Check-in simülasyonu)
  Future<void> toggleStationOccupancy(Asset station) async {
    final bool newOccupied = !station.isOccupied;
    final Map<String, dynamic> newMetadata = Map.from(station.metadata);
    newMetadata['is_occupied'] = newOccupied;

    if (newOccupied) {
      newMetadata['active_subject_name'] = 'Yeni Hasta / Araç';
      newMetadata['status_note'] = 'Hizmet Başlatıldı';
    } else {
      newMetadata.remove('active_subject_name');
      newMetadata.remove('status_note');
    }

    final updated = station.copyWith(metadata: newMetadata);
    await assetRepository.updateAsset(updated);

    final index = _assets.indexWhere((a) => a.id == station.id);
    if (index != -1) {
      _assets[index] = updated;
      notifyListeners();
    }
  }

  /// Varlık paylaşımı gerçekleştirir (Evrensel CRUD)
  Future<bool> shareAsset(AssetShare share) async {
    try {
      final result = await shareAssetUseCase.execute(share);
      final assetIndex = _assets.indexWhere((a) => a.id == share.assetId);
      if (assetIndex != -1) {
        final currentShares = List<AssetShare>.from(_assets[assetIndex].shares);
        currentShares.add(result);
        _assets[assetIndex] = _assets[assetIndex].copyWith(shares: currentShares);
        notifyListeners();
      }
      return true;
    } catch (e) {
      _errorMessage = 'Paylaşım yapılamadı: $e';
      notifyListeners();
      return false;
    }
  }
}
