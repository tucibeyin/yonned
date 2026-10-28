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

---

## 3. PROJE MONOREPO DİZİN YAPISI

Proje, backend, mobil, web ve belgeleri tek bir çatı altında toplayan monorepo mimarisindedir:

```
/var/www/yonned.com/ (Sunucu Kök Dizini)
├── backend/                  # Python 3.12+ / FastAPI / SQLAlchemy Async Servisi
│   ├── alembic/              # Veritabanı şema göç sözleşmeleri (Migrations)
│   │   ├── versions/         # Versiyon dosyaları (0001_initial_schema.py, ...)
│   │   └── env.py            # Asyncpg göç motoru
│   ├── app/
│   │   ├── api/              # REST Controller katmanı
│   │   │   ├── deps.py       # Auth ve DB bağımlılık enjeksiyonları
│   │   │   └── v1/           # v1 API endpoint'leri (auth, assets, vasifs, sessions, ...)
│   │   ├── core/             # config.py, database.py, security.py
│   │   ├── models/           # SQLAlchemy 2.0 Declarative ORM modelleri (Person, Asset, Vasif, ...)
│   │   ├── schemas/          # Pydantic v2 veri doğrulama ve DTO sözleşmeleri
│   │   ├── services/         # İş mantığı (PermissionService, ScannerService, ...)
│   │   └── main.py           # FastAPI ASGI giriş noktası
│   ├── tests/                # Pytest test bataryası (unit, e2e, integration)
│   ├── requirements.txt      # Python bağımlılıkları
│   └── alembic.ini           # Alembic konfigürasyonu
├── frontend/                 # Web Arayüzleri (Patron Admin & Müşteri Canlı Takipçi)
│   ├── static/               # Saf CSS (Glassmorphism), Vanilla JS
│   └── templates/            # Jinja2 HTML5 SSR şablonları
├── mobile/                   # Flutter (Dart) Mobil Uygulama Projesi
│   └── lib/                  # MVVM mimarisinde vizör ve süreç ekranları
└── documents/                # Tek Gerçek Kaynağı (SSOT) Dokümantasyon Kasası
    ├── architecture.md       # Teknik Mimari ve Sistem Şartnamesi (Teknik SSOT)
    ├── business.md           # İş Modeli, Süreçler ve Ürün Vizyonu (İş SSOT)
    ├── test.md               # Test, Kalite Güvencesi ve Doğrulama Şartnamesi (Test SSOT)
    └── ADR.md                # Mimari Karar Kayıtları ve Geliştirme Yönergeleri (Bu Belge)
```

---

## 4. DAĞITIM VE YAŞAM DÖNGÜSÜ (DEPLOYMENT LIFECYCLE)

Sistemde yerel ortamda test koşumu yapılmaz; tüm doğrulama gerçek Linux ortamında icra edilir.

```
┌──────────────────────┐
│  1. LOCAL ORTAM      │  Kodlama yapılır (Clean Code & İngilizce kod)
│     (Geliştirici)    │  Değişiklikler incelenir
└──────────┬───────────┘
           │
           ▼  git push origin main
┌──────────────────────┐
│  2. GITHUB REPO      │  Merkezi kod deposu (https://github.com/tucibeyin/yonned.git)
└──────────┬───────────┘
           │
           ▼  git pull origin main
┌──────────────────────┐
│  3. NODE103          │  🧪 TAM BAĞIMSIZ STAGING VE TEST ORTAMI
│     (Staging Node)   │  • /var/www/yonned.com/ dizininde git pull
│     (185.205.194.236)│  • alembic upgrade head (Veritabanı göçü)
└──────────┬───────────┘  • pytest tests/ -v (Tüm test bataryası koşturulur)
           │
           ▼  TESTLER %100 YEŞİL ONAY ALDIKTAN SONRA:
┌────────────────────────────────────────────────────────┐
│  4. ÜRETİM ORTAMI (PRODUCTION DEPLOYMENT)              │
│                                                        │
│  [ NODE102 - Compute & DB ]     [ NODE104 - Storage ]  │
│  • cd /var/www/yonned.com/      • cd /var/www/yonned.com/
│  • git pull origin main         • git pull origin main │
│  • alembic upgrade head         • MinIO depolama kontrolü
│  • sudo systemctl restart yonned-api                   │
└────────────────────────────────────────────────────────┘
```

---

## 5. SUNUCU ÇALIŞMA KURALLARI VE DİZİN STANDARDI

1. **Sunucu Kök Dizini:**  
   Tüm sunucularda (`node102`, `node103`, `node104`) kod tabanı daima **/var/www/yonned.com/** dizini altında barındırılır.
2. **Kalıcı İzinler ve İzolasyon:**  
   * Kod dizini `yonned:yonned` (veya `www-data`) kullanıcısına aittir.
   * `.env` dosyası asla git'e gönderilmez; sunucuda `chmod 600` ile korunur.
3. **Rollback (Geri Alma) Güvencesi:**  
   Olası bir arıza durumunda `node103` üzerinde test edilmemiş hiçbir kod `node102` canlı sunucusuna alınamaz. Üretimde sorun çıkarsa tek bir komutla önceki commit'e dönülür:
   ```bash
   git reset --hard HEAD~1 && sudo systemctl restart yonned-api
   ```
