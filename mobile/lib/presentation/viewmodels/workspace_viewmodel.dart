import 'package:flutter/foundation.dart';
import '../../domain/entities/workspace.dart';
import '../../domain/usecases/get_workspaces_usecase.dart';

/// Çalışma Alanı ve Bağlam Yönetimi (MVVM Workspace ViewModel)
class WorkspaceViewModel extends ChangeNotifier {
  final GetWorkspacesUseCase getWorkspacesUseCase;

  WorkspaceViewModel({required this.getWorkspacesUseCase});

  List<Workspace> _workspaces = [];
  Workspace? _activeWorkspace;
  bool _isLoading = false;
  String? _errorMessage;

  List<Workspace> get workspaces => _workspaces;
  Workspace? get activeWorkspace => _activeWorkspace;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  /// İşletmelere göre gruplanmış çalışma alanları
  Map<String, List<Workspace>> get groupedWorkspaces {
    final Map<String, List<Workspace>> map = {};
    for (var w in _workspaces) {
      final key = w.subtitle ?? 'Diğer';
      map.putIfAbsent(key, () => []).add(w);
    }
    return map;
  }

  /// Tüm çalışma alanlarını yükler
  Future<void> loadWorkspaces() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _workspaces = await getWorkspacesUseCase.execute();
      if (_workspaces.isNotEmpty && _activeWorkspace == null) {
        // Varsayılan olarak ilk çalışma alanını (Kişisel Varlıklar) seç
        _activeWorkspace = _workspaces.first;
      }
    } catch (e) {
      _errorMessage = 'Çalışma alanları yüklenirken hata: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Aktif çalışma alanını değiştirir (Slack / Apple tarzı bağlam değişimi)
  void switchWorkspace(Workspace newWorkspace) {
    if (_activeWorkspace?.id == newWorkspace.id) return;
    _activeWorkspace = newWorkspace;
    notifyListeners();
  }
}
