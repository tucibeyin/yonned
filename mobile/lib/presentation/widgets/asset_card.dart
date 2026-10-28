import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/asset.dart';
import '../../domain/entities/asset_type.dart';
import 'crud_badge.dart';

/// Polimorfik Varlık Kartı (Kişisel Varlıklar: Kedi, Köpek, Araç)
class AssetCard extends StatelessWidget {
  final Asset asset;
  final VoidCallback? onShareTap;
  final VoidCallback? onQrTap;

  const AssetCard({
    super.key,
    required this.asset,
    this.onShareTap,
    this.onQrTap,
  });

  String get _typeIcon {
    switch (asset.assetType) {
      case AssetType.pet:
        final species = asset.metadata['species'] as String?;
        return species == 'Kedi' ? '🐈' : '🐕';
      case AssetType.vehicle:
        return '🚗';
      case AssetType.device:
        return '📱';
      default:
        return '📦';
    }
  }

  @override
  Widget build(BuildContext context) {
    final status = asset.metadata['status'] as String? ?? 'Aktif';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceElevated,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.surfaceBorder, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              // Varlık İkonu
              Container(
                width: 44,
                height: 44,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: AppColors.amethyst.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.amethyst.withValues(alpha: 0.3),
                    width: 1,
                  ),
                ),
                child: Text(
                  _typeIcon,
                  style: const TextStyle(fontSize: 22),
                ),
              ),
              const SizedBox(width: 14),
              // Varlık Adı & Kimlik
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      asset.name,
                      style: const TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        letterSpacing: -0.3,
                      ),
                    ),
                    if (asset.identifier != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        asset.identifier!,
                        style: const TextStyle(
                          color: AppColors.textMuted,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              // QR Butonu
              if (asset.qrCode != null)
                IconButton(
                  icon: const Icon(Icons.qr_code_2_rounded, color: AppColors.emerald, size: 22),
                  onPressed: onQrTap,
                  tooltip: 'QR Kodu Görüntüle',
                ),
            ],
          ),
          const SizedBox(height: 12),
          // Durum Satırı
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.04),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.info_outline_rounded, color: AppColors.textSecondary, size: 14),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    status,
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 12,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
          if (asset.shares.isNotEmpty) ...[
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.share_outlined, color: AppColors.textMuted, size: 13),
                const SizedBox(width: 6),
                const Text(
                  'Paylaşılan İzinler:',
                  style: TextStyle(color: AppColors.textMuted, fontSize: 11),
                ),
                const SizedBox(width: 6),
                CrudBadge(share: asset.shares.first),
                const Spacer(),
                GestureDetector(
                  onTap: onShareTap,
                  child: const Text(
                    'Düzenle',
                    style: TextStyle(
                      color: AppColors.cobalt,
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
