import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/workspace.dart';

/// Üst Bağlam Değiştirici Hapı ve Seçim Penceresi (Context Switcher)
class ContextSwitcherBar extends StatelessWidget {
  final Workspace activeWorkspace;
  final List<Workspace> allWorkspaces;
  final Function(Workspace) onWorkspaceSelected;

  const ContextSwitcherBar({
    super.key,
    required this.activeWorkspace,
    required this.allWorkspaces,
    required this.onWorkspaceSelected,
  });

  void _showWorkspaceModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      isScrollControlled: true,
      builder: (ctx) {
        // İşletmelere göre grupla
        final Map<String, List<Workspace>> groups = {};
        for (var w in allWorkspaces) {
          final groupTitle = w.subtitle ?? 'Kişisel';
          groups.putIfAbsent(groupTitle, () => []).add(w);
        }

        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
          constraints: BoxConstraints(
            maxHeight: MediaQuery.of(context).size.height * 0.75,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Başlık ve Çizgi
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 18),
              const Text(
                'Çalışma Alanı Değiştir',
                style: TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Dilediğiniz şubenize veya kişisel varlık cüzdanınıza anında geçin.',
                style: TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 13,
                ),
              ),
              const SizedBox(height: 18),
              Expanded(
                child: ListView(
                  children: groups.entries.map((entry) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.only(top: 12, bottom: 8),
                          child: Text(
                            entry.key.toUpperCase(),
                            style: const TextStyle(
                              color: AppColors.cobalt,
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.8,
                            ),
                          ),
                        ),
                        ...entry.value.map((ws) {
                          final isSelected = ws.id == activeWorkspace.id;
                          return Container(
                            margin: const EdgeInsets.only(bottom: 6),
                            decoration: BoxDecoration(
                              color: isSelected
                                  ? AppColors.emerald.withValues(alpha: 0.12)
                                  : AppColors.surfaceElevated,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: isSelected
                                    ? AppColors.emerald
                                    : AppColors.surfaceBorder,
                                width: isSelected ? 1.5 : 1,
                              ),
                            ),
                            child: ListTile(
                              leading: Text(
                                ws.icon,
                                style: const TextStyle(fontSize: 22),
                              ),
                              title: Text(
                                ws.name,
                                style: TextStyle(
                                  color: isSelected
                                      ? AppColors.emerald
                                      : AppColors.textPrimary,
                                  fontWeight: isSelected
                                      ? FontWeight.w700
                                      : FontWeight.w600,
                                  fontSize: 14,
                                ),
                              ),
                              subtitle: ws.isBusiness
                                  ? Text(
                                      ws.subtitle ?? '',
                                      style: const TextStyle(
                                        color: AppColors.textMuted,
                                        fontSize: 12,
                                      ),
                                    )
                                  : null,
                              trailing: isSelected
                                  ? const Icon(
                                      Icons.check_circle_rounded,
                                      color: AppColors.emerald,
                                      size: 20,
                                    )
                                  : null,
                              onTap: () {
                                Navigator.pop(ctx);
                                onWorkspaceSelected(ws);
                              },
                            ),
                          );
                        }),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => _showWorkspaceModal(context),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: AppColors.surfaceElevated,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: activeWorkspace.isPersonal
                ? AppColors.amethyst.withValues(alpha: 0.4)
                : AppColors.cobalt.withValues(alpha: 0.4),
            width: 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              activeWorkspace.icon,
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(width: 8),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 180),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    activeWorkspace.name,
                    style: const TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (activeWorkspace.isBusiness && activeWorkspace.subtitle != null)
                    Text(
                      activeWorkspace.subtitle!,
                      style: const TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 10,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            const SizedBox(width: 6),
            const Icon(
              Icons.keyboard_arrow_down_rounded,
              color: AppColors.textSecondary,
              size: 18,
            ),
          ],
        ),
      ),
    );
  }
}
