import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../../core/theme/app_colors.dart';
import '../../domain/entities/asset.dart';
import '../../domain/entities/asset_type.dart';
import '../../domain/entities/workspace.dart';

/// Yeni Varlık Ekleme Çekmecesi (Add Asset Bottom Sheet)
class AddAssetBottomSheet extends StatefulWidget {
  final Workspace currentWorkspace;
  final Function(Asset) onAssetCreated;

  const AddAssetBottomSheet({
    super.key,
    required this.currentWorkspace,
    required this.onAssetCreated,
  });

  @override
  State<AddAssetBottomSheet> createState() => _AddAssetBottomSheetState();
}

class _AddAssetBottomSheetState extends State<AddAssetBottomSheet> {
  final _nameController = TextEditingController();
  final _identifierController = TextEditingController();
  late AssetType _selectedType;

  @override
  void initState() {
    super.initState();
    // Bağlama göre varsayılan tipi seç
    if (widget.currentWorkspace.isPersonal) {
      _selectedType = AssetType.pet;
    } else {
      _selectedType = AssetType.cage;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _identifierController.dispose();
    super.dispose();
  }

  void _submit() {
    final name = _nameController.text.trim();
    if (name.isEmpty) return;

    final id = const Uuid().v4();
    final now = DateTime.now();

    final newAsset = Asset(
      id: id,
      tenantId: widget.currentWorkspace.organizationId ?? 'tenant_personal_me',
      parentId: widget.currentWorkspace.branchId,
      ownerType: widget.currentWorkspace.isPersonal ? 'customer' : 'business',
      assetType: _selectedType,
      name: name,
      identifier: _identifierController.text.trim().isNotEmpty
          ? _identifierController.text.trim()
          : null,
      qrCode: 'YONNED-${_selectedType.name.toUpperCase()}-${id.substring(0, 6)}',
      capacity: 1,
      metadata: {
        'status': 'Yeni Kayıt Oluşturuldu',
        if (_selectedType == AssetType.pet) 'species': 'Evcil Hayvan',
      },
      isActive: true,
      createdAt: now,
      updatedAt: now,
    );

    widget.onAssetCreated(newAsset);
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final isPersonal = widget.currentWorkspace.isPersonal;
    final availableTypes = isPersonal
        ? [AssetType.pet, AssetType.vehicle, AssetType.device]
        : [AssetType.cage, AssetType.station, AssetType.bay, AssetType.lift];

    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
        left: 20,
        right: 20,
        top: 24,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 18),
          Text(
            isPersonal ? 'Yeni Kişisel Varlık Ekle' : 'Yeni İstasyon / Kafes Ekle',
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            isPersonal
                ? 'Kediniz, köpeğiniz veya aracınız için benzersiz QR kodlu kayıt oluşturun.'
                : '${widget.currentWorkspace.name} için yeni bir işlem noktası tanımlayın.',
            style: const TextStyle(color: AppColors.textMuted, fontSize: 13),
          ),
          const SizedBox(height: 18),
          // Tip Seçici
          Wrap(
            spacing: 8,
            children: availableTypes.map((type) {
              final isSelected = type == _selectedType;
              return ChoiceChip(
                label: Text(type.displayName),
                selected: isSelected,
                selectedColor: isPersonal
                    ? AppColors.amethyst.withValues(alpha: 0.25)
                    : AppColors.emerald.withValues(alpha: 0.25),
                backgroundColor: AppColors.surfaceElevated,
                labelStyle: TextStyle(
                  color: isSelected
                      ? (isPersonal ? AppColors.amethyst : AppColors.emerald)
                      : AppColors.textSecondary,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                  fontSize: 12,
                ),
                side: BorderSide(
                  color: isSelected
                      ? (isPersonal ? AppColors.amethyst : AppColors.emerald)
                      : AppColors.surfaceBorder,
                ),
                onSelected: (selected) {
                  if (selected) setState(() => _selectedType = type);
                },
              );
            }).toList(),
          ),
          const SizedBox(height: 16),
          // Ad Alanı
          TextField(
            controller: _nameController,
            style: const TextStyle(color: AppColors.textPrimary, fontSize: 14),
            decoration: InputDecoration(
              labelText: isPersonal ? 'Varlık Adı (örn: Tarçın, BMW 3.20)' : 'İstasyon Adı (örn: Kafes #4)',
              labelStyle: const TextStyle(color: AppColors.textMuted),
              filled: true,
              fillColor: AppColors.surfaceElevated,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.surfaceBorder),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.surfaceBorder),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.emerald),
              ),
            ),
          ),
          const SizedBox(height: 12),
          // Kimlik Alanı (Çip / Plaka)
          TextField(
            controller: _identifierController,
            style: const TextStyle(color: AppColors.textPrimary, fontSize: 14),
            decoration: InputDecoration(
              labelText: isPersonal ? 'Kimlikleyici (Çip No, Plaka, Seri No)' : 'Açıklama / Kapasite Notu',
              labelStyle: const TextStyle(color: AppColors.textMuted),
              filled: true,
              fillColor: AppColors.surfaceElevated,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.surfaceBorder),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.surfaceBorder),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.emerald),
              ),
            ),
          ),
          const SizedBox(height: 20),
          // Kaydet Butonu
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: isPersonal ? AppColors.amethyst : AppColors.emerald,
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: _submit,
              child: const Text(
                'Varlığı Oluştur ve QR Bas ➔',
                style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
