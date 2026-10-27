# Yonned Kurumsal Sistem, Ağ ve Yazılım Mimarisi Şartnamesi (V1.0)
**Tarih:** 28 Ekim 2026  
**Durum:** Kesinleşmiş Ana Mimari Belgesi (Master Architecture Document)  
**Standardizasyon:** *Enterprise Architecture Framework (EAF / C4 Model)*

---

## 1. Topoloji Mimarisi (Topology Architecture)

Sistemin fiziksel düğümleri, ağ katmanları, port güvenliği, şifreleme ve DDoS/IPS savunma hattı.

```
[ DIŞ DÜNYA: İstemciler ] (Mobil, Web Admin, Müşteri Tracker)
             │
             ▼ HTTPS (Port 443 / TLS 1.3)
┌────────────────────────────────────────────────────────────────────────┐
│ KATMAN 1: CLOUDFLARE EDGE (DNS, WAF, CDN & DDoS Kalkanı)              │
│ • Anycast DNS & Edge Caching                                           │
│ • DDoS Koruması (L3/L4/L7 saldırı emilimi)                             │
│ • Full (Strict) SSL Termination & Bot Fight Mode                       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼ Şifreli Trafik (Cloudflare Origin CA)
┌────────────────────────────────────────────────────────────────────────┐
│ KATMAN 2: NODE102 (Compute & Core Application Node)                    │
│ • IP: 185.205.194.173 | 3 vCPU | 9 GB RAM | 80 GB SSD | 10 Gbps Port   │
│ • OS: Debian GNU/Linux 13 (Trixie)                                     │
│                                                                        │
│ 🛡️ CROWDSEC SAVUNMA KATMANI:                                          │
│ ├── CrowdSec Security Engine (Log analizörü: SSH + Caddy logları)      │
│ ├── nftables Firewall Bouncer: Kötü niyetli IP'leri çekirdekte banlar  │
│ └── Community Threat Intelligence: Küresel kara listeleri önceden çeker│
│                                                                        │
│ 🌐 TERS VEKİL & SSL (Caddy Server):                                    │
│ ├── Port 80  ➔ 443 Yönlendirmesi                                       │
│ ├── Port 443 ➔ SSL Sonlandırma & Dahili Yönlendirme                    │
│ │   ├── /api/*   ➔ 127.0.0.1:8000 (FastAPI ASGI Uvicorn)               │
│ │   ├── /ws      ➔ 127.0.0.1:8000 (WebSocket Canlı Takip Akışı)        │
│ │   └── /admin, /t/* ➔ Statik / Jinja2 Web Arayüzleri                  │
│                                                                        │
│ ⚙️ DAHİLİ SERVİSLER (Yalnızca 127.0.0.1 - Dışarıya Kapalı):           │
│ ├── PostgreSQL 17 (Port 5432)                                          │
│ ├── Redis 7 (Port 6379)                                                │
│ └── Uvicorn / FastAPI Workers (Port 8000)                              │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼ Özel / İmzalı S3 İletişimi (Port 9000)
┌────────────────────────────────────────────────────────────────────────┐
│ KATMAN 3: NODE104 (Object Storage & Media Vault Node)                  │
│ • IP: 82.39.86.94 | 2 vCPU | 3 GB RAM | 1 TB HDD (/mnt/data) | 1 Gbps  │
│ • OS: Debian GNU/Linux 13 (Trixie)                                     │
│                                                                        │
│ 🛡️ CROWDSEC (SSH Koruması & Port Kısıtlaması)                          │
│                                                                        │
│ 📦 MinIO S3 Object Storage Service (Port 9000):                        │
│ ├── /mnt/data/yonned-media/   ➔ Fotoğraflar, tahliller, evraklar       │
│ └── /mnt/data/yonned-backups/ ➔ node102 Veritabanı Yedek Arşivi        │
└────────────────────────────────────────────────────────────────────────┘
```

### Port Güvenlik Matrisi:
| Sunucu | Port | Protokol | Servis | Dış Dünyaya Açık mı? | Koruma Yöntemi |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **`node102`** | 22 | TCP | SSH | Evet (Kısıtlı) | Sadece SSH Key (Parola Kapalı) + CrowdSec |
| **`node102`** | 80 | TCP | HTTP | Evet | Caddy (Otomatik HTTPS 443 Yönlendirmesi) |
| **`node102`** | 443 | TCP | HTTPS | Evet | Cloudflare WAF + Caddy TLS 1.3 |
| **`node102`** | 8000 | TCP | FastAPI | **HAYIR** | Sadece `127.0.0.1` dinler |
| **`node102`** | 5432 | TCP | PostgreSQL | **HAYIR** | Sadece `127.0.0.1` dinler |
| **`node102`** | 6379 | TCP | Redis | **HAYIR** | Sadece `127.0.0.1` dinler |
| **`node104`** | 22 | TCP | SSH | Evet (Kısıtlı) | Sadece SSH Key + CrowdSec |
| **`node104`** | 9000 | TCP | MinIO S3 | Kısıtlı | Yalnızca `node102` IP'sinden erişim (nftables) |

---

## 2. Yapılandırma Mimarisi (Configuration Architecture)

Sistemin ortam değişkenleri, sırlar (secrets), bağımlılık yönetimi ve 12-Faktör uyumu.

### 2.1. Prensip: 12-Factor App & Strict Typing
* Konfigürasyonlar kodun içinde asla yer almaz; tamamen işletim sistemi ortam değişkenleri (`environment variables`) ve `.env` üzerinden beslenir.
* Python tarafında **`pydantic-settings`** kullanılır. Uygulama ayağa kalkarken eksik veya tipi yanlış bir ayar varsa sistem anında hata vererek başlamayı reddeder (Fail-Fast).

### 2.2. Konfigürasyon Katmanları
```
/var/www/yonned/
├── .env.production          # Yalnızca root/yonned kullanıcısına okunur (chmod 600)
│   ├── DATABASE_URL         # postgresql+asyncpg://yonned:pass@127.0.0.1:5432/yonned_db
│   ├── REDIS_URL            # redis://127.0.0.1:6379/0
│   ├── SECRET_KEY           # JWT ve Token imzalama için 64-karakter hex
│   ├── S3_ENDPOINT_URL      # http://82.39.86.94:9000 (node104)
│   ├── S3_ACCESS_KEY        # MinIO erişim anahtarı
│   ├── S3_SECRET_KEY        # MinIO gizli anahtarı
│   └── S3_BUCKET_NAME       # yonned-media
```

### 2.3. Sırların Güvenliği (Secret Management)
* `.env` dosyaları `.gitignore` ile korunur, asla GitHub'a gitmez.
* Sunucuya ortam değişkenleri ilk kurulumda güvenli SCP ile aktarılır.
* Servisler `systemd` üzerinden `EnvironmentFile=/var/www/yonned/.env.production` direktifiyle izole çalışır.

---

## 3. İletişim Mimarisi (Communication Architecture)

Birimlerin nerede, hangi protokollerle ve nasıl bağlandığı.

```
┌─────────────────┬───────────────────┬─────────────────────┬──────────────────────────┐
│ Kaynak Birim    │ Hedef Birim       │ Fiziksel / Sanal    │ Protokol / Erişim Kanalı │
├─────────────────┼───────────────────┼─────────────────────┼──────────────────────────┤
│ Mobil (Flutter) │ Caddy Proxy       │ İnternet ➔ node102  │ HTTPS / TLS 1.3 (JSON)   │
│ Web Admin (JS)  │ Caddy Proxy       │ İnternet ➔ node102  │ HTTPS / TLS 1.3 (JSON)   │
│ Web Tracker (JS)│ Caddy Proxy       │ İnternet ➔ node102  │ WSS (WebSocket Secure)   │
│ Caddy Proxy     │ FastAPI Backend   │ node102 Dahili Ağ   │ HTTP/1.1 (127.0.0.1:8000)│
│ FastAPI Backend │ PostgreSQL 17     │ node102 Dahili Ağ   │ TCP (asyncpg / 5432)     │
│ FastAPI Backend │ Redis 7           │ node102 Dahili Ağ   │ TCP (redis-py / 6379)    │
│ FastAPI Backend │ MinIO (node104)   │ node102 ➔ node104   │ S3 API / HTTP (Port 9000)│
│ Admin / DevOps  │ node102 / node104 │ İnternet (SSH)      │ SSH (Ed25519 Key / 22)   │
└─────────────────┴───────────────────┴─────────────────────┴──────────────────────────┘
```

---

## 4. Entegrasyon Mimarisi (Integration Architecture)

Birimlerin birbiriyle konuşma ve veri alışveriş mekanizmaları.

### 4.1. Senkron API Entegrasyonu (REST & OpenAPI)
* **Format:** %100 JSON (UTF-8).
* **Standart:** RESTful prensipleri ve OpenAPI v3 (Swagger).
* **Sözleşme:** Her istek Pydantic şemaları ile çift yönlü doğrulanır (hem gelen veri hem dönen cevap tiplidir).
* **Hata Yönetimi:** Standart RFC 7807 problem detay formatı:
  `{"status": 404, "code": "ASSET_NOT_FOUND", "message": "Kafes #1 bulunamadı"}`

### 4.2. Asenkron & Gerçek Zamanlı Entegrasyon (WebSocket + Redis Pub/Sub)
* Müşteri takip sayfası açıldığında WebSocket bağlantısı kurar (`/ws/tracker/{token}`).
* Hekim veya operatör mobilde işlem kaydettiğinde (`POST /api/processes/event`):
  1. Veri PostgreSQL'e yazılır.
  2. FastAPI, Redis'e bir yayın fırlatır: `redis.publish(f"session:{session_id}", event_json)`.
  3. O oturumu dinleyen WebSocket istemcilerine mesaj anında iletilir.
  4. Sayfa yenilenmeden müşterinin ekranında anlık güncelleme belirir.

### 4.3. Dosya ve Medya Alışverişi (S3 Presigned URLs)
* Mobil çalışan fotoğraf çektiğinde; büyük boyutlu resim dosyası **FastAPI sunucusunu yormaz**.
* **Akış:**
  1. Mobil uygulama API'den yükleme izni ister: `POST /api/media/upload-url`
  2. FastAPI, `node104` MinIO sunucusu için 15 dakika geçerli **İmzalı Yükleme URL'i (Presigned PUT URL)** üretir.
  3. Mobil uygulama fotoğrafı doğrudan `node104`e yükler (`PUT http://82.39.86.94:9000/...`).
  4. Yükleme tamamlanınca fotoğrafın S3 anahtarı sürece iliştirilir.

---

## 5. Teknoloji Mimarisi (Technology Architecture)

Sistemin üzerine oturduğu ortamın donanım, işletim sistemi ve teknolojik marka/model detayları:

| Katman | Teknoloji / Model | Sürüm | Konum & Açıklama |
| :--- | :--- | :--- | :--- |
| **Donanım: Compute** | DeluxHost VPS (AMD/Intel) | 3 vCPU / 9 GB RAM | `node102` (Amsterdam) |
| **Donanım: Storage** | DeluxHost Storage VPS | 2 vCPU / 3 GB / 1 TB | `node104` (Amsterdam) |
| **İşletim Sistemi** | Debian GNU/Linux | 13 (Trixie) - Kernel 6.12 | Bare-metal yerel kurulum (Docker'sız) |
| **Web / Reverse Proxy**| Caddy Server | 2.8+ | Go tabanlı yerel HTTP/3 ters vekil |
| **Güvenlik Savunması**| CrowdSec + nftables bouncer | Güncel FOSS | Yerel log analizörü ve IP banlayıcı |
| **Backend Runtime** | Python (CPython) | 3.12+ LTS | Asenkron ASGI motoru |
| **Backend Framework** | FastAPI | 0.115+ | Yüksek hızlı asenkron web çatısı |
| **ASGI Sunucusu** | Uvicorn (standard uvloop) | 0.32+ | C tabanlı ultra hızlı event-loop |
| **Veritabanı Motoru** | PostgreSQL | 17.x | ACID, JSONB, Recursive CTE destekli |
| **Veritabanı Sürücüsü**| asyncpg + SQLAlchemy Async | 2.0+ | En hızlı asenkron Python DB sürücüsü |
| **Önbellek & Soket** | Redis | 7.x | Bellek içi veri yapısı deposu |
| **Medya Depolama** | MinIO Server | Single Binary | 1 TB HDD üzerinde S3 uyumlu nesne deposu |
| **Mobil Çatı** | Flutter (Dart) | 3.x+ | Cross-platform native derleme motoru |
| **Mobil Kamera/Tarayıcı**| mobile_scanner | Güncel | Donanım hızlandırmalı kamera barkod vizörü |
| **Web UI** | HTML5 + Vanilla CSS + Vanilla JS| Saf Web | Modern cam efekti (glassmorphism), sıfır build |

---

## 6. Bağımlılık Mimarisi (Dependency Architecture)

Her birimin birbiriyle ve dış dünya kütüphanelerine olan bağımlılıklarının kontrolü:

### 6.1. Dış Servis Bağımlılıkları (External Dependencies)
* **Cloudflare (Ücretsiz Tier):** Yalnızca DNS ve SSL trafiği için kullanılır. Cloudflare çökse bile Caddy doğrudan Let's Encrypt ile tek başına çalışabilir.
* **Let's Encrypt:** Otomatik SSL sertifikası üretimi için kullanılır.
* **Üçüncü Taraf Bulut Bağımlılığı: SIFIR!** (AWS, Google Cloud, Firebase vb. ücretli bağımlılıklar yoktur; her şey `node102` ve `node104`tedir).

### 6.2. Python Kütüphane Bağımlılıkları (`requirements.txt`)
Yalnızca denenmiş, hafif ve kararlı paketler:
* `fastapi`, `uvicorn[standard]` $\rightarrow$ Web motoru
* `sqlalchemy[asyncio]`, `asyncpg`, `alembic` $\rightarrow$ DB & migration
* `pydantic`, `pydantic-settings` $\rightarrow$ Veri doğrulama
* `redis` $\rightarrow$ Asenkron Redis istemcisi
* `jinja2`, `python-multipart` $\rightarrow$ HTML şablonları ve dosya formları
* `boto3` veya `aioboto3` $\rightarrow$ MinIO S3 dosya iletişimi
* `pyjwt`, `passlib[bcrypt]` $\rightarrow$ Kimlik doğrulama & şifreleme

### 6.3. Flutter Paket Bağımlılıkları (`pubspec.yaml`)
* `mobile_scanner` $\rightarrow$ Kamera ve barkod okuma
* `http` veya `dio` $\rightarrow$ API REST istemcisi
* `web_socket_channel` $\rightarrow$ Canlı soket istemcisi
* `flutter_riverpod` veya `provider` $\rightarrow$ Reaktif durum yönetimi (State management)
* `shared_preferences` $\rightarrow$ Yerel oturum token saklama

---

## 7. Yazılım Mimarisi (Software Architecture)

### 7.1. Backend Architecture (Python FastAPI)

FastAPI mimarisi **Katmanlı Mimari (Layered Architecture)** prensibine göre inşa edilir:

```
backend/
├── app/
│   ├── api/             # HTTP & WebSocket Uç Noktaları (Controller Katmanı)
│   │   ├── v1/
│   │   │   ├── auth.py          # Oturum açma & profil geçişi (Düzenleyici/Sorgulayıcı)
│   │   │   ├── assets.py        # Varlık ağacı (şube, kat, kafes, hasta/cihaz)
│   │   │   ├── processes.py     # Canlı süreç başlatma, bitirme, olay ekleme
│   │   │   ├── scanner.py       # Evrensel barkod/QR çözümleme servisi
│   │   │   ├── tracker.py       # Müşteri canlı takip API & WebSocket
│   │   │   └── media.py         # S3 presigned URL üretimi
│   │   └── router.py
│   │
│   ├── core/            # Çekirdek Sistem Konfigürasyonu
│   │   ├── config.py            # Pydantic Settings (.env yükleme)
│   │   ├── database.py          # SQLAlchemy async engine & sessionmaker
│   │   ├── redis.py             # Redis async connection pool
│   │   └── security.py          # JWT, bcrypt şifreleme, yetki doğrulama
│   │
│   ├── models/          # SQLAlchemy Veritabanı Modelleri (Kutsal Üçlü)
│   │   ├── person.py            # Persons, PersonRoles
│   │   ├── asset.py             # Assets (Recursive Tree)
│   │   ├── process.py           # ProcessDefinitions, AssetSessions, LiveProcesses
│   │   └── consumable.py        # ProcessConsumables
│   │
│   ├── schemas/         # Pydantic Doğrulama Şemaları (DTO'lar)
│   │   ├── person_schema.py
│   │   ├── asset_schema.py
│   │   ├── process_schema.py
│   │   └── scanner_schema.py
│   │
│   ├── services/        # İş Mantığı Katmanı (Business Logic)
│   │   ├── asset_service.py     # Varlık dolaşımı ve doluluk kontrolleri
│   │   ├── process_engine.py    # Süreç özyineleme, başla/bitir hesapları
│   │   ├── scanner_resolver.py  # Barkod ön eki (loc_, ast_, ses_) analizörü
│   │   └── notification.py      # Redis Pub/Sub bildirim tetikleyicisi
│   │
│   └── templates/       # HTML Şablonları (Jinja2)
│       ├── admin/               # Web Admin Sayfaları
│       └── tracker/             # Müşteri Canlı Takip Sayfası
│
├── alembic/             # Veritabanı Migration Dosyaları
├── main.py              # Uygulama Giriş Noktası & Middleware
└── requirements.txt
```

#### Cross-Cutting Concerns (Enine Kesen Kaygılar):
1. **Kimlik ve Yetkilendirme (Auth & Scoped RBAC):**  
   JWT (JSON Web Token) tabanlıdır. İstek başlığında gelen token çözülür, kullanıcının o şubedeki rolü (`superuser`, `admin`, `operator` veya varlık sahibi `client`) middleware düzeyinde denetlenir.
2. **Kapsamlı Loglama (Structured Logging):**  
   Her istek için bir `request_id` üretilir. Gelen istek, yanıt süresi ve hata logları standart JSON formatında yazılır (CrowdSec bu logları kolayca ayrıştırır).
3. **CORS ve Rate Limiting:**  
   FastAPI CORS middleware'i sadece tanımlı alan adlarına izin verir. Kötü niyetli istekler için IP bazlı istek sınırlandırması uygulanır.
4. **Veritabanı Oturum Yönetimi (Session Lifecycle):**  
   `async with get_db() as db:` kalıbı ile her istek için ayrı bir asenkron veritabanı oturumu açılır, işlem bitince otomatik commit/rollback edilir ve havuza iade edilir.

---

### 7.2. Mobil Architecture (Flutter)

Saha personeli için tasarlanan Flutter uygulaması **Feature-First & Repository Pattern** ile kurulur:

```
mobile/
├── lib/
│   ├── core/                    # Ağ istemcisi, tema, yerel depolama
│   │   ├── network/api_client.dart
│   │   ├── theme/app_theme.dart # Yüksek kontrastlı, sahaya uygun arayüz
│   │   └── constants/
│   │
│   ├── features/
│   │   ├── scanner/             # Evrensel Kamera Vizörü
│   │   │   ├── scanner_screen.dart
│   │   │   └── scanner_controller.dart
│   │   │
│   │   ├── process/             # Süreç Yönetimi (Başlat / Bitir / Olay)
│   │   │   ├── process_card_widget.dart
│   │   │   ├── quick_actions_widget.dart
│   │   │   └── process_controller.dart
│   │   │
│   │   ├── station/             # İstasyon & Kafes Durumu
│   │   │   ├── station_detail_screen.dart
│   │   │   └── asset_picker_modal.dart
│   │   │
│   │   └── auth/                # Giriş ve Şube Seçimi
│   │
│   └── main.dart
```

#### Mobil Tarama ve Çalışma Prensibi:
* **Tek Dokunuşla Vizör:** Uygulama açılır açılmaz veya ana sayfadaki dev kamera butonuna basılınca kamera açılır.
* **Otomatik Ayrıştırma:**
  * Okunan değer `loc_` ile başlıyorsa $\rightarrow$ `StationDetailScreen` açılır.
  * Okunan değer `ast_` ile başlıyorsa $\rightarrow$ `AssetActiveProcessScreen` açılır.
  * Okunan değer standart EAN barkod ise $\rightarrow$ Açık olan sürecin sarfiyat modalı tetiklenir.

---

### 7.3. Web UI Architecture (Saf HTML / Vanilla CSS / Modern JS)

Web tarafında ağır JavaScript kütüphaneleri (React/Vue/Angular) yerine **hafif, modüler ve sıfır build** prensibi uygulanır:

```
frontend/ (veya backend/templates & backend/static)
├── static/
│   ├── css/
│   │   ├── base.css             # CSS Sıfırlama ve Değişkenler (:root renkler)
│   │   ├── components.css       # Cam efektli kartlar, butonlar, modal'lar
│   │   └── tracker.css          # Canlı zaman tüneli ve mobil kart stilleri
│   ├── js/
│   │   ├── tracker_socket.js    # WebSocket canlı dinleyici ve DOM güncelleyici
│   │   └── admin_dashboard.js   # Bayi filtreleme ve dinamik arama
│   └── icons/
│
└── templates/
    ├── base.html                # Ana layout (Navbar, bildirim alanı)
    ├── admin/
    │   ├── dashboard.html       # Şube kuşbakışı haritası & doluluk
    │   ├── definitions.html     # Süreç legoları oluşturma sihirbazı
    │   └── assets.html          # Varlık ağacı gezgini
    └── tracker/
        └── live.html            # Müşterinin açtığı canlı zaman tüneli
```

#### Tasarım Sistemi (Aesthetics):
* **Lüks Koyu Tema (Dark Mode):** Derin lacivert/antrasit zeminler (`#0B0F19`), neon turkuaz ve amber aksan renkleri.
* **Glassmorphism:** Hafif yarı saydam zeminler (`backdrop-filter: blur(12px)`), ince parlak bordürler.
* **Mikro-Animasyonlar:** Durum değişimlerinde yeşil yanan nabız (pulse) animasyonları.
* **Mobil Uyumluluk:** Her ekran %100 responsive flex/grid ile masaüstü, tablet ve mobil tarayıcılarda kusursuz akar.
