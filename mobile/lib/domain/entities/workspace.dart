/// Çalışma Alanı Tipi (Workspace Context Type)
enum WorkspaceType {
  personal, // Bireysel Varlık Cüzdanı (Kedi, Köpek, Araba)
  branch,   // İşletme Şubesi / Bayi (Klinik şubesi, Oto yıkama şubesi)
}

/// Aktif Çalışma Alanı (Active Workspace Context)
/// Kullanıcının o anda hangi bağlamda (hangi dükkanda veya kişisel cüzdanında) olduğunu modeller.
class Workspace {
  final String id;
  final String name;
  final String? subtitle;
  final WorkspaceType type;
  final String? organizationId;
  final String? branchId;
  final String icon;

  const Workspace({
    required this.id,
    required this.name,
    this.subtitle,
    required this.type,
    this.organizationId,
    this.branchId,
    required this.icon,
  });

  bool get isPersonal => type == WorkspaceType.personal;
  bool get isBusiness => type == WorkspaceType.branch;

  /// Fabrika: Kişisel Cüzdan Bağlamı
  factory Workspace.personal({required String personId}) {
    return Workspace(
      id: 'personal_$personId',
      name: 'Kişisel Varlıklarım',
      subtitle: 'Kedi, Köpek, Taşıt & Cihazlarım',
      type: WorkspaceType.personal,
      icon: '🐾',
    );
  }

  /// Fabrika: İşletme Şubesi Bağlamı
  factory Workspace.branch({
    required String branchId,
    required String branchName,
    required String organizationId,
    required String organizationName,
    String icon = '🏢',
  }) {
    return Workspace(
      id: branchId,
      name: branchName,
      subtitle: organizationName,
      type: WorkspaceType.branch,
      organizationId: organizationId,
      branchId: branchId,
      icon: icon,
    );
  }
}
