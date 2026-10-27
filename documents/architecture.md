# Yonned Teknik Mimari ve Sistem Şartnamesi (V1.0 - Master Technical Spec)
**Belge Türü:** Tek Gerçek Kaynağı (Single Source of Truth - Technical SSOT)  
**Tarih:** 28 Ekim 2026  
**Durum:** Kesinleşmiş ve Onaylanmış Ana Belge  
**Felsefe:** *Kutsal Üçlü (Kişi - Aset - Süreç), Sıfır-Docker (Bare-Metal Linux), Sıfır-Blokaj (Non-Blocking), %100 Ücretsiz FOSS*

---

## 1. MİMARİ VİZYON VE NEDEN-SONUÇ İLİŞKİLERİ

### 1.1. Geleneksel Dikey Yazılımların Çıkmazı
Geleneksel yazılımlar sektöre göre katılaşır: Veteriner için ayrı, oto servis için ayrı, tamirhane için ayrı tablolar açılır. Bu durum 3 ölümcül sonuç doğurur:
* **Veri Parçalanması:** Bir kişi (Ayşe Hanım) hem kediye hem arabaya sahiptir; ama iki ayrı sistemde iki yabancı gibi yaşar. Bir patron (Mehmet Bey) hem klinik hem oto servis işletir; iki ayrı hantal ekranda kaybolur.
* **Sahada Blokaj:** Tıraş sırasında kaza olup dikiş gerektiğinde veya barkodu sisteme girilmemiş yeni bir ilaç geldiğinde; geleneksel yazılım *"Önce süreci iptal et"* veya *"Bu barkod kayıtlı değil"* diyerek personeli kilitler. Personel tableti fırlatır, kağıt-kaleme döner.
* **Mekansal Katılık:** Bir şube 2 katlıdır, diğer şube tek katlıdır; birinde 5 kafes vardır, diğerinde açık peron. Katı tablolar bu esnekliği taşıyamaz.

### 1.2. Çözüm: Kutsal Üçlü ve Evrensel Aset Paradigması (The Universal Asset Paradigm)
Fiziksel dünyadaki tüm işletme operasyonları ve varlık ilişkileri tek ve simetrik bir gerçeğe indirgenmiştir:
**"Kişi, Fiziksel Olan Şey ve Fiziksel/Zamansal Süreç aslında tek bir Aset gibi davranır."**

1. **FİZİKSEL ASET (Physical Asset):** İşletmenin kendisi, bayisi, katı, odası, masası, cihazı, ilacı ve müşterinin getirdiği canlı/eşya (özyinelemeli tek ağaç: `parent_id`).
2. **SÜREÇ ASETİ (Temporal Asset / Process):** Zaman boyutunda yaşayan varlıklar (Ameliyat, Bakım, Tıraş, Muayene). Başlangıcı, bitişi, durumu, fotoğrafları ve alt adımları vardır.
3. **İNSAN / AKTÖR (Human Asset / Person):** Sisteme kimlik doğrulamasıyla (Auth/JWT) bağlanan bilinç; işletme açısından ise yetkinlik ve çalışma kapasitesi.

Tüm bu varlıklar tek bir ortak yetki modeliyle yönetilir ve paylaşılır:
* **1. GÖRÜNTÜLE (`can_view`):** Varlığı, konumunu ve üzerinde yürüyen süreçleri/geçmişi izleme yetkisi.
* **2. DEĞİŞTİR (`can_edit`):** Süreç notlarını, varlık bilgilerini veya detayları güncelleme yetkisi.
* **3. EKLE (`can_add`):** Varlık üzerinde yeni süreç başlatma, sarf/ilaç ekleme veya alt varlık tanımlama yetkisi.
* **4. SİL (`can_delete`):** Varlığı veya süreci arşivleme/silme yetkisi.

---

## 2. TOPOLOJİ VE DONANIM MİMARİSİ (TOPOLOGY & HARDWARE)

Sistem kaynak israfını önlemek, operasyonel karmaşıklığı sıfıra indirmek ve bare-metal performans almak amacıyla **2 Düğümlü Mimari (Node102 + Node104)** üzerinde çalışır. Diğer 3 sunucu serbesttir.

```
[ DIŞ DÜNYA: İstemciler ] (Flutter Mobil, Web Admin, Müşteri Tracker)
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
│ • OS: Debian GNU/Linux 13 (Trixie) - Kernel 6.12                       │
│                                                                        │
│ 🛡️ CROWDSEC SAVUNMA KATMANI:                                          │
│ ├── CrowdSec Security Engine (Log analizörü: SSH + Nginx logları)      │
│ ├── nftables Firewall Bouncer: Kötü niyetli IP'leri çekirdekte banlar  │
│ └── Community Threat Intelligence: Küresel kara listeleri önceden çeker│
│                                                                        │
│ 🌐 TERS VEKİL & SSL (Nginx Server + Certbot):                          │
│ ├── Port 80  ➔ 443 Yönlendirmesi                                       │
│ ├── Port 443 ➔ SSL Sonlandırma & Dahili Yönlendirme                    │
│ │   ├── /api/*   ➔ 127.0.0.1:8000 (FastAPI ASGI Uvicorn)               │
│ │   ├── /ws      ➔ 127.0.0.1:8000 (WebSocket Canlı Takip Akışı)        │
│ │   └── /admin, /t/* ➔ Statik Dosyalar / Jinja2 Web Arayüzleri         │
│                                                                        │
│ ⚙️ DAHİLİ SERVİSLER (Yalnızca 127.0.0.1 - Dışarıya Kapalı):           │
│ ├── PostgreSQL 17 (Port 5432 - İlişkisel Veritabanı)                   │
│ ├── Redis 7 (Port 6379 - Soket & Önbellek)                             │
│ └── Uvicorn / FastAPI Workers (Port 8000 - Backend Motoru)             │
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

### Donanım Kaynak Dağılımı ve Port Matrisi:
* **`node102` (Compute & DB):** 9 GB RAM'in yalnızca ~2.85 GB'ı servisler (Postgres, Redis, API, Nginx) tarafından kullanılır; geriye kalan ~6 GB bellek disk I/O önbelleğine ve anlık yüklere kalır.
* **`node104` (Storage):** 3 GB RAM'in ~500 MB'ı MinIO tarafından kullanılır; 1 TB diskte **1.000.000 adet fotoğraf** sıfır bulut maliyetiyle depolanır.

| Sunucu | Port | Protokol | Servis | Dış Dünyaya Açık mı? | Güvenlik Önlemi |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **`node102`** | 22 | TCP | SSH | Evet (Kısıtlı) | Yalnızca SSH Key (Parola Kapalı) + CrowdSec |
| **`node102`** | 80 | TCP | HTTP | Evet | Nginx (Otomatik HTTPS 443 Yönlendirmesi) |
| **`node102`** | 443 | TCP | HTTPS | Evet | Cloudflare WAF + Nginx TLS 1.3 (Certbot SSL) |
| **`node102`** | 8000 | TCP | FastAPI | **HAYIR** | Sadece `127.0.0.1` dinler |
| **`node102`** | 5432 | TCP | PostgreSQL | **HAYIR** | Sadece `127.0.0.1` dinler |
| **`node102`** | 6379 | TCP | Redis | **HAYIR** | Sadece `127.0.0.1` dinler |
| **`node104`** | 22 | TCP | SSH | Evet (Kısıtlı) | Sadece SSH Key + CrowdSec |
| **`node104`** | 9000 | TCP | MinIO S3 | Kısıtlı | Yalnızca `node102` IP'sine izin verilir (nftables) |

---

## 3. YAPILANDIRMA MİMARİSİ (CONFIGURATION ARCHITECTURE)

* **12-Factor App:** Konfigürasyonlar kod içine gömülmez; işletim sistemi ortam değişkenleri (`.env`) üzerinden beslenir.
* **Strict Typing:** Python tarafında **`pydantic-settings`** kullanılır. Eksik veya geçersiz tipte bir ayar varsa sistem ayağa kalkmaz (Fail-Fast).
* **Güvenlik (`chmod 600`):** `.env.production` dosyası yalnızca `root`/`yonned` kullanıcısına okunur, `.gitignore` ile korunur.

```ini
# /var/www/yonned/.env.production
DATABASE_URL=postgresql+asyncpg://yonned:GIZLI_PAROLA@127.0.0.1:5432/yonned_db
REDIS_URL=redis://127.0.0.1:6379/0
SECRET_KEY=64_KARAKTER_HEX_GIZLI_ANAHTAR
S3_ENDPOINT_URL=http://82.39.86.94:9000
S3_ACCESS_KEY=MINIO_ACCESS_KEY
S3_SECRET_KEY=MINIO_SECRET_KEY
S3_BUCKET_NAME=yonned-media
```

---

## 4. İLETİŞİM VE ENTEGRASYON MİMARİSİ (COMMUNICATION & INTEGRATION)

### 4.1. Senkron API Entegrasyonu (REST & OpenAPI)
* **Format:** %100 JSON (UTF-8).
* **Standart:** RESTful ve OpenAPI v3 (Swagger). Kod yazıldığı an `https://api.yonned.com/docs` adresinde interaktif API dökümanı hazırdır.
* **Hata Standardı (RFC 7807):** `{"status": 404, "code": "ASSET_NOT_FOUND", "message": "Kafes #1 bulunamadı"}`.

### 4.2. Asenkron & Gerçek Zamanlı Entegrasyon (WebSocket + Redis Pub/Sub)
Müşterinin takip ekranı açıkken (`/ws/tracker/{token}`):
1. Hekim veya operatör mobilde işlem kaydettiğinde (`POST /api/processes/event`),
2. Veri PostgreSQL'e işlenir,
3. FastAPI, Redis'e mesaj fırlatır (`redis.publish`),
4. Açık WebSocket üzerinden JSON basılır,
5. Müşterinin ekranında sayfa yenilenmeden canlı yeşil tik yanar ve fotoğraf belirir!

### 4.3. Dosya Alışverişi (MinIO S3 Presigned URLs)
Büyük boyutlu resimler backend sunucusunu yormaz:
1. Mobil uygulama izin ister: `POST /api/media/upload-url`
2. Backend 15 dakika geçerli **İmzalı Yükleme URL'i (Presigned PUT)** döner.
3. Mobil uygulama fotoğrafı doğrudan `node104` MinIO sunucusuna yükler.

---

## 5. TEKNOLOJİ VE BAĞIMLILIK MİMARİSİ (TECH STACK & DEPENDENCIES)

| Katman | Teknoloji / Model | Sürüm | Konum / Çalışma Şekli | Neden Seçildi? |
| :--- | :--- | :--- | :--- | :--- |
| **Mobil Uygulama** | **Flutter (Dart)** | 3.x+ | iOS & Android | Tek kodla 60/120 FPS native performans, `mobile_scanner` ile hızlı vizör. |
| **Backend API** | **Python (FastAPI)** | 3.12+ / 0.115+ | `node102` (systemd / Uvicorn) | Bakımı en kolay dil, asenkron hız, otomatik `/docs` Swagger dokümantasyonu. |
| **Veritabanı** | **PostgreSQL** | 17.x | `node102` (Debian Native) | JSONB, recursive hiyerarşi ve ACID güvencesi. |
| **Önbellek & Soket**| **Redis** | 7.x | `node102` (Debian Native) | Canlı müşteri takip akışı, pub/sub ve oturum önbelleği. |
| **Ters Vekil & SSL** | **Nginx + Certbot** | 1.26+ | `node102` (Debian Native) | 20 yıllık stabilite, CrowdSec ile resmi log uyumu, otomatik Let's Encrypt SSL. |
| **Ağ Güvenliği** | **CrowdSec + nftables**| FOSS | `node102` & `node104` | Kaba kuvvet saldırılarını engeller, kötü IP'leri çekirdekte banlar. |
| **Web Arayüzleri** | **HTML5 + Vanilla CSS + JS**| Saf Web | `node102` (Jinja2 / Nginx) | `node_modules` karmaşası yok, mikrosaniyede açılan sayfalar, cam efekti. |
| **Medya Deposu** | **MinIO Server** | Tek Binary | `node104` (`/mnt/data` 1 TB HDD)| AWS S3 maliyetini sıfırlayan yerel nesne depolama motoru. |

---

## 6. VERİTABANI VE VERİ YAPILARI ŞARTNAMESİ (DATA STRUCTURES & SQL)

### 6.1. Ontolojik Model: Evrensel Aset Yaklaşımı ve 4 Temel Fiil
Sistemdeki tüm nesneler, aktörler ve eylemler tek bir ortak ontolojide buluşur:
* **1. KİŞİ (`persons`):** Evrensel kimlik (telefon / JWT). Sisteme giriş yapan conscious aktör.
* **2. FİZİKSEL ASET (`assets`):** Özyinelemeli ağaç (`parent_id`).
  * `İşletme ➔ Bayi ➔ Kat ➔ Oda ➔ Kafes/Lift ➔ Cihaz ➔ Hasta/Araç`.
  * *Varlık Dolaşımı (Asset Roaming):* Kedi Tarçın veya BMW araç şubeler arasında özgürce gezer; kayıt kopyalanmaz.
* **3. SÜREÇ (`processes`):** Zaman boyutunda yaşayan varlıklar. Başlayan, biten (`started_at != ended_at`) veya anlık (`0 sn`) tüm operasyonlar.
* **4. EVRENSEL YETKİ MOTORU (`asset_shares`):**
  Aset sahibi (patron, araç sahibi veya evcil hayvan sahibi), varlığını dilediği kişiyle paylaşır. Yetki 4 temel fiilden ibarettir ve alt varlıklar ile süreçlere özyinelemeli olarak sirayet eder:
  * **`can_view` (Görüntüle):** Varlığı, anlık konumunu ve üzerinde yürüyen tüm süreç/oturum kayıtlarını, fotoğrafları izleme izni.
  * **`can_edit` (Değiştir):** Var olan süreç detaylarını, aşama durumlarını, notları veya varlık bilgilerini güncelleme izni.
  * **`can_add` (Ekle):** Varlık üzerinde yeni bir süreç başlatma, araya acil müdahale ekleme, sarf/ilaç tüketimi girme veya alt varlık tanımlama izni.
  * **`can_delete` (Sil):** Varlığı, süreci veya kaydı iptal etme/arşivleme/silme izni.

### 6.2. Üretim PostgreSQL DDL Şeması
```sql
-- 1. KİŞİLER (Universal Identity)
CREATE TABLE persons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL UNIQUE,       -- Sisteme ana giriş anahtarı
    email VARCHAR(150) UNIQUE,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. KİŞİLERİN BAĞLAMSAL ROLLERİ (Contextual Roles)
CREATE TABLE person_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    tenant_asset_id UUID NOT NULL,            -- Hangi işletme aseti altında yetkili?
    branch_asset_id UUID,                     -- Belirli bir bayi ile sınırlı ise
    system_role VARCHAR(50) NOT NULL,        -- 'superuser', 'admin', 'operator', 'viewer'
    business_title VARCHAR(100),             -- "Veteriner Hekim", "Usta", "Karşılama"
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. EVRENSEL ÖZYİNELEMELİ VARLIK AĞACI (Recursive Asset Tree)
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    parent_id UUID REFERENCES assets(id) ON DELETE CASCADE, -- Hiyerarşi (Kat ➔ Oda ➔ Kafes)
    owner_person_id UUID REFERENCES persons(id),            -- Müşteri varlığı ise kişi ID'si
    owner_type VARCHAR(20) NOT NULL DEFAULT 'business',    -- 'business' | 'customer'
    asset_type VARCHAR(50) NOT NULL, 
    -- 'organization', 'branch', 'floor', 'room', 'station', 'cage', 'bay', 'device', 'consumable', 'pet', 'vehicle'
    name VARCHAR(150) NOT NULL,              -- "Kadıköy Şubesi", "2. Kat", "Kafes #1", "Tarçın", "BMW 3.20"
    identifier VARCHAR(100),                 -- Çip No, Plaka, Seri No, Barkod
    qr_code VARCHAR(100) UNIQUE,             -- Fiziksel QR kod etiketi (loc_..., ast_...)
    current_location_asset_id UUID REFERENCES assets(id), -- Tarçın şu an hangi Kafes asetinde?
    capacity INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_assets_parent ON assets(parent_id);
CREATE INDEX idx_assets_owner ON assets(owner_person_id);
CREATE INDEX idx_assets_qr ON assets(qr_code);

-- 3.1. EVRENSEL VARLIK PAYLAŞIMI (ASSET SHARES - SIFIR KARIŞIKLIK)
-- Kişi assetinin patronudur. Paylaştığı kişinin haklarını 4 bağımsız kutuyla belirler:
CREATE TABLE asset_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    shared_with_person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    
    -- 4 Bağımsız Seçilebilir İzin:
    can_view BOOLEAN DEFAULT TRUE,    -- Görüntüle
    can_edit BOOLEAN DEFAULT FALSE,   -- Değiştir
    can_add BOOLEAN DEFAULT FALSE,    -- Ekle
    can_delete BOOLEAN DEFAULT FALSE, -- Sil
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(asset_id, shared_with_person_id)
);
CREATE INDEX idx_asset_shares_lookup ON asset_shares(shared_with_person_id, asset_id);

-- 4. SÜREÇ ŞABLON KÜTÜPHANESİ (Process Blueprints)
CREATE TABLE process_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name VARCHAR(150) NOT NULL,              -- "Genel Bakım", "Ameliyat", "Aşı", "Yağ Değişimi"
    is_instant BOOLEAN DEFAULT FALSE,       -- TRUE: Anlık Olay (0 sn), FALSE: Süreli Süreç
    default_location_type VARCHAR(50),
    is_customer_visible BOOLEAN DEFAULT TRUE,
    customer_label VARCHAR(255),
    icon VARCHAR(50),
    metadata_schema JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE process_definition_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_definition_id UUID NOT NULL REFERENCES process_definitions(id) ON DELETE CASCADE,
    child_definition_id UUID NOT NULL REFERENCES process_definitions(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    is_optional BOOLEAN DEFAULT TRUE
);

-- 5. CANLI OTURUM VE SÜREÇ AĞACI (Live Execution)
CREATE TABLE asset_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    branch_asset_id UUID NOT NULL REFERENCES assets(id),
    subject_asset_id UUID NOT NULL REFERENCES assets(id),
    status VARCHAR(50) NOT NULL DEFAULT 'checked_in', 
    -- 'checked_in', 'in_service', 'ready_for_pickup', 'completed', 'cancelled'
    current_location_asset_id UUID REFERENCES assets(id),
    tracking_token VARCHAR(100) NOT NULL UNIQUE,          -- Müşteri canlı takip linki
    check_in_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_out_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_sessions_active ON asset_sessions(subject_asset_id, status);

CREATE TABLE live_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES asset_sessions(id) ON DELETE CASCADE,
    definition_id UUID REFERENCES process_definitions(id),
    parent_id UUID REFERENCES live_processes(id) ON DELETE CASCADE,
    previous_id UUID REFERENCES live_processes(id),
    name VARCHAR(150) NOT NULL,
    is_instant BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) NOT NULL DEFAULT 'queued', -- 'queued', 'running', 'paused', 'completed', 'cancelled'
    location_asset_id UUID REFERENCES assets(id),
    assigned_person_id UUID REFERENCES persons(id),
    completed_by_id UUID REFERENCES persons(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    is_customer_visible BOOLEAN DEFAULT TRUE,
    customer_notes VARCHAR(255),
    notes TEXT,
    photos JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);
CREATE INDEX idx_live_proc_session ON live_processes(session_id);

CREATE TABLE live_process_operators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES live_processes(id) ON DELETE CASCADE,
    person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'operator',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. SARF TÜKETİMİ (Consumables & Medicine)
CREATE TABLE process_consumables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES live_processes(id) ON DELETE CASCADE,
    consumable_asset_id UUID REFERENCES assets(id),
    custom_name VARCHAR(150),                       -- Katalogda yoksa anında girilen ad (JIT)
    barcode_scanned VARCHAR(100),
    quantity NUMERIC(10, 2) DEFAULT 1,
    unit VARCHAR(20) DEFAULT 'adet',
    administered_by_id UUID REFERENCES persons(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 7. YAZILIM MİMARİSİ (SOFTWARE ARCHITECTURE)

### 7.1. Backend Mimarisi (FastAPI)
Katmanlı Mimari (Controller ➔ Service ➔ Repository/Model):
```
backend/
├── app/
│   ├── api/v1/              # Endpoint'ler (auth, assets, processes, scanner, tracker, media)
│   ├── core/                # config.py, database.py, redis.py, security.py
│   ├── models/              # SQLAlchemy modelleri (Person, Asset, Process, Consumable)
│   ├── schemas/             # Pydantic şemaları (Giriş/çıkış DTO'ları)
│   ├── services/            # İş mantığı (Süreç motoru, barkod çözümleyici, bildirim)
│   └── templates/           # Jinja2 HTML şablonları (admin, tracker)
├── main.py                  # Giriş noktası & Nginx/Uvicorn köprüsü
└── requirements.txt
```

### 7.2. Mobil Mimarisi (Flutter)
Feature-First & Repository Pattern:
```
mobile/lib/
├── core/                    # API istemcisi, tema, sabitler
├── features/
│   ├── scanner/             # Evrensel Kamera Vizörü (mobile_scanner)
│   ├── process/             # Canlı süreç yönetimi kartları ve butonları
│   ├── station/             # İstasyon & Kafes durum ekranı
│   └── auth/                # Giriş ve profil/şube seçimi
└── main.dart
```

### 7.3. Web UI Mimarisi (HTML5 + Vanilla CSS + JS)
Sıfır derleme, cam efekti (glassmorphism), karanlık mod ve mobil uyumlu responsive tasarım:
```
frontend/ (veya backend/templates & backend/static)
├── static/
│   ├── css/style.css        # Glassmorphism, karanlık tema, CSS değişkenleri
│   └── js/tracker_socket.js # Canlı WebSocket dinleyici ve DOM güncelleyici
└── templates/
    ├── admin/dashboard.html # Patron & Bayi kuşbakışı yönetim ekranı
    └── tracker/live.html    # Müşteri canlı takip sayfası
```

---

## 8. DAĞITIM VE DEVOPS (GIT-NATIVE DEPLOYMENT)

Sunucularda Docker yükü olmadan doğrudan Git tabanlı dağıtım:
1. **Local'de Geliştir:** Kod yazılır, test edilir.
2. **Push:** `git commit -m "feat: core process engine" && git push origin main`
3. **Canlıya Alma (`node102` üzerinde):**
   ```bash
   cd /var/www/yonned
   git pull origin main
   source backend/venv/bin/activate
   pip install -r backend/requirements.txt
   alembic upgrade head
   sudo systemctl restart yonned-api
   ```
4. **Otomatik Yedekleme (`node102` ➔ `node104`):**
   Her gece saat 03:00'te PostgreSQL veritabanı şifrelenir ve SSH üzerinden `node104`ün 1 TB'lık `/mnt/data/yonned-backups/` dizinine kopyalanır.

---

## 9. GERÇEK HAYAT DOĞRULAMA SENARYOLARI (STRES TESTLERİ)

* **Senaryo A (Çok Katlı Bayi & Varlık Dolaşımı):** Tarçın Kadıköy'de Zemin Kat Kafes 1'e girer, 1. Katta ameliyat olur. 3 ay sonra Beşiktaş Şubesine gittiğinde Beşiktaş çalışanı QR'ı okutur; tüm ameliyat geçmişi anında ekrandadır. Sıfır mükerrer kayıt!
* **Senaryo B (Tıraşta Kaza & İlaç Barkodu):** Tıraş devam ederken kesik olur $\rightarrow$ Hekim anında `[+ Acil Müdahale]` sürecini açar $\rightarrow$ Ecza dolabından aldığı spreyin barkodunu okutur (tanımsızsa adını yazar, kaydeder) $\rightarrow$ Dikiş biter, fotoğraf yüklenir $\rightarrow$ Tıraş kaldığı yerden devam eder. Sıfır blokaj!
* **Senaryo C (Patron-Müşteri Geçişi):** Mehmet Bey tek tıkla hem veteriner kliniğini hem oto servisini yönetir. Ayşe Hanım aynı ekranda hem kedisi Tarçın'ın ameliyatını hem BMW'sinin balata değişimini canlı izler.
