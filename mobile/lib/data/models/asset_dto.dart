import 'dart:convert';
import '../../domain/entities/asset.dart';
import '../../domain/entities/asset_type.dart';

/// Asset Veri Transfer Nesnesi (DTO / Data Mapping)
class AssetDto {
  final String id;
  final String tenantId;
  final String? parentId;
  final String? ownerPersonId;
  final String ownerType;
  final String assetType;
  final String name;
  final String? identifier;
  final String? qrCode;
  final int capacity;
  final Map<String, dynamic> metadata;
  final bool isActive;
  final String createdAt;
  final String updatedAt;

  AssetDto({
    required this.id,
    required this.tenantId,
    this.parentId,
    this.ownerPersonId,
    required this.ownerType,
    required this.assetType,
    required this.name,
    this.identifier,
    this.qrCode,
    required this.capacity,
    required this.metadata,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Domain Entity'den DTO Üretimi
  factory AssetDto.fromDomain(Asset asset) {
    return AssetDto(
      id: asset.id,
      tenantId: asset.tenantId,
      parentId: asset.parentId,
      ownerPersonId: asset.ownerPersonId,
      ownerType: asset.ownerType,
      assetType: asset.assetType.name,
      name: asset.name,
      identifier: asset.identifier,
      qrCode: asset.qrCode,
      capacity: asset.capacity,
      metadata: asset.metadata,
      isActive: asset.isActive,
      createdAt: asset.createdAt.toIso8601String(),
      updatedAt: asset.updatedAt.toIso8601String(),
    );
  }

  /// SQLite Veritabanı Haritasından DTO Üretimi
  factory AssetDto.fromDb(Map<String, dynamic> map) {
    Map<String, dynamic> parsedMetadata = {};
    if (map['metadata'] != null) {
      if (map['metadata'] is String) {
        try {
          parsedMetadata = jsonDecode(map['metadata'] as String);
        } catch (_) {
          parsedMetadata = {};
        }
      } else if (map['metadata'] is Map) {
        parsedMetadata = Map<String, dynamic>.from(map['metadata']);
      }
    }

    return AssetDto(
      id: map['id'] as String,
      tenantId: map['tenant_id'] as String,
      parentId: map['parent_id'] as String?,
      ownerPersonId: map['owner_person_id'] as String?,
      ownerType: map['owner_type'] as String? ?? 'business',
      assetType: map['asset_type'] as String,
      name: map['name'] as String,
      identifier: map['identifier'] as String?,
      qrCode: map['qr_code'] as String?,
      capacity: map['capacity'] as int? ?? 1,
      metadata: parsedMetadata,
      isActive: (map['is_active'] as int? ?? 1) == 1,
      createdAt: map['created_at'] as String,
      updatedAt: map['updated_at'] as String,
    );
  }

  /// SQLite Veritabanına Yazım Haritası
  Map<String, dynamic> toDbMap() {
    return {
      'id': id,
      'tenant_id': tenantId,
      'parent_id': parentId,
      'owner_person_id': ownerPersonId,
      'owner_type': ownerType,
      'asset_type': assetType,
      'name': name,
      'identifier': identifier,
      'qr_code': qrCode,
      'capacity': capacity,
      'metadata': jsonEncode(metadata),
      'is_active': isActive ? 1 : 0,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }

  /// DTO'dan Domain Entity'ye Dönüşüm
  Asset toDomain() {
    return Asset(
      id: id,
      tenantId: tenantId,
      parentId: parentId,
      ownerPersonId: ownerPersonId,
      ownerType: ownerType,
      assetType: AssetType.fromString(assetType),
      name: name,
      identifier: identifier,
      qrCode: qrCode,
      capacity: capacity,
      metadata: metadata,
      isActive: isActive,
      createdAt: DateTime.tryParse(createdAt) ?? DateTime.now(),
      updatedAt: DateTime.tryParse(updatedAt) ?? DateTime.now(),
    );
  }
}
