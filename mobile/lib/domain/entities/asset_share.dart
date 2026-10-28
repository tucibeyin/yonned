/// Vasıf / Varlık Paylaşım İzin Modeli (The Universal CRUD Permission Contract)
/// Bir varlığı paylaşan kişi, alıcıya birbirinden bağımsız 4 temel CRUD yetkisi verir.
class AssetShare {
  final String id;
  final String assetId;
  final String sharedWithPersonId;
  final String? sharedWithPersonName;
  final bool canCreate; // Ekle: Yeni süreç, alt mekan, sarf veya kayıt oluşturabilme
  final bool canRead;   // Oku: Durumu, fotoğrafları ve canlı takibi görüntüleyebilme
  final bool canUpdate; // Güncelle: Not ve durumları değiştirebilme
  final bool canDelete; // Sil: Süreci veya varlığı silebilme/iptal edebilme
  final DateTime createdAt;

  const AssetShare({
    required this.id,
    required this.assetId,
    required this.sharedWithPersonId,
    this.sharedWithPersonName,
    this.canCreate = false,
    this.canRead = true,
    this.canUpdate = false,
    this.canDelete = false,
    required this.createdAt,
  });

  /// Tam yetki kontrolü
  bool get isFullAccess => canCreate && canRead && canUpdate && canDelete;

  /// Yalnızca izleme (Salt okunur) kontrolü
  bool get isReadOnly => canRead && !canCreate && !canUpdate && !canDelete;

  AssetShare copyWith({
    String? id,
    String? assetId,
    String? sharedWithPersonId,
    String? sharedWithPersonName,
    bool? canCreate,
    bool? canRead,
    bool? canUpdate,
    bool? canDelete,
    DateTime? createdAt,
  }) {
    return AssetShare(
      id: id ?? this.id,
      assetId: assetId ?? this.assetId,
      sharedWithPersonId: sharedWithPersonId ?? this.sharedWithPersonId,
      sharedWithPersonName: sharedWithPersonName ?? this.sharedWithPersonName,
      canCreate: canCreate ?? this.canCreate,
      canRead: canRead ?? this.canRead,
      canUpdate: canUpdate ?? this.canUpdate,
      canDelete: canDelete ?? this.canDelete,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
