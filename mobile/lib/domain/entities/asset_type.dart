/// Evrensel Varlık Tipleri (Universal Asset Types)
enum AssetType {
  // Mekansal ve Organizasyonel Varlıklar
  organization, // Şirket / Ana Kurum
  branch,       // Şube / Bayi
  floor,        // Kat
  room,         // Oda / Bölüm

  // Fiziksel İstasyonlar (Hizmetin icra edildiği yerler)
  cage,         // Veteriner Kafesi
  station,      // Muayene Masası / İş İstasyonu
  bay,          // Oto Yıkama Peronu
  lift,         // Oto Servis Lifti

  // Üzerinde İşlem Yapılan Özneler (Müşteri Varlıkları)
  pet,          // Evcil Hayvan (Kedi, Köpek vb.)
  vehicle,      // Taşıt (Otomobil, Motosiklet)
  device,       // Elektronik Cihaz (Telefon, Bilgisayar)

  // Sarf ve Donanım
  consumable,   // İlaç / Sarf Malzemesi
  equipment;    // Tıbbi Cihaz / Atölye Aleti

  String get displayName {
    switch (this) {
      case AssetType.organization:
        return 'Kurum / Şirket';
      case AssetType.branch:
        return 'Şube / Bayi';
      case AssetType.floor:
        return 'Kat';
      case AssetType.room:
        return 'Oda';
      case AssetType.cage:
        return 'Kafes';
      case AssetType.station:
        return 'İş İstasyonu';
      case AssetType.bay:
        return 'Yıkama Peronu';
      case AssetType.lift:
        return 'Servis Lifti';
      case AssetType.pet:
        return 'Evcil Hayvan';
      case AssetType.vehicle:
        return 'Taşıt';
      case AssetType.device:
        return 'Cihaz';
      case AssetType.consumable:
        return 'Sarf Malzemesi';
      case AssetType.equipment:
        return 'Ekipman';
    }
  }

  static AssetType fromString(String value) {
    return AssetType.values.firstWhere(
      (type) => type.name == value.toLowerCase(),
      orElse: () => AssetType.station,
    );
  }
}
