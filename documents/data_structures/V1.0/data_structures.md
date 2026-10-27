# Yonned Veri Yapıları Şartnamesi (V1.0)
**Tarih:** 27 Ekim 2026  
**Durum:** Taslak / Onaylandı  
**Mimari Felsefe:** *Generic, Loosely-Coupled (Gevşek Bağlı), İlişkisel ve Blokajsız (Non-Blocking)*

---

## 1. Mimari Vizyon ve Felsefe

Bu veri yapısı; veteriner kliniklerinden oto servis/yıkamalara, elektronik teknik servislerden özel üretim atölyelerine kadar **herhangi bir fiziksel işletmenin operasyonlarını** yönetmek üzere tasarlanmıştır.

### Temel İlkeler:
1. **Her Şey Bir Süreçtir (Everything is a Process):** Sistemde yapay "aksiyon" ve "süreç" ayrımı yoktur. Süresi olan işler (`started_at != ended_at`) ile anlık olan işler (`started_at == ended_at`, 0 saniye) aynı temel nesnedir.
2. **Gevşek Bağlılık (Loosely Coupled):** Hiçbir süreç veya adım bir personeli ya da başka bir süreci kilitlemez. Operasyonlar bağımsız yaşar, kaynaklarla (personel, lokasyon) serbestçe ilişkilendirilir.
3. **Özyinelemeli Hiyerarşi (Recursive / Tree Structure):** Bir süreç içinde başka bir süreç başlayabilir, araya anlık işlemler girebilir, süreç bittiğinde peşine yeni bir süreç takılabilir.
4. **Çift Yönlü QR Mimarisi:** Hem fiziksel alanlar (istasyonlar/odalar/kafesler) hem de varlıklar (müşteri aseti) QR kodlarla fiziksel dünyada sabitlenir.

---

## 2. Temel Varlıklar (Core Entities)

```mermaid
erDiagram
    TENANT ||--o{ USER : employs
    TENANT ||--o{ WORKER_TITLE : defines
    TENANT ||--o{ LOCATION : operates
    TENANT ||--o{ PROCESS_DEFINITION : configures
    TENANT ||--o{ CUSTOMER : serves
    
    USER }|--|{ WORKER_TITLE : holds
    CUSTOMER ||--o{ ASSET : owns
    
    PROCESS_DEFINITION ||--o{ PROCESS_RELATION : parent
    PROCESS_DEFINITION ||--o{ PROCESS_RELATION : child
    
    ASSET ||--o{ ASSET_SESSION : visits
    LOCATION ||--o{ ASSET_SESSION : current_spot
    
    ASSET_SESSION ||--o{ LIVE_PROCESS : executes
    PROCESS_DEFINITION ||--o{ LIVE_PROCESS : instantiates
    LIVE_PROCESS ||--o{ LIVE_PROCESS : parent_child
    LOCATION ||--o{ LIVE_PROCESS : occurs_at
    USER ||--o{ LIVE_PROCESS : operates
```

---

## 3. Detaylı Veri Modeli ve Tablo Şeması

### 3.1. İşletme ve Kişiler Katmanı

#### `tenants` (İşletme)
Platformda hizmet veren her bir işletme/organizasyon.
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}', -- Logo, çalışma saatleri, bildirim ayarları
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `worker_titles` (İşletme Unvanları / Mesleki Tipler)
Patronun kendi sektörüne göre serbestçe tanımladığı unvanlar (Örn: Doktor, Hemşire, Kuaför, Usta, Çırak, Danışman).
```sql
CREATE TABLE worker_titles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title_name VARCHAR(100) NOT NULL, -- "Veteriner Hekim", "Detailing Ustası", "Teknisyen"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `users` (Personel ve Yöneticiler)
Sisteme giriş yapan gerçek kişiler.
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(50),
    
    -- Sistemsel Yetki Rolü:
    system_role VARCHAR(50) NOT NULL DEFAULT 'operator', 
    -- 'owner' (patron), 'admin' (yönetici), 'operator' (çalışan), 'viewer' (sadece izleyici)
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `user_title_assignments` (Kişi-Unvan Çoktan-Çoğa Eşleşmesi)
Bir çalışan birden fazla işletme unvanına sahip olabilir (Tam esneklik).
```sql
CREATE TABLE user_title_assignments (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title_id UUID REFERENCES worker_titles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, title_id)
);
```

---

### 3.2. Fiziksel Mekanlar ve QR Kodlar

#### `locations` (İstasyonlar / Odalar / Alanlar)
İşletmenin fiziksel koordinatları. Her lokasyonun duvara, masaya veya kafese yapıştırılan sabit bir QR kodu vardır.
```sql
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,         -- "Kafes #1", "Ameliyathane 2", "Yıkama Peronu A", "Tezgah 3"
    location_type VARCHAR(50) NOT NULL, -- "cage", "room", "table", "bay", "shelf", "general"
    qr_code VARCHAR(100) NOT NULL UNIQUE, -- Sabit QR token (örn: loc_7a9f8b)
    capacity INTEGER DEFAULT 1,         -- Aynı anda kaç varlık barınabilir?
    metadata JSONB DEFAULT '{}',        -- Ekstra özellikler (örn: oksijen desteği var mı?)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

### 3.3. Müşteri ve Varlık (Asset) Katmanı

#### `customers` (Müşteri)
İşletmeye hizmet almaya gelen gerçek veya tüzel kişi.
```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(150),
    metadata JSONB DEFAULT '{}', -- Adres, vergi no, müşteri özel notu
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `assets` (Müşteri Varlığı / Takip Edilen Şey)
Müşteriye ait olan ve üzerinde işlem yapılan her şey (1 Müşteri $\rightarrow$ N Varlık).
```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,         -- "Tarçın", "34 ABC 123", "iPhone 15 Pro", "Elmas Kolye"
    identifier VARCHAR(100),            -- Mikroçip No, Şasi No, IMEI, Seri No
    qr_code VARCHAR(100) UNIQUE,        -- Varlığa yapıştırılan / tasmaya takılan dinamik etiket QR
    metadata JSONB DEFAULT '{}',        -- Sektörel esnek veriler (Tür, Irk, Doğum Tarihi / Model, KM)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

### 3.4. Süreç Şablon Kütüphanesi (Admin Tanımları)

Adminin web panelinden tanımladığı bağımsız Lego parçaları ve bunların birbirine bağlanması.

#### `process_definitions` (Süreç ve Adım Şablonları)
```sql
CREATE TABLE process_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,          -- "Genel Bakım", "Yıkama", "Tıraş", "Mama Verme", "Aşı"
    is_instant BOOLEAN DEFAULT FALSE,   -- TRUE: Anlık Olay (0 sn), FALSE: Süreli Süreç (Başla/Bitir)
    default_location_id UUID REFERENCES locations(id), -- Önerilen varsayılan lokasyon
    is_customer_visible BOOLEAN DEFAULT TRUE,          -- Müşteri takip ekranında görünsün mü?
    customer_label VARCHAR(255),         -- Müşteriye görünecek dil (örn: "Dostunuzun bakımı yapılıyor")
    icon VARCHAR(50),                    -- Mobilde görünecek ikon
    metadata_schema JSONB DEFAULT '{}',  -- Form/giriş alanları şeması (ör. kilo, ateş, parça no)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `process_relations` (Şablon Kompozisyonu / İç İçe ve Sıralı Bağlama)
Süreçlerin birbirine prangalanmadan, ilişkisel olarak önerilmesini sağlayan tablo.
```sql
CREATE TABLE process_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_definition_id UUID NOT NULL REFERENCES process_definitions(id) ON DELETE CASCADE,
    child_definition_id UUID NOT NULL REFERENCES process_definitions(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,        -- Varsayılan sıra önerisi
    is_optional BOOLEAN DEFAULT TRUE     -- Çalışan bu adımı atlayabilir mi?
);
```

---

### 3.5. Canlı İşleyiş Katmanı (Runtime Execution)

#### `asset_sessions` (Varlığın İşletmedeki Yaşam Döngüsü / Ziyaret)
Varlığın kapıdan girdiği an başlayan, teslim edilene kadar açık kalan en üst çatı.
```sql
CREATE TABLE asset_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    
    status VARCHAR(50) NOT NULL DEFAULT 'open', 
    -- 'open' (dükkanda işlem görüyor), 'ready_for_pickup' (bitti, teslim bekliyor), 'closed' (teslim edildi)
    
    current_location_id UUID REFERENCES locations(id), -- Şu an fiziki olarak hangi istasyonda/kafeste?
    
    tracking_token VARCHAR(100) NOT NULL UNIQUE,       -- Müşteri canlı takip linki token'ı
    
    check_in_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_out_at TIMESTAMP WITH TIME ZONE              -- Teslim edilince dolar
);
```

#### `live_processes` (Canlı Süreç Ağacı - Başlayan, Biten, Araya Giren İşler)
İster 2 günlük yatış, ister 40 dakikalık tıraş, ister 1 saniyelik mama verme, ister araya giren acil dikiş müdahalesi... Hepsi bu tablodaki bir düğümdür (`Node`).
```sql
CREATE TABLE live_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES asset_sessions(id) ON DELETE CASCADE,
    definition_id UUID REFERENCES process_definitions(id), -- Hangi şablondan türedi? (Serbest ise NULL)
    
    -- Özyinelemeli İlişkiler:
    parent_id UUID REFERENCES live_processes(id) ON DELETE CASCADE, -- İç içe süreçler için
    previous_id UUID REFERENCES live_processes(id),                 -- Sıralı akış zinciri için
    
    name VARCHAR(150) NOT NULL,          -- "Tıraş", "Pansuman", "Mama Verildi"
    status VARCHAR(50) NOT NULL,         -- 'queued', 'running', 'paused', 'completed', 'cancelled'
    
    -- Fiziksel Mekan:
    location_id UUID REFERENCES locations(id), -- O an nerede yapıldı/yapılıyor?
    
    -- Operatör / Çalışan (Kilitleyici değil, ilişkisel):
    assigned_operator_id UUID REFERENCES users(id), -- Süreci üzerine alan / atanan
    completed_by_id UUID REFERENCES users(id),      -- Süreci tamamlayan / kapatan
    
    -- Zaman Çizelgesi:
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,              -- Anlık işlemlerde started_at ile aynıdır
    duration_seconds INTEGER,                       -- Otomatik hesaplanan süre
    
    -- Müşteri İletişimi:
    is_customer_visible BOOLEAN DEFAULT TRUE,
    customer_notes VARCHAR(255),
    
    -- Kanıt & Ekstra Veriler:
    notes TEXT,
    photos JSONB DEFAULT '[]',           -- ["https://s3.../photo1.jpg"]
    metadata JSONB DEFAULT '{}'          -- Ateş, kilo, kullanılan malzeme vb.
);
```

#### `live_process_operators` (Çoklu Operatör Katılımı)
Bir ameliyatta veya oto yıkamada birden fazla çalışan aynı süreç üzerinde eşzamanlı çalışabilir.
```sql
CREATE TABLE live_process_operators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES live_processes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'operator', -- 'lead', 'assistant', 'collaborator'
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 4. QR Kod İşleyiş Mekanizması

Sistemde QR okutma 3 temel akışta çalışır:

1. **Sabit Lokasyon QR'ı (İstasyon Tespiti):**
   * Çalışan kafesteki QR'ı okutur (`loc_cage_01`).
   * Mobil uygulama anında o lokasyonun kartını açar: 
     * İçinde varlık varsa: O varlığın aktif süreçleri ve hızlı işlem butonları listelenir.
     * Boş ise: *"Bu istasyona varlık yerleştir"* seçeneği çıkar.
2. **Dinamik Varlık QR'ı (Hasta / Araç / Cihaz Tespiti):**
   * Çalışan varlığın tasmasındaki/camındaki etiketi okutur (`ast_99182`).
   * Mobil uygulama doğrudan o varlığın açık olan `asset_session` kartını açar.
3. **Mekan Doğrulamalı Süreç Başlatma (Opsiyonel Güvenlik):**
   * Süreç başlatılırken çalışandan fiziksel mekanın QR'ını okutması istenerek personelin fiziken orada olduğu kanıtlanır.

---

## 5. Stres Testi Senaryoları ile Doğrulama

### Senaryo 1: Standart Akış
1. Kedi "Tarçın" kliniğe girer $\rightarrow$ `asset_sessions` açılır.
2. `live_processes` içine "Genel Bakım" (running) eklenir.
3. İçine alt süreç "Yıkama" eklenir $\rightarrow$ Biter.
4. İçine alt süreç "Tıraş" eklenir $\rightarrow$ Biter.
5. "Genel Bakım" biter.
6. Tarçın Kafes #2'ye alınır (`current_location_id = Kafes 2`, `session.status = ready_for_pickup`).
7. Müşteri gelir, teslim edilir $\rightarrow$ `session.status = closed`.

### Senaryo 2: Beklenmedik Olay / Acil Müdahale (Non-Blocking Testi)
1. Tıraş devam ederken kaza gerçekleşir.
2. Açık olan "Tıraş" süreci `status: paused` yapılır (veya açık bırakılır).
3. Hekim hemen yeni bir süreç oluşturur: "Acil Dikiş & Müdahale" (`status: running`, `operator: Dr. Mehmet`).
4. Dikiş atılır, fotoğraf yüklenir, süreç `status: completed` yapılır.
5. Kuaför duraklatılan "Tıraş" sürecine geri döner, tamamlar.
6. **Sonuç:** Hiçbir sistem hatası oluşmaz; hem tıbbi müdahale hem kuaförlük süreci tek bir zaman tünelinde eksiksiz kayıt altına alınır.
