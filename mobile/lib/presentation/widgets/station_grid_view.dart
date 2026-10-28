import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/asset.dart';

/// Mekansal İstasyon Izgarası (Station Grid View - Cages, Bays, Lifts)
class StationGridView extends StatelessWidget {
  final List<Asset> stations;
  final Function(Asset) onStationTap;

  const StationGridView({
    super.key,
    required this.stations,
    required this.onStationTap,
  });

  @override
  Widget build(BuildContext context) {
    if (stations.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: const [
              Icon(Icons.inbox_rounded, color: AppColors.textMuted, size: 48),
              SizedBox(height: 12),
              Text(
                'Bu şubede henüz kayıtlı istasyon/kafes bulunmuyor.',
                style: TextStyle(color: AppColors.textSecondary),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    final occupiedCount = stations.where((s) => s.isOccupied).length;
    final totalCount = stations.length;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Özet İstatistik Çubuğu
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'İSTASYONLAR ($totalCount)',
              style: const TextStyle(
                color: AppColors.textMuted,
                fontSize: 12,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.6,
              ),
            ),
            Row(
              children: [
                _buildStatusDot(AppColors.emerald, '${totalCount - occupiedCount} Boş'),
                const SizedBox(width: 12),
                _buildStatusDot(AppColors.crimson, '$occupiedCount Dolu'),
              ],
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Izgara
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.15,
          ),
          itemCount: stations.length,
          itemBuilder: (context, index) {
            final station = stations[index];
            final isOccupied = station.isOccupied;

            return GestureDetector(
              onTap: () => onStationTap(station),
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.surfaceElevated,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isOccupied
                        ? AppColors.crimson.withValues(alpha: 0.4)
                        : AppColors.emerald.withValues(alpha: 0.3),
                    width: 1.2,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          station.assetType.displayName,
                          style: const TextStyle(
                            color: AppColors.textMuted,
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: isOccupied
                                ? AppColors.crimson.withValues(alpha: 0.15)
                                : AppColors.emerald.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            isOccupied ? 'DOLU' : 'BOŞ',
                            style: TextStyle(
                              color: isOccupied ? AppColors.crimson : AppColors.emerald,
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      station.name,
                      style: const TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const Spacer(),
                    if (isOccupied && station.activeSubjectName != null) ...[
                      Text(
                        station.activeSubjectName!,
                        style: const TextStyle(
                          color: AppColors.amber,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (station.metadata['status_note'] != null)
                        Text(
                          station.metadata['status_note'] as String,
                          style: const TextStyle(
                            color: AppColors.textMuted,
                            fontSize: 10,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                    ] else
                      const Text(
                        'Kabul İçin Dokun ➔',
                        style: TextStyle(
                          color: AppColors.textMuted,
                          fontSize: 11,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                  ],
                ),
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildStatusDot(Color color, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(
          text,
          style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
        ),
      ],
    );
  }
}
