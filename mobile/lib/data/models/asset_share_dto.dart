import '../../domain/entities/asset_share.dart';

/// AssetShare / Vasif Veri Transfer Nesnesi (DTO)
class AssetShareDto {
  final String id;
  final String assetId;
  final String sharedWithPersonId;
  final bool canCreate;
  final bool canRead;
  final bool canUpdate;
  final bool canDelete;
  final String createdAt;

  AssetShareDto({
    required this.id,
    required this.assetId,
    required this.sharedWithPersonId,
    required this.canCreate,
    required this.canRead,
    required this.canUpdate,
    required this.canDelete,
    required this.createdAt,
  });

  factory AssetShareDto.fromDomain(AssetShare share) {
    return AssetShareDto(
      id: share.id,
      assetId: share.assetId,
      sharedWithPersonId: share.sharedWithPersonId,
      canCreate: share.canCreate,
      canRead: share.canRead,
      canUpdate: share.canUpdate,
      canDelete: share.canDelete,
      createdAt: share.createdAt.toIso8601String(),
    );
  }

  factory AssetShareDto.fromDb(Map<String, dynamic> map) {
    return AssetShareDto(
      id: map['id'] as String,
      assetId: map['asset_id'] as String,
      sharedWithPersonId: map['shared_with_person_id'] as String,
      canCreate: (map['can_create'] as int? ?? 0) == 1,
      canRead: (map['can_read'] as int? ?? 1) == 1,
      canUpdate: (map['can_update'] as int? ?? 0) == 1,
      canDelete: (map['can_delete'] as int? ?? 0) == 1,
      createdAt: map['created_at'] as String,
    );
  }

  Map<String, dynamic> toDbMap() {
    return {
      'id': id,
      'asset_id': assetId,
      'shared_with_person_id': sharedWithPersonId,
      'can_create': canCreate ? 1 : 0,
      'can_read': canRead ? 1 : 0,
      'can_update': canUpdate ? 1 : 0,
      'can_delete': canDelete ? 1 : 0,
      'created_at': createdAt,
    };
  }

  AssetShare toDomain({String? personName}) {
    return AssetShare(
      id: id,
      assetId: assetId,
      sharedWithPersonId: sharedWithPersonId,
      sharedWithPersonName: personName,
      canCreate: canCreate,
      canRead: canRead,
      canUpdate: canUpdate,
      canDelete: canDelete,
      createdAt: DateTime.tryParse(createdAt) ?? DateTime.now(),
    );
  }
}
