import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/asset.dart';
import '../viewmodels/asset_viewmodel.dart';
import '../viewmodels/workspace_viewmodel.dart';
import '../widgets/add_asset_bottom_sheet.dart';
import '../widgets/asset_card.dart';
import '../widgets/context_switcher_bar.dart';
import '../widgets/live_activity_pill.dart';
import '../widgets/station_grid_view.dart';

/// Ana Kontrol Paneli Görünümü (Dashboard View - MVVM View)
class DashboardView extends StatefulWidget {
  const DashboardView({super.key});

  @override
  State<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends State<DashboardView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initData();
    });
  }

  Future<void> _initData() async {
    final workspaceVm = context.read<WorkspaceViewModel>();
    final assetVm = context.read<AssetViewModel>();

    await workspaceVm.loadWorkspaces();
    if (workspaceVm.activeWorkspace != null) {
      await assetVm.loadAssets(workspaceVm.activeWorkspace!);
    }
  }

  void _openAddAssetSheet() {
    final workspaceVm = context.read<WorkspaceViewModel>();
    final assetVm = context.read<AssetViewModel>();
    final currentWorkspace = workspaceVm.activeWorkspace;
    if (currentWorkspace == null) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.surface,
      builder: (ctx) => AddAssetBottomSheet(
        currentWorkspace: currentWorkspace,
        onAssetCreated: (newAsset) {
          assetVm.addAsset(newAsset, currentWorkspace);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('${newAsset.name} başarıyla oluşturuldu.'),
              backgroundColor: AppColors.emerald,
              behavior: SnackBarBehavior.floating,
            ),
          );
        },
      ),
    );
  }

  void _showQrModal(Asset asset) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        backgroundColor: AppColors.surfaceElevated,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 140,
                height: 140,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                ),
                alignment: Alignment.center,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.qr_code_2_rounded, color: Colors.black, size: 90),
                    Text(
                      asset.qrCode ?? 'YONNED-QR',
                      style: const TextStyle(
                        color: Colors.black,
                        fontSize: 9,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Text(
                asset.name,
                style: const TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                asset.identifier ?? asset.assetType.displayName,
                style: const TextStyle(color: AppColors.textMuted, fontSize: 13),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppColors.textPrimary,
                    side: const BorderSide(color: AppColors.surfaceBorder),
                  ),
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('Kapat'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final workspaceVm = context.watch<WorkspaceViewModel>();
    final assetVm = context.watch<AssetViewModel>();
    final activeWorkspace = workspaceVm.activeWorkspace;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: activeWorkspace != null
            ? ContextSwitcherBar(
                activeWorkspace: activeWorkspace,
                allWorkspaces: workspaceVm.workspaces,
                onWorkspaceSelected: (ws) {
                  workspaceVm.switchWorkspace(ws);
                  assetVm.loadAssets(ws);
                },
              )
            : const Text('Yonned'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none_rounded, color: AppColors.textSecondary),
            onPressed: () {},
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: workspaceVm.isLoading || assetVm.isLoading
          ? const Center(
              child: CircularProgressIndicator(color: AppColors.emerald),
            )
          : RefreshIndicator(
              color: AppColors.emerald,
              backgroundColor: AppColors.surface,
              onRefresh: () async {
                if (activeWorkspace != null) {
                  await assetVm.loadAssets(activeWorkspace);
                }
              },
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                children: [
                  // 1. Canlı Süreç Bildirimi (Kişisel modda iken hekim/usta canlı sürecini gösterir)
                  if (activeWorkspace != null && activeWorkspace.isPersonal) ...[
                    LiveActivityPill(
                      title: '🐾 Tarçın • Pati Veteriner Kliniğinde',
                      subtitle: 'Operasyon Tamamlandı, Dinlenme Kafesi #1',
                      timeText: '14:20 Canlı',
                      onTap: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Canlı takip linki: https://yonned.com/t/tarcin'),
                            backgroundColor: AppColors.emerald,
                            behavior: SnackBarBehavior.floating,
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 24),
                  ],

                  // 2. Mod Başlığı ve İpucu
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            activeWorkspace?.name ?? '',
                            style: const TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 20,
                              fontWeight: FontWeight.w800,
                              letterSpacing: -0.5,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            activeWorkspace?.isPersonal == true
                                ? 'Kişisel Varlık Cüzdanınız'
                                : '${activeWorkspace?.subtitle ?? ""} İstasyon Yönetimi',
                            style: const TextStyle(
                              color: AppColors.textMuted,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                      // Hızlı Eylem Butonu
                      IconButton.filledTonal(
                        style: IconButton.styleFrom(
                          backgroundColor: activeWorkspace?.isPersonal == true
                              ? AppColors.amethyst.withValues(alpha: 0.15)
                              : AppColors.emerald.withValues(alpha: 0.15),
                        ),
                        icon: Icon(
                          Icons.add_rounded,
                          color: activeWorkspace?.isPersonal == true
                              ? AppColors.amethyst
                              : AppColors.emerald,
                        ),
                        onPressed: _openAddAssetSheet,
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // 3. İçerik Görünümü: İşletme ise İstasyon Izgarası, Kişisel ise Varlık Kartları
                  if (activeWorkspace?.isBusiness == true) ...[
                    StationGridView(
                      stations: assetVm.assets.where((a) => a.isStation).toList(),
                      onStationTap: (station) {
                        assetVm.toggleStationOccupancy(station);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(
                              station.isOccupied
                                  ? '${station.name} BOŞALDI (Çıkış Yapıldı).'
                                  : '${station.name} DOLDU (Yeni Süreç Başlatıldı).',
                            ),
                            backgroundColor:
                                station.isOccupied ? AppColors.emerald : AppColors.amber,
                            behavior: SnackBarBehavior.floating,
                            duration: const Duration(seconds: 1),
                          ),
                        );
                      },
                    ),
                  ] else ...[
                    // Kişisel Varlık Kartları
                    if (assetVm.assets.isEmpty)
                      const Center(
                        child: Padding(
                          padding: EdgeInsets.all(40.0),
                          child: Text(
                            'Henüz kayıtlı bir varlığınız yok.\nYukarıdaki (+) butonuna dokunarak kedi, köpek veya aracınızı ekleyin.',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: AppColors.textMuted),
                          ),
                        ),
                      )
                    else
                      ...assetVm.assets.map((asset) {
                        return AssetCard(
                          asset: asset,
                          onQrTap: () => _showQrModal(asset),
                          onShareTap: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('${asset.name} CRUD paylaşım ayarları açıldı.'),
                                backgroundColor: AppColors.cobalt,
                                behavior: SnackBarBehavior.floating,
                              ),
                            );
                          },
                        );
                      }),
                  ],
                ],
              ),
            ),
    );
  }
}
