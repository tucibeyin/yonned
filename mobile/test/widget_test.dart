import 'package:flutter_test/flutter_test.dart';
import 'package:yonned_mobile/domain/entities/asset.dart';
import 'package:yonned_mobile/domain/entities/asset_share.dart';
import 'package:yonned_mobile/domain/entities/asset_type.dart';
import 'package:yonned_mobile/domain/entities/workspace.dart';

void main() {
  group('Yonned Domain Entities Testi', () {
    test('Workspace oluşturma ve tip doğrulama', () {
      final personalWs = Workspace.personal(personId: 'user_123');
      expect(personalWs.isPersonal, isTrue);
      expect(personalWs.isBusiness, isFalse);
      expect(personalWs.icon, '🐾');

      final branchWs = Workspace.branch(
        branchId: 'branch_1',
        branchName: 'Beşiktaş Şubesi',
        organizationId: 'org_1',
        organizationName: 'Pati Veteriner',
      );
      expect(branchWs.isBusiness, isTrue);
      expect(branchWs.name, 'Beşiktaş Şubesi');
    });

    test('Asset doluluk ve istasyon tipi doğrulama', () {
      final cage = Asset(
        id: 'cage_1',
        tenantId: 'tenant_1',
        assetType: AssetType.cage,
        name: 'Kafes #1',
        metadata: {'is_occupied': true, 'active_subject_name': 'Pamuk'},
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(cage.isStation, isTrue);
      expect(cage.isOccupied, isTrue);
      expect(cage.activeSubjectName, 'Pamuk');

      final pet = Asset(
        id: 'pet_1',
        tenantId: 'tenant_1',
        ownerType: 'customer',
        assetType: AssetType.pet,
        name: 'Tarçın',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(pet.isCustomerAsset, isTrue);
      expect(pet.isStation, isFalse);
    });

    test('AssetShare (Vasıf) 4 Atomik CRUD izin kontrolü', () {
      final fullShare = AssetShare(
        id: 's1',
        assetId: 'a1',
        sharedWithPersonId: 'p1',
        canCreate: true,
        canRead: true,
        canUpdate: true,
        canDelete: true,
        createdAt: DateTime.now(),
      );
      expect(fullShare.isFullAccess, isTrue);
      expect(fullShare.isReadOnly, isFalse);

      final readOnlyShare = AssetShare(
        id: 's2',
        assetId: 'a1',
        sharedWithPersonId: 'p2',
        canRead: true,
        createdAt: DateTime.now(),
      );
      expect(readOnlyShare.isReadOnly, isTrue);
      expect(readOnlyShare.isFullAccess, isFalse);
    });
  });
}
