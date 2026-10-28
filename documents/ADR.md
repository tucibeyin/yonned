# Yonned Mimari Karar Kayıtları ve Geliştirme Yönergeleri (ADR & Workflow)
**Belge Türü:** Mimari Karar Kaydı ve Mühendislik El Kitabı (ADR & Engineering Guidelines)  
**Tarih:** 28 Ekim 2026  
**Durum:** Kesinleşmiş ve Bağlayıcı Standart  

---

## 1. GELİŞTİRME PRENSİPLERİ VE MİMARİ STANDARTLAR

Yonned projesinde üretilen her satır kod aşağıdaki endüstriyel standartlara ve yazılım felsefelerine harfiyen uymak zorundadır:

### 1.1. Temel Prensipler
* **Clean Architecture & Clean Code:** Bağımlılıklar içten dışa doğru akar (Domain/Entity $\rightarrow$ Use Cases/Services $\rightarrow$ Controllers/API). Kod okunabilir, fonksiyonlar tek bir sorumluluğa sahip (Single Responsibility) ve yan etkisiz (side-effect free) olmalıdır.
* **MVVM (Model-View-ViewModel):** Özellikle Flutter mobil ve istemci arayüzlerinde iş mantığı doğrudan UI bileşenlerinin içine gömülemez. Durum yönetimi (State) ve veri akışı ViewModel / Controller katmanları üzerinden yönetilir.
* **Sıfır Blokaj (Non-Blocking Real-World Operations):** Sahada beklenmedik durumlar (kaza, acil müdahale, sisteme henüz tanımlanmamış ilaç veya sarf malzemesi) hiçbir zaman personeli kilitletemez (JIT veri girişi desteklenir).
* **Sıfır Docker (Bare-Metal Performans):** Üretim ve staging sunucularında container soyutlamaları (Docker, K8s) kullanılmaz; işletim sistemiyle doğrudan konuşan yerel Linux servisleri (`systemd`) ve Debian native paketleri esastır.

---

## 2. GELİŞTİRME VE DOKÜMANTASYON DİL STANDARDI

* **Kodlama Dili: %100 İNGİLİZCE**
  * Sınıf adları (`Person`, `Asset`, `Vasif`, `LiveProcess`),
  * Fonksiyon ve metot adları (`resolve_permissions()`, `start_process()`),
  * Değişkenler, veri tipleri, enum'lar,
  * Veritabanı tablo ve sütun adları (`persons`, `asset_shares`, `can_create`, `can_read`, `can_update`, `can_delete`),
  * REST API endpoint yolları (`/api/v1/sessions/check-in`).
* **Yorum ve Açıklama Dili: %100 TÜRKÇE**
  * Kod içi satır yorumları (`# Varlık sahibiyse tüm izinler açıktır`),
  * Fonksiyon ve sınıf docstring'leri (`"""..."""`),
  * Git commit mesajları ve dokümantasyon belgeleri.

### 2.1. Mimari Karar Kaydı (ADR-001): Vasıf = Evrensel CRUD Sözleşmesi
* **Karar:** Yonned dünyasında varlık paylaşımı ve yetki delegasyonu, bilgisayar biliminin ve REST/HTTP standartlarının temeli olan **CRUD (Create, Read, Update, Delete)** modeline bağlanmıştır.
* **Neden:** 
  1. `POST` $\rightarrow$ `can_create` (Yeni süreç/sarf/alt mekan oluşturma)
  2. `GET` $\rightarrow$ `can_read` (Canlı durum, geçmiş, fotoğrafları okuma)
  3. `PUT/PATCH` $\rightarrow$ `can_update` (Süreç notu, aşama veya varlık güncelleme)
  4. `DELETE` $\rightarrow$ `can_delete` (Süreç veya varlık silme)
* **Kazanım:** HTTP metodları ile yetki doğrulaması 1:1 eşleşir; kodda karmaşık yetki matrisleri yerine tek satırlık `if not can_create` filtreleri çalışır.

### 2.2. Mimari Karar Kaydı (ADR-002): Tek Düğümde İzole Çift Ortam ve Standart İsimlendirme (`yonned_prod` & `yonned_staging`)
* **Karar:** Donanım ve maliyet verimliliğini maksimize etmek amacıyla Staging ve Production ortamları aynı ana hesaplama sunucusu (**`node102`**) üzerinde, ancak **%100 izole ağ, servis, veritabanı ve Redis süreçleriyle** konuşlandırılmıştır.
* **Standart İsimlendirme Sözleşmesi:** Sistemdeki tüm servisler, worker'lar, veritabanları ve yetkiler istisnasız `yonned_prod` ve `yonned_staging` önekleriyle adlandırılır:
  1. **Servisler:** `yonned_prod_api`, `yonned_prod_critical_worker`, `yonned_prod_worker`, `yonned_prod_redis` $\leftrightarrow$ `yonned_staging_api`, `yonned_staging_critical_worker`, `yonned_staging_worker`, `yonned_staging_redis`.
  2. **Veritabanları & Roller:** `yonned_prod_db` (`yonned_prod`) $\leftrightarrow$ `yonned_staging_db` (`yonned_staging`).
  3. **Ağ Portları:** Port `8000` (Prod API) $\leftrightarrow$ Port `8001` (Staging API); Port `6379` (Prod Redis) $\leftrightarrow$ Port `6380` (Staging Redis).
  4. **Medya Kasası (`node104`):** `yonned-prod-media` $\leftrightarrow$ `yonned-staging-media`.
* **Kazanım:** Ekstra sunucu ve altyapı maliyeti sıfırlanmış, donanım kaynakları maksimum verimle konsolide edilmiştir.

---

## 3. PROJE MONOREPO DİZİN YAPISI

Proje, backend, mobil, web ve belgeleri tek bir çatı altında toplayan monorepo mimarisindedir:

```
/var/www/yonned.com/ (Üretim Kök Dizini - yonned_prod)
/var/www/staging.yonned.com/ (Staging Kök Dizini - yonned_staging)
├── backend/                  # Python 3.13+ / FastAPI / SQLAlchemy Async Servisi
│   ├── alembic/              # Veritabanı şema göç sözleşmeleri (Migrations)
│   │   ├── versions/         # Versiyon dosyaları (0001_initial_schema.py, ...)
│   │   └── env.py            # Asyncpg göç motoru
│   ├── app/
│   │   ├── api/              # REST Controller katmanı
│   │   ├── core/             # config.py, database.py, security.py
│   │   ├── models/           # SQLAlchemy 2.0 ORM modelleri (Person, Asset, Vasif, ...)
│   │   ├── schemas/          # Pydantic v2 veri doğrulama ve DTO sözleşmeleri
│   │   ├── services/         # İş mantığı (PermissionService, ScannerService, ...)
│   │   ├── workers/          # Arkaplan işlemcileri (critical_worker.py, default_worker.py)
│   │   └── main.py           # FastAPI ASGI giriş noktası
│   ├── tests/                # Pytest test bataryası (unit, e2e, integration)
│   ├── pytest.ini            # Test konfigürasyonu (asyncio auto)
│   ├── requirements.txt      # Python bağımlılıkları
│   └── alembic.ini           # Alembic konfigürasyonu
├── frontend/                 # Web Arayüzleri (Patron Admin & Müşteri Canlı Takipçi)
├── mobile/                   # Flutter (Dart) Mobil Uygulama Projesi
└── documents/                # Tek Gerçek Kaynağı (SSOT) Dokümantasyon Kasası
    ├── architecture.md       # Teknik Mimari ve Sistem Şartnamesi (Teknik SSOT)
    ├── business.md           # İş Modeli, Süreçler ve Ürün Vizyonu (İş SSOT)
    ├── test.md               # Test, Kalite Güvencesi ve Doğrulama Şartnamesi (Test SSOT)
    ├── configurations.md     # OS, Sysctl, Ulimits, Cloudflare & Systemd Şartnamesi
    └── ADR.md                # Mimari Karar Kayıtları ve Geliştirme Yönergeleri (Bu Belge)
```

---

## 4. DAĞITIM VE YAŞAM DÖNGÜSÜ (DEPLOYMENT LIFECYCLE)

Yonned platformunda yerel ortamda test koşumu yapılmaz; tüm kod geliştirme döngüsü aşağıdaki 7 sıralı adımla icra edilir:

```
┌────────────────────────────────────────────────────────┐
│  1. LOCAL GELİŞTİRME (LOCAL DEV)                       │
│  • Clean Code & Clean Architecture standartlarında kod │
│  • %100 İngilizce kod / %100 Türkçe yorum kuralı       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼ git push origin main
┌────────────────────────────────────────────────────────┐
│  2. GITHUB REPO                                        │
│  • Merkezi kod deposu (github.com/tucibeyin/yonned)    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼ git pull (staging)
┌────────────────────────────────────────────────────────┐
│  3. STAGING GIT PULL (NODE102 - STAGING ORTAMI)        │
│  • cd /var/www/staging.yonned.com                      │
│  • git pull origin main                                │
│  • venv/bin/alembic upgrade head (Staging DB Göçü)     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼ pytest koşturulur
┌────────────────────────────────────────────────────────┐
│  4. TEST ONAY                                          │
│  • venv/bin/pytest tests/ -v (Linux Bare-Metal Testi)  │
│  • %100 YEŞİL ONAY ALINMADAN ASLA İLERLENEMEZ!         │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼ Testler geçince
┌────────────────────────────────────────────────────────┐
│  5. DÖKÜMANTASYON GÜNCELLE                             │
│  • Mimari, test veya konfigürasyon değişiklikleri      │
│    documents/ dizinindeki SSOT belgelerine işlenir     │
│  • Dokümantasyon güncellemeleri git'e commitlenir      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼ git pull (prod)
┌────────────────────────────────────────────────────────┐
│  6. PROD GIT PULL (NODE102 & NODE104)                  │
│  • node102: cd /var/www/yonned.com && git pull         │
│  • node104: cd /var/www/yonned.com && git pull         │
│  • node102: venv/bin/alembic upgrade head (Canlı DB)   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼ Servisler yeniden başlatılır
┌────────────────────────────────────────────────────────┐
│  7. CANLIYA ALMA İŞLEMLERİ (PRODUCTION RELEASE)        │
│  • sudo systemctl restart yonned_prod_api              │
│  • sudo systemctl restart yonned_prod_critical_worker  │
│  • sudo systemctl restart yonned_prod_worker           │
│  • curl -s http://127.0.0.1:8000/health (Doğrulama)    │
└────────────────────────────────────────────────────────┘
```

---

## 5. SUNUCU ÇALIŞMA KURALLARI VE DİZİN STANDARDI

1. **Sunucu Kök Dizinleri (`node102`):**  
   * Üretim Ortamı: `/var/www/yonned.com/` (`yonned_prod`)
   * Staging Ortamı: `/var/www/staging.yonned.com/` (`yonned_staging`)
2. **Kalıcı İzinler ve İzolasyon:**  
   * Kod dizinleri `tucibeyin:tucibeyin` kullanıcısına aittir (mod 755).
   * `.env` dosyaları asla git'e gönderilmez; sunucuda `chmod 600` ile korunur.
   * `yonned_staging` veritabanı kullanıcısının `yonned_prod_db`'ye `CONNECT` yetkisi PostgreSQL çekirdeğinde kesin olarak iptal edilmiştir.
3. **Rollback (Geri Alma) Güvencesi:**  
   Olası bir arıza durumunda `staging` üzerinde doğrulanmamış hiçbir kod canlıya alınamaz. Üretimde acil geri alma gerekirse:
   ```bash
   cd /var/www/yonned.com
   git reset --hard HEAD~1
   sudo systemctl restart yonned_prod_api yonned_prod_critical_worker yonned_prod_worker
   ```

