# Yonned Test, Kalite Güvencesi ve Doğrulama Şartnamesi (V1.0 - Master Test Spec)
**Belge Türü:** Tek Gerçek Kaynağı (Single Source of Truth - Testing & QA SSOT)  
**Tarih:** 28 Ekim 2026  
**Durum:** Kesinleşmiş ve Onaylanmış Ana Test Belgesi  
**Felsefe:** *Sıfır-Blokaj Doğrulaması, 4 Fiil İzin Matrisi, Varlık Dolaşımı Simetrisi, Bare-Metal Dayanıklılık*

---

## 1. TEST STRATEJİSİ VE KALİTE PİRAMİDİ

Yonned platformunda kalite kontrolü; geleneksel basit "happy-path" senaryolarının çok ötesindedir. Sahada kirli, ıslak ellerle, acil müdahalelerin ortasında çalışan operatörlerin hiçbir zaman bloklanmamasını ve kullanıcı izinlerinin 4 fiil (Görüntüle, Değiştir, Ekle, Sil) çerçevesinde kusursuz çalışmasını garanti altına alır.

```
                            /\
                           /  \
                          / E2E \       --> Gerçek Saha & Kaza Simülasyonları
                         / Saha  \          (Acil Müdahale, Roaming, İkili Kimlik)
                        /─────────\
                       / Entegrasyon\   --> API + WebSocket + Redis + MinIO
                      /  & Güvenlik  \      (4 Fiil Yetki, CrowdSec, Token Takip)
                     /────────────────\
                    /    Birim (Unit)   \ --> Özyinelemeli Ağaç, Süreç Süreleri,
                   /   & Model Testleri  \    4 Fiil Matris Hesaplamaları
                  /───────────────────────\
```

---

## 2. BİRİM VE MODEL TESTLERİ (UNIT TESTS)

### 2.1. Özyinelemeli Aset Ağacı (Recursive Asset Tree Integrity)
* **Amaç:** Hiyerarşik mekan ve nesne yapısının (`parent_id`) veri tabanında sonsuz döngüye girmesini önlemek ve doğru konum yolunu (Breadcrumb: *Kadıköy ➔ 2. Kat ➔ Ameliyathane ➔ Masa #1*) milisaniyeler içinde türetmek.
* **Test Senaryoları:**
  1. `test_circular_parent_prevention`: Bir asetin kendi çocuğuna veya torununa bağlanması (`A -> B -> C -> A`) engellenmeli, sistem `CycleDetectedError` fırlatmalıdır.
  2. `test_deep_tree_breadcrumb`: 10 seviye derinliğindeki bir nesnenin (Örn: Cihaz) tam yol haritası tek bir Recursive CTE sorgusu ile 5ms altında dönmelidir.
  3. `test_asset_roaming_parent_switch`: Bir hasta (Kedi Tarçın) Kadıköy Şubesi'nden Beşiktaş Şubesi Yoğun Bakım Kafesi'ne taşındığında, `current_location_asset_id` atomik olarak güncellenmeli ve geçmiş ilişkileri bozulmamalıdır.

### 2.2. Süreç Zamanı ve Anlık Olay Hesabı (Temporal vs Instant Event)
* **Amaç:** Süreç ve Olay ayrımının sıfır süre mantığıyla doğrulanması.
* **Test Senaryoları:**
  1. `test_instant_event_zero_duration`: `is_instant = True` olan bir olay (Örn: Aşı Yapıldı) kaydedildiğinde `started_at == ended_at` ve `duration_seconds == 0` olmalıdır.
  2. `test_durational_process_calculation`: `started_at` 10:00 ve `ended_at` 10:45 olan bir operasyonun `duration_seconds` değeri tam 2700 saniye (45 dk) olarak hesaplanmalıdır.
  3. `test_parallel_subprocesses`: Bir ana süreç (`parent_id`) altında eşzamanlı iki alt süreç (Örn: Tıraş ve Tırnak Kesimi) birbirini kilitlemeden aynı anda `running` statüsünde kalabilmelidir.

### 2.3. Evrensel CRUD İzin Matrisi Motoru (CRUD Permission Engine)
* **Amaç:** `asset_shares` tablosundaki 4 bağımsız CRUD kutucuğunun yetki çözümlemesini doğrulamak.
* **Test Senaryoları:**

| Rol / Kişi | can_create | can_read | can_update | can_delete | Beklenen Davranış |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Tam Sahip (Owner)** | ✅ | ✅ | ✅ | ✅ | Her işlemi yapar (C-R-U-D), varlığı başkalarıyla paylaşabilir. |
| **Eş / Tam Ortak** | ✅ | ✅ | ✅ | ✅ | Tüm süreçleri yönetir, silebilir, günceller. |
| **Saha Hekimi / Usta** | ✅ | ✅ | ✅ | ❌ | Yeni süreç açar, notları günceller; fakat kaydı silemez. |
| **Stajyer / Çırak** | ✅ | ✅ | ❌ | ❌ | Süreçleri görür, yeni not/olay ekler; geçmişi değiştiremez/silemez. |
| **Müşteri / Takipçi** | ❌ | ✅ | ❌ | ❌ | Sadece kendi varlığının canlı durumunu izler, müdahale edemez. |
| **Yetkisiz Yabancı** | ❌ | ❌ | ❌ | ❌ | `403 Forbidden` veya `404 Not Found` alır. |

---

## 3. API VE ENTEGRASYON TESTLERİ (INTEGRATION TESTS)

### 3.1. Kimlik Doğrulama ve Çift Yönlü Vatandaş Oturumu (Auth & Dual Identity)
* **`POST /api/v1/auth/otp/request` & `verify`:**
  * Telefon numarası ile OTP doğrulanır.
  * Dönen JWT içinde `person_id` yer alır.
* **`GET /api/v1/persons/me/workspaces`:**
  * Bireyin hem sahibi olduğu işletme asetleri (`Pati Veteriner Kliniği`, `Ali Usta Detailing`),
  * Hem de müşteri olarak sahip olduğu özel varlıkları (`Kedi Tarçın`, `BMW 3.20`) tek bir JSON yanıtında döner.
  * Tek dokunuşla bağlam (context) değiştiğinde yeni token üretmeye gerek kalmadan yetkiler filtrelenir.

### 3.2. Evrensel Kamera Vizörü Çözümleyici (Universal Scanner Resolver)
Mobil kameradan gelen tek bir ham metin / QR string'i backend tarafından anında tipine ayrıştırılmalıdır:
* **`POST /api/v1/scanner/resolve`**
  1. Girdi `loc_kdk_zmn_kf1` $\rightarrow$ `{type: "location", entity: "Kafes #1", branch: "Kadıköy", status: "occupied"}`
  2. Girdi `ast_pet_tarcin_01` $\rightarrow$ `{type: "subject", entity: "Kedi Tarçın", active_session: "ses_987..."}`
  3. Girdi `8699508000123` (İlaç Barkodu) $\rightarrow$ `{type: "consumable", entity: "Synulox 50ml", unit: "ml"}`
  4. Girdi `tanımsız_kod_999` $\rightarrow$ `{type: "unknown", prompt_create: true}` *(Sıfır Blokaj!)*

### 3.3. Canlı WebSocket ve Redis Pub/Sub Akışı (Real-Time Tracker)
* **`WS /ws/tracker/{token}`:**
  1. Müşteri tarayıcısı WebSocket'e bağlanır.
  2. Saha operatörü mobilden ameliyat aşamasını tamamlar: `POST /api/v1/processes/{id}/complete`
  3. FastAPI, Redis kanalına olayı yayınlar (`redis.publish("tracker:{token}", payload)`).
  4. Müşterinin açık WebSocket bağlantısına veri iletilir.
  5. **Metrik:** Veritabanına yazılma anı ile tarayıcıda WebSocket paketinin alınması arasındaki süre **< 50 milisaniye** olmalıdır.

### 3.4. Medya Yükleme ve S3 Presigned URL Akışı (MinIO Integration)
* **`POST /api/v1/media/upload-url`:**
  1. Mobil uygulama `content_type: image/jpeg` ile yükleme URL'i ister.
  2. Backend `node104` MinIO sunucusu için 15 dakika geçerli imzalı PUT URL döner.
  3. Test betiği mock bir fotoğrafı doğrudan `node104:9000` adresine yükler (HTTP 200).
  4. Yüklenen fotoğrafın kalıcı URL'i `live_processes.photos` JSON dizisine başarıyla eklenir.

---

## 4. UÇTAN UCA SAHA SİMÜLASYONLARI (CRITICAL REAL-WORLD E2E)

### Senaryo A: Çok Katlı Bayide Varlık Dolaşımı (Multi-Floor Roaming)
1. Kedi Tarçın kliniğe gelir. Karşılamadaki görevli Tarçın'ın boyunluk QR'ını okutur $\rightarrow$ `asset_sessions` açılır, statü `checked_in`.
2. Asistan, Zemin Kat "Kafes 1" QR'ını okutur $\rightarrow$ Tarçın Kafes 1'e atanır.
3. 2 saat sonra ameliyat vakti gelir: Cerrahi teknikeri Tarçın'ı alır, 1. Katta Ameliyathane "Masa 2" QR'ını okutur $\rightarrow$ Tarçın'ın konumu otomatik "Masa 2" olur.
4. Müşteri takip linkini açtığında: "Tarçın şu an Ameliyathanede" ibaresini canlı görür.
5. Ameliyat biter, Tarçın 2. Kat "Uyanma Odası Kafes 4"e alınır $\rightarrow$ Konum anında güncellenir.
6. **Beklenen Sonuç:** Sıfır veri kopyalama, sıfır mükerrer hasta kaydı, tam izlenebilirlik.

### Senaryo B: Sıfır-Blokaj Kaza & Acil Müdahale (Emergency Interruption)
1. Operatör kuaförde köpeği tıraş etmektedir (`live_processes` statüsü: `running`).
2. Tıraş esnasında beklenmedik ani bir hareketle kulakta küçük bir kesik oluşur.
3. Operatör tıraşı iptal **ETMEZ**; ekrandaki `[+ Acil Müdahale]` butonuna dokunur.
4. Tıraş süreci arka planda beklemeye alınır (`paused`); `Acil Dikiş / Pansuman` süreci başlatılır.
5. Operatör ecza dolabından aldığı spreyi okutur:
   * **Durum 1 (Tanımlı İlaç):** Sistem ilacı tanır, 1 doz düşer.
   * **Durum 2 (Sisteme Henüz Girilmemiş Yeni İlaç):** Sistem *"Bu barkod kayıtlı değil"* diyerek personeli durdurmaz! Ekranda tek satırlık kutu açılır: *"Yeni İlaç Adı: [ Terramycin Sprey ]"*. Operatör adı yazar, onaylar ve geçer.
6. Dikiş atılır, fotoğraf çekilir, acil müdahale tamamlanır (`completed`).
7. Tıraş süreci kaldığı yerden devam ettirilir (`running`).
8. **Beklenen Sonuç:** Operatör asla hata penceresine takılmaz; hastanın hayatı ve operasyon bürokrasiye kurban gitmez.

### Senaryo C: CRUD İzin Matrisiyle Güvenli Paylaşım
1. **İşletme İçi Delegasyon:**
   * Patron (Dr. Hasan) yeni stajyer Özge'ye kliniği paylaşır: `can_read=True, can_create=True, can_update=False, can_delete=False`.
   * Stajyer Özge yeni muayene kaydı açabilir (`can_create=True`), hasta durumunu görebilir (`can_read=True`).
   * Stajyer Özge geçmiş 10 yıllık tahlil sonucunu değiştirmeye çalıştığında `403 Update Forbidden` alır.
   * Stajyer Özge bir ameliyat kaydını silmeye çalıştığında `403 Delete Forbidden` alır.
2. **Müşteri İçi Delegasyon:**
   * Araç sahibi Mehmet Bey arabasını servise bırakır. Takip ekranını eşine paylaşır (`can_read=True`). Eşi arabanın takibini canlı izler ama tamirciye yanlışlıkla servis iptali veremez.

### Senaryo D: Mülkiyetin Değişmezliği ve Zilyetlik İzolasyonu (Ownership Invariance)
1. **Giriş:** Ali Bey köpeği Karabaş'ı (`owner_person_id = Ali`) kliniğe bırakır.
2. **Oturum Açılışı:** Hekim Karabaş'ı teslim alır (`asset_sessions` açılır, `checked_in`).
3. **Doğrulama 1 (Mülkiyet Korunumu):** Oturum süresince `karabaş.owner_person_id` değerinin kesinlikle Ali Bey kaldığı, kliniğin veya hekimin mülkiyeti üzerine ALAMADIĞI doğrulanır.
4. **Doğrulama 2 (Varlık İradesizliği):** Bir varlığın (Karabaş veya Kafes 1) sisteme login olamayacağı veya başka birine paylaşım (Vasıf) devredemeyeceği (`AssertionError / 400 Bad Request`) doğrulanır.
5. **Çıkış:** Hizmet biter (`checked_out`); varlık sahibine iade edilir.

---

## 5. BARE-METAL GÜVENLİK VE DAYANIKLILIK TESTLERİ

### 5.1. CrowdSec & nftables L3/L4 Çekirdek Ban Testi
* **Amaç:** Sunuculara yönelik brute-force (kaba kuvvet) saldırıların işletim sistemi çekirdeğinde (kernel space) engellendiğini doğrulamak.
* **Test Adımları:**
  1. Test istemcisinden `node102` API portuna 1 dakika içinde 60 adet yetkisiz istek (`401 Unauthorized`) gönderilir.
  2. CrowdSec log analizörü (`crowdsec.service`) anormalliği tespit eder.
  3. `crowdsec-firewall-bouncer` nftables kurallarına saldırgan IP'yi ekler.
  4. Saldırgan IP'den gelen 61. istek Nginx'e dahi ulaşamadan TCP seviyesinde `DROP` edilir (Connection timed out / dropped).

### 5.2. Eşzamanlı Yük ve Performans Testi (Load & Concurrency Benchmark)
* **Hedef Değerler:**
  * **API Yanıt Süresi:** p95 < 25ms, p99 < 50ms.
  * **Eşzamanlı WebSocket Bağlantısı:** Tek `node102` sunucusunda minimum 5.000 aktif müşteri canlı takip soketi (RAM tüketimi < 1.5 GB).
  * **Veritabanı Sorguları:** 100.000 aset ve 1.000.000 geçmiş süreç içeren veritabanında recursive konum ve izin sorguları < 8ms.

---

## 6. TESTLERİN ÇALIŞTIRILMASI VE DOĞRULAMA (NODE103 STAGING RUNNER)

Yerel geliştirme ortamında (localhost) test koşumu **yapılmaz**. Tüm birim, entegrasyon ve yük testleri doğrudan **`node103` (Standalone Staging Node: `185.205.194.236`)** üzerinde, gerçek Debian 13 işletim sistemi, yerel PostgreSQL 17 ve Redis 7 servisleri ile koşturulur.

### node103 Üzerinde Test Koşum Adımları:
```bash
# 1. SSH ile Staging Düğümüne Bağlan
ssh node103

# 2. En son kodu çek ve sanal ortamı aktif et
cd /var/www/yonned.com
git pull origin main
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# 3. Staging Veritabanı Göçlerini (Alembic) Uygula
alembic upgrade head

# 4. Tüm Test Bataryasını Çalıştır
pytest tests/ -v --asyncio-mode=auto

# 5. E2E Sıfır Blokaj ve Kaza Senaryolarını Çalıştır
pytest tests/e2e/test_zero_blockage_accident.py -v

# 6. Test Kapsama (Coverage) Raporu Al
pytest --cov=app --cov-report=term-missing tests/
```

Her canlıya çıkış öncesinde bu test bataryası `node103` üzerinde %100 yeşil olmak zorundadır.
