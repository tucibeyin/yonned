import 'asset_type.dart';
import 'asset_share.dart';

/// Evrensel Varlık (Universal Asset / Property / Subject / Spatial Container)
/// Özyinelemeli ağaç (parentId) yapısıyla hem dükkanları/kafesleri hem de kedi/araba gibi özneleri modeller.
class Asset {
  final String id;
  final String tenantId;
  final String? parentId;
  final String? ownerPersonId;
  final String ownerType; // 'business' | 'customer'
  final AssetType assetType;
  final String name;
  final String? identifier; // Çip No, Plaka, IMEI
  final String? qrCode;
  final int capacity;
  final Map<String, dynamic> metadata;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<AssetShare> shares;

  const Asset({
    required this.id,
    required this.tenantId,
    this.parentId,
    this.ownerPersonId,
    this.ownerType = 'business',
    required this.assetType,
    required this.name,
    this.identifier,
    this.qrCode,
    this.capacity = 1,
    this.metadata = const {},
    this.isActive = true,
    required this.createdAt,
    required this.updatedAt,
    this.shares = const [],
  });

  /// Varlığın kişisel mi yoksa ticari mi olduğu
  bool get isCustomerAsset => ownerType == 'customer';
  bool get isBusinessAsset => ownerType == 'business';

  /// Varlığın mekansal bir istasyon (kafes, lift, peron) olup olmadığı
  bool get isStation =>
      assetType == AssetType.cage ||
      assetType == AssetType.station ||
      assetType == AssetType.bay ||
      assetType == AssetType.lift;

  /// İstasyonun dolu olup olmadığı (metadata içindeki current_subject kontrolü)
  bool get isOccupied => metadata['is_occupied'] == true;

  /// İstasyonda bulunan aktif özne adı (örn: "Pamuk (Kedi)")
  String? get activeSubjectName => metadata['active_subject_name'] as String?;

  Asset copyWith({
    String? id,
    String? tenantId,
    String? parentId,
    String? ownerPersonId,
    String? ownerType,
    AssetType? assetType,
    String? name,
    String? identifier,
    String? qrCode,
    int? capacity,
    Map<String, dynamic>? metadata,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
    List<AssetShare>? shares,
  }) {
    return Asset(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      parentId: parentId ?? this.parentId,
      ownerPersonId: ownerPersonId ?? this.ownerPersonId,
      ownerType: ownerType ?? this.ownerType,
      assetType: assetType ?? this.assetType,
      name: name ?? this.name,
      identifier: identifier ?? this.identifier,
      qrCode: qrCode ?? this.qrCode,
      capacity: capacity ?? this.capacity,
      metadata: metadata ?? this.metadata,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      shares: shares ?? this.shares,
    );
  }
}
