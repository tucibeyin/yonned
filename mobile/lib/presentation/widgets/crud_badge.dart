import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/asset_share.dart';

/// 4 Atomik CRUD Yetki Rozeti [C] [R] [U] [D]
class CrudBadge extends StatelessWidget {
  final AssetShare share;

  const CrudBadge({super.key, required this.share});

  Widget _buildLetter(String letter, bool isEnabled) {
    return Container(
      width: 18,
      height: 18,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: isEnabled ? AppColors.emerald.withValues(alpha: 0.2) : Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: isEnabled ? AppColors.emerald : Colors.white.withValues(alpha: 0.1),
          width: 0.8,
        ),
      ),
      child: Text(
        letter,
        style: TextStyle(
          color: isEnabled ? AppColors.emerald : AppColors.textMuted,
          fontSize: 10,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildLetter('C', share.canCreate),
        const SizedBox(width: 3),
        _buildLetter('R', share.canRead),
        const SizedBox(width: 3),
        _buildLetter('U', share.canUpdate),
        const SizedBox(width: 3),
        _buildLetter('D', share.canDelete),
      ],
    );
  }
}
