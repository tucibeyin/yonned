# Yonned Mimari ve Veri Yapıları Şartnamesi (V1.0)
**Belge Sürümü:** 1.0.0  
**Tarih:** 28 Ekim 2026  
**Durum:** Temel Mimari Referans Belgesi (Master Architecture Document)  
**Tasarım Felsefesi:** *Kutsal Üçlü (Kişi - Aset - Süreç), Gevşek Bağlılık (Loosely-Coupled), Sıfır-Blokaj (Non-Blocking) ve Özyinelemeli Ağaç (Recursive Tree)*

---

## BÖLÜM 1: NEDEN BÖYLE BİR MİMARİ? (SEBEP - SONUÇ İLİŞKİLERİ)

Geleneksel yazılım dünyasında işletme operasyonları yönetilirken yapılan en ölümcül hata **"Dikey ve Katı Modeller" (Rigid Vertical Models)** üretmektir:
* Veteriner için ayrı bir yazılım yazılır (hasta, aşı, kafes tabloları).
* Oto servis için ayrı bir yazılım yazılır (plaka, lift, usta tabloları).
* Elektronik tamir için ayrı yazılır (arıza, lehim masası, yedek parça tabloları).

Bu yaklaşım üç büyük çöküşe sebep olur:
1. **Veri Parçalanması ve Tekrar (Duplication):** Bir insan (Ayşe Hanım) aynı anda hem kedi sahibi hem araba sahibidir; ama iki ayrı programda iki yabancı gibi yaşar. Bir girişimci (Mehmet Bey) hem klinik hem oto servis işletir; iki ayrı ekranda birbirini tanımayan hantal sistemlerle boğuşur.
2. **Sahada Blokaj ve Sürtünme (Friction & Dead-Ends):** Katı sistemler personeli bürokrasiye boğar. Tıraş yapılırken kaza olup acil müdahale gerekirse veya barkodu sistemde olmayan yeni bir ilaç gelirse; geleneksel yazılım *"Önce süreci iptal et"* veya *"Bu barkod kayıtlı değil, yöneticinize başvurun"* diyerek çalışanı kilitler. Sahadaki personel tableti fırlatır, kağıt-kaleme döner.
3. **Mekansal Katılık (Spatial Rigidity):** Bir şube 2 katlıdır, diğer şube tek katlıdır; birinde 5 kafes vardır, diğerinde 2 açık peron. Katı tablolar bu esnekliği taşıyamaz.

### Çözüm Felsefemiz: Kutsal Üçlü (The Ontological Trinity)
Fiziksel dünyadaki tüm işletme operasyonları aslında sadece **üç evrensel soruya** indirgenebilir:
* **KİM? $\rightarrow$ KİŞİ (Person):** Hizmet veren (düzenleyici) veya hizmet alan (sorgulayıcı) insanlar.
* **NE & NEREDE? $\rightarrow$ ASET (Asset):** İşletmenin kendisi, bayisi, katı, odası, masası, cihazı, ilacı ve müşterinin getirdiği canlı/eşya.
* **NE OLUYOR? $\rightarrow$ SÜREÇ (Process):** Kişilerin asetler üzerinde, belirli mekanlarda zaman içinde icra ettiği tüm olaylar ve yaşam döngüleri.

---

## BÖLÜM 2: KUTSAL ÜÇLÜNÜN ANATOMİSİ

```
┌────────────────────────────────────────────────────────────────────────┐
│                        YONNED ÇEKİRDEK MİMARİSİ                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   1. KİŞİ (Person) ────────────────────────────────────────────────┐   │
│      └── Kimlik tektir. Bağlama göre rol alır:                     │   │
│          • DÜZENLEYİCİ: Superuser, Admin, Operator                 │   │
│          • SORGULAYICI: Müşteri (Kendi varlıklarını izleyen)       │   │
│                                                                    ▼   │
│   2. ASET (Asset - Recursive Tree) ───────────────► 3. SÜREÇ (Process) │
│      └── Mekanlar, Cihazlar ve Canlılar:            └── Ne yapılıyor?  │
│          İşletme ➔ Bayi ➔ Kat ➔ Oda ➔ Masa          • Süreli (Döngü)   │
│          ➔ Cihaz ➔ Hasta / Araç / Cihaz             • Anlık (0 sn Olay)│
│                                                     • İç içe / Sıralı  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## BÖLÜM 3: 1. SÜTUN — KİŞİ VE ÇİFT YÖNLÜ ETKİLEŞİM MODELİ

### 3.1. Düzenleyici vs. Sorgulayıcı Ayrımı
Sistemdeki her insan (`persons`) potansiyel olarak iki tarafta da yer alabilir:
* **DÜZENLEYİCİ (Mutator / Provider):**  
  Sisteme veri besleyen, süreç başlatan/bitiren, QR basan, barkod okutan taraftır.  
  *Tipleri:*
  * `SUPERUSER` (Mimar / Çatı Sahip): Tüm işletmeleri, şubeleri, genel tanımları düzenler.
  * `ADMIN` (Şube Yöneticisi): Belirli bir bayiyi, personeli ve süreçleri düzenler.
  * `OPERATOR` (Saha Çalışanı): Sahada eldiveni takıp süreci yürüten, veri üreten personel (Veteriner hekim, teknisyen, usta, kuaför).
* **SORGULAYICI (Querier / Consumer / Client):**  
  Süreci izleyen, durumunu merak eden, fotoğrafına bakan taraftır (Müşteri).  
  *Kural:* Bir kişi bir asetin sahibi (`asset.owner_person_id`) ise, o kişi o asetin tüm süreçlerinin doğal **Sorgulayıcısıdır**.

### 3.2. Bağlamsal Yetki (Contextual RBAC)
* **Neden?** Dr. Özge kendi kliniğinde bir `OPERATOR` iken, akşam arabasını bıraktığı oto serviste bir `MÜŞTERİ`dir. İki ayrı hesap açmak saçmalıktır.
* **Sonuç:** Kişi tek bir telefon numarasıyla sisteme giriş yapar. Ekranda **"İşletme Modu"** (Düzenleyici) ile **"Kişisel Varlıklarım"** (Sorgulayıcı) arasında tek tıkla geçiş yapar.

---

## BÖLÜM 4: 2. SÜTUN — EVRENSEL ÖZYİNELEMELİ VARLIK AĞACI (RECURSIVE ASSET TREE)

Geleneksel veritabanlarındaki `branches`, `rooms`, `cages`, `devices`, `materials` ve `customer_pets` tablolarının hepsi kaldırılmıştır. Çünkü hepsi **aynı genetik yapıya** sahiptir:

### 4.1. Hiyerarşik Varlık Ağacı Örneği
Her varlığın bir `parent_id`si vardır. Böylece sonsuz derinlikte mekansal ve fiziksel ağaçlar kurulur:

```
📦 ASET: "Pati Sağlık Grubu" (Tip: organization, Sahip: Mehmet Bey)
│
├── 📦 ASET: "Kadıköy Şubesi" (Tip: branch, Parent: Pati Grubu)
│   │
│   ├── 📦 ASET: "Zemin Kat" (Tip: floor, Parent: Kadıköy)
│   │   ├── 📦 ASET: "Kabul Bankosu" (Tip: station) ── [Sabit QR: loc_kdk_bnk]
│   │   ├── 📦 ASET: "Kafes #1" (Tip: cage) ───────── [Sabit QR: loc_kdk_kf1]
│   │   └── 📦 ASET: "MR Cihazı 1" (Tip: equipment) ── [Sabit QR: loc_kdk_mr1]
│   │
│   ├── 📦 ASET: "1. Kat" (Tip: floor, Parent: Kadıköy)
│   │   ├── 📦 ASET: "Ameliyathane 1" (Tip: room) ─── [Sabit QR: loc_kdk_am1]
│   │   │     └── 📦 ASET: "Cerrahi Masası A" ────── [Sabit QR: loc_kdk_msA]
│   │   └── 📦 ASET: "Kafes #2" (Tip: cage) ───────── [Sabit QR: loc_kdk_kf2]
│   │
│   └── 📦 ASET: "Amoklavin 500mg" (Tip: consumable, Kat bağımsız) ── [Barkod: 8699...]
│
└── 📦 MÜŞTERİ ASETİ: "Kedi Tarçın" (Tip: subject, Sahip: Ayşe Hanım) ── [QR: ast_trcn_01]
```

### 4.2. Bu Modelin Kazandırdığı 3 Devrim:
1. **İşletme Demirbaşları da Bakım Görür:** MR Cihazı da bir asettir. Tıpkı bir kedinin ameliyat olması gibi, MR Cihazı üzerinde de "Yıllık Kalibrasyon Süreci" işletilebilir.
2. **Sıfır Tekrar ile Varlık Dolaşımı (Asset Roaming):** Kedi Tarçın veya 34 ABC 123 plakalı BMW, Kadıköy şubesinden Beşiktaş şubesine gittiğinde yeni bir kayıt açılmaz. `current_location_asset_id` Beşiktaş'taki bir kafese/lifte güncellenir. Tüm tıbbi ve mekanik geçmişi tek bir zaman çizelgesinde kalır.
3. **Mekansal Sorgulama Gücü:** *"Kadıköy Şubesi Zemin Katta şu an hangi kafesler dolu?"* sorusunun cevabı, tek bir hiyerarşik SQL sorgusudur.

---

## BÖLÜM 5: 3. SÜTUN — EVRENSEL SÜREÇ MOTORU (UNIFIED PROCESS ENGINE)

### 5.1. Neden "Aksiyon" ve "Süreç" Ayrımı Yoktur?
Bilgisayar biliminde her şey bir zaman aralığıdır:
* **Süreli Süreç (`is_instant = false`):** Başlar ve biter (`started_at` ve `ended_at` vardır). Zaman akar, mekanı işgal eder. (Örn: 2 saatlik Ameliyat, 45 dakikalık Tıraş, 3 günlük Yatış).
* **Anlık Olay (`is_instant = true`):** Başladığı an biter (`started_at == ended_at`, süre 0 sn). Bir sürecin içine atılan zaman damgalı bir izdir. (Örn: Mama verildi, ateş 38.5 ölçüldü, aşı enjekte edildi, fotoğraf çekildi).

### 5.2. Özyinelemeli Akış (Recursive Process Spans)
Süreçler `parent_id` ve `previous_id` ile birbirine bağlanır. Bu sayede sahadaki akış sonsuz esneklik kazanır:

```
🌀 SÜREÇ: "Genel Bakım" [10:00 ➔ 12:00] (Mekan: Bakım Odası, Operatör: Ali)
│
├── 🌀 İÇ SÜREÇ: "Yıkama & Kurutma" [10:05 ➔ 10:40] (Mekan: Küvet)
│     └── ⚡ ANLIK OLAY: "Özel şampuan uygulandı" (10:15)
│
├── ⚡ ANLIK OLAY: "Ödül maması verildi" (10:45)
│
├── 🌀 BEKLENMEDİK İÇ SÜREÇ: "Acil Dikiş & Müdahale" [10:50 ➔ 11:05] (Operatör: Dr. Özge)
│     └── ⚡ SARF KULLANIMI: "Yara Spreyi (1 Doz)" [Barkod okutuldu]
│
└── 🌀 İÇ SÜREÇ: "Tıraş Tamamlama" [11:10 ➔ 11:50] (Mekan: Tıraş Masası)
```

### 5.3. Süreçlerin Özgürlüğü (Non-Blocking)
* **Personele Tapulu Değildir:** Bir süreci Ali başlatabilir, mola verince nöbetçi Veli devralıp bitirebilir. Sistem bunu engellemez; her dokunuşu kimin yaptığını loglar.
* **Mekana Tapulu Değildir:** Süreç ameliyathanede başlar, hasta kafese taşınırsa sürecin mekan referansı güncellenir.
* **Araya İş Girebilir:** Tıraş devam ederken araya acil müdahale süreci açılabilir. Tıraş kilitlenmez, duraklatılabilir veya paralel yürütülebilir.

---

## BÖLÜM 6: 4. SÜTUN — SARF TÜKETİMİ VE EVRENSEL TARAYICI (UNIVERSAL SCANNER)

Sahada çalışan hekim veya usta ekranda form dolduramaz. Mobil uygulamadaki **tek bir kamera vizörü** taranan her formatı anında hedefine bağlar:

```
                      ┌─── [1. 'loc_' Ön Eki] ──► FİZİKSEL MEKAN (Kafes / Masa / Peron)
                      │                            ➔ Mekan kartını aç, varlığı buraya transfer et.
                      │
                      ├─── [2. 'ast_' Ön Eki] ──► MÜŞTERİ / İŞLETME VARLIĞI (Hasta / Cihaz)
[KAMERA VİZÖRÜ] ──────┼                            ➔ Canlı süreç kartını ve geçmişini aç.
                      │
                      ├─── [3. 'ses_' Ön Eki] ──► CANLI OTURUM / BİLET (Müşteri Takip Fişi)
                      │                            ➔ Doğrudan aktif ziyareti aç.
                      │
                      ├─── [4. Kayıtlı Barkod] ─► SARF MALZEME (İlaç / Şampuan / Yedek Parça)
                      │                            ➔ Açık olan sürece sarfiyat olarak iliştir.
                      │
                      └─── [5. Tanımsız Barkod] ─► ANINDA EKLE (On-The-Fly / JIT Cataloging)
                                                   ➔ Sistem durmaz; "Ürün Adı:" sorar, kaydeder.
                                                   ➔ Hem kataloğa girer hem sürece bağlanır!
```

### Sıfır Blokajın 3 Altın Kuralı:
1. **Kamera Yoksa Liste Vardır:** Kamera kırık veya barkod yırtıksa her varlık, mekan ve ilaç listeden elle seçilebilir.
2. **Katalogda Olmama Hatası Yoktur:** Sistem asla "Ürün bulunamadı" diye işlemi durdurmaz; hemen orada kaydettirir.
3. **Rol Engeli Yoktur:** İlacı o an kim verdiyse onun imzasıyla kaydeder, sistemi kilitlemez.

---

## BÖLÜM 7: VERİTABANI ŞEMASI (POSTGRESQL DDL)

Bu felsefeyi hayata geçiren, gereksiz tüm tabloları elenmiş, **kompakt ve ilişkisel** üretim şeması:

```sql
-- ============================================================================
-- 1. KİŞİLER VE BAĞLAMSAL YETKİLER (ACTORS & CONTEXTUAL ROLES)
-- ============================================================================

-- Evrensel İnsan Tablosu (Hem patron, hem personel, hem müşteri)
CREATE TABLE persons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL UNIQUE,       -- Sisteme ana giriş anahtarı
    email VARCHAR(150) UNIQUE,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bir kişinin hangi işletme/bayide hangi düzenleyici yetkisi var?
CREATE TABLE person_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    tenant_asset_id UUID NOT NULL,            -- Hangi işletme aseti altında yetkili?
    branch_asset_id UUID,                     -- Belirli bir bayi ile sınırlı ise
    
    -- Sistemsel Düzenleyici Rolü:
    system_role VARCHAR(50) NOT NULL,        -- 'superuser', 'admin', 'operator', 'viewer'
    
    -- İşletme İçi Mesleki Unvan (Serbest):
    business_title VARCHAR(100),             -- "Veteriner Hekim", "Kaporta Ustası", "Karşılama"
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================================
-- 2. EVRENSEL VARLIK AĞACI (RECURSIVE ASSET TREE)
-- ============================================================================

-- Mekanlar, Cihazlar, Sarf Malzemeler ve Müşteri Varlıkları tek bir tablodadır.
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,                 -- Hangi en üst işletme şemsiyesinde?
    parent_id UUID REFERENCES assets(id) ON DELETE CASCADE, -- Hiyerarşi (Kat ➔ Oda ➔ Kafes)
    
    -- Sahiplik:
    owner_person_id UUID REFERENCES persons(id), -- Müşteri varlığı ise sahibi kişi; şirket ise NULL
    owner_type VARCHAR(20) NOT NULL DEFAULT 'business', -- 'business' | 'customer'
    
    -- Varlık Tipi (Ontolojik Sınıflandırma):
    asset_type VARCHAR(50) NOT NULL, 
    -- Mekansal: 'organization', 'branch', 'floor', 'room', 'station', 'cage', 'bay'
    -- Ekipman:  'device', 'equipment', 'vehicle_tool'
    -- Sarf:     'consumable', 'medicine', 'spare_part'
    -- Özne:     'pet', 'customer_vehicle', 'customer_device', 'custom_subject'
    
    name VARCHAR(150) NOT NULL,              -- "Kadıköy Şubesi", "2. Kat", "Kafes #1", "Tarçın", "BMW 3.20"
    identifier VARCHAR(100),                 -- Çip No, Plaka, Seri No, IMEI, Barkod
    qr_code VARCHAR(100) UNIQUE,             -- Fiziksel QR kod etiketi (loc_..., ast_...)
    
    -- Anlık Fiziksel Konum:
    current_location_asset_id UUID REFERENCES assets(id), -- Örn: Tarçın şu an hangi Kafes asetinde?
    
    capacity INTEGER DEFAULT 1,              -- Mekan ise kapasitesi (Kafes: 1, Bekleme Salonu: 20)
    metadata JSONB DEFAULT '{}',             -- Dinamik alanlar (Irk, Renk, Model, Dozaj, Oksijen desteği)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_assets_parent ON assets(parent_id);
CREATE INDEX idx_assets_owner ON assets(owner_person_id);
CREATE INDEX idx_assets_qr ON assets(qr_code);


-- ============================================================================
-- 3. SÜREÇ ŞABLON KÜTÜPHANESİ (BLUEPRINTS / TEMPLATES)
-- ============================================================================

-- Adminin tanımladığı bağımsız lego süreçler
CREATE TABLE process_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name VARCHAR(150) NOT NULL,              -- "Genel Bakım", "Ameliyat", "Aşı", "Yağ Değişimi"
    is_instant BOOLEAN DEFAULT FALSE,       -- TRUE: Anlık Olay (0 sn), FALSE: Süreli Süreç
    default_location_type VARCHAR(50),       -- Önerilen mekan tipi (örn: 'cage', 'room')
    is_customer_visible BOOLEAN DEFAULT TRUE,
    customer_label VARCHAR(255),             -- Müşteriye giden bildirim dili
    icon VARCHAR(50),
    metadata_schema JSONB DEFAULT '{}',      -- Form giriş şeması (Ateş, kilo, parça no)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Şablonların birbirine bağlanması (İç içe veya sıralı süreç legoları)
CREATE TABLE process_definition_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_definition_id UUID NOT NULL REFERENCES process_definitions(id) ON DELETE CASCADE,
    child_definition_id UUID NOT NULL REFERENCES process_definitions(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    is_optional BOOLEAN DEFAULT TRUE
);


-- ============================================================================
-- 4. CANLI YAŞAM DÖNGÜSÜ VE SÜREÇ AĞACI (RUNTIME EXECUTION)
-- ============================================================================

-- Varlığın işletmedeki kabul/ziyaret oturumu (Check-in ➔ Check-out)
CREATE TABLE asset_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    branch_asset_id UUID NOT NULL REFERENCES assets(id),  -- Hangi şube asetinde misafir?
    subject_asset_id UUID NOT NULL REFERENCES assets(id), -- Hangi hayvan / araç / cihaz misafir?
    
    status VARCHAR(50) NOT NULL DEFAULT 'checked_in', 
    -- 'checked_in', 'in_service', 'ready_for_pickup', 'completed', 'cancelled'
    
    current_location_asset_id UUID REFERENCES assets(id), -- Şu an fiziken hangi kafeste/lifte?
    tracking_token VARCHAR(100) NOT NULL UNIQUE,          -- Müşterinin canlı takip web linki
    
    check_in_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    check_out_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_sessions_active ON asset_sessions(subject_asset_id, status);

-- Canlıda işleyen tüm süreç ve anlık olay düğümleri (Recursive Tree)
CREATE TABLE live_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES asset_sessions(id) ON DELETE CASCADE,
    definition_id UUID REFERENCES process_definitions(id),
    
    -- Özyinelemeli İlişkiler:
    parent_id UUID REFERENCES live_processes(id) ON DELETE CASCADE, -- İç süreç ise
    previous_id UUID REFERENCES live_processes(id),                 -- Sıralı akış ise
    
    name VARCHAR(150) NOT NULL,              -- "Tıraş", "Pansuman", "Mama Verildi"
    is_instant BOOLEAN DEFAULT FALSE,       -- TRUE: Anlık olay, FALSE: Süreli süreç
    status VARCHAR(50) NOT NULL DEFAULT 'queued', -- 'queued', 'running', 'paused', 'completed', 'cancelled'
    
    -- Mekan ve Operatör İlişkisi:
    location_asset_id UUID REFERENCES assets(id), -- Hangi mekan asetinde yapılıyor?
    assigned_person_id UUID REFERENCES persons(id), -- Süreci yürüten / üzerine alan kişi
    completed_by_id UUID REFERENCES persons(id),    -- Süreci tamamlayan kişi
    
    -- Zaman Çizelgesi:
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,       -- Anlık ise started_at ile aynıdır
    duration_seconds INTEGER,
    
    -- Müşteri İletişimi:
    is_customer_visible BOOLEAN DEFAULT TRUE,
    customer_notes VARCHAR(255),
    
    -- Kanıt & Ekstra Veriler:
    notes TEXT,
    photos JSONB DEFAULT '[]',               -- ["https://.../wound.jpg"]
    metadata JSONB DEFAULT '{}'              -- Ölçümler, vital bulgular vb.
);

CREATE INDEX idx_live_proc_session ON live_processes(session_id);
CREATE INDEX idx_live_proc_parent ON live_processes(parent_id);

-- Çoklu Personel Katılımı (Bir ameliyatta veya oto yıkamada birden fazla kişi çalışabilir)
CREATE TABLE live_process_operators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES live_processes(id) ON DELETE CASCADE,
    person_id UUID NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'operator',     -- 'lead', 'assistant', 'recorder'
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================================
-- 5. SARF TÜKETİMİ VE İLAÇ KULLANIMI (PROCESS CONSUMABLES)
-- ============================================================================

-- Hangi süreçte hangi ilaçtan, parçadan veya sarf malzemeden ne kadar kullanıldı?
CREATE TABLE process_consumables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES live_processes(id) ON DELETE CASCADE,
    consumable_asset_id UUID REFERENCES assets(id), -- Varlık ağacındaki sarf malzeme (varsa)
    
    custom_name VARCHAR(150),                       -- Katalogda yoksa o an yazılan ad
    barcode_scanned VARCHAR(100),                   -- Okutulan fiziksel barkod
    quantity NUMERIC(10, 2) DEFAULT 1,              -- 1 kutu, 2.5 ml, 4 litre
    unit VARCHAR(20) DEFAULT 'adet',
    
    administered_by_id UUID REFERENCES persons(id), -- Hangi hekim/usta uyguladı?
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## BÖLÜM 8: STRES TESTLERİ VE GERÇEK HAYAT SİMÜLASYONLARI

### Simülasyon A: Çoklu Bayi, Çok Katlı Mekan ve Varlık Dolaşımı
* **Vaka:**  
  Pati Sağlık Grubu'nun Kadıköy (2 katlı) ve Beşiktaş (2 katlı) şubeleri vardır. Kedi Tarçın Kadıköy'e gelir.
* **Akış:**
  1. Zemin Katta karşılama personeli Tarçın'ın `ast_trcn` QR'ını okutur $\rightarrow$ Ziyaret başlar (`asset_sessions.branch = Kadıköy`).
  2. Tarçın Zemin Kat Kafes #1'e yerleştirilir (`current_location_asset_id = Kafes 1`).
  3. Ameliyat zamanı gelince 1. Kata çıkarılır $\rightarrow$ Ameliyathane 1 Masası QR'ı okutulur. Süreç başlar.
  4. 3 ay sonra sahibi Tarçın'ı Beşiktaş Şubesine götürür. Beşiktaş personeli Tarçın'ın QR'ını okutur.
* **Sonuç:**  
  Tarçın'ın geçmiş ameliyatı, Kadıköy'deki dikiş fotoğrafları ve kullanılan antibiyotikler saniyede ekrana gelir. Beşiktaş için yeni bir ziyaret oturumu açılır. **Sıfır mükerrer kayıt, sıfır veri kaybı.**

### Simülasyon B: Tıraş Esnasında Kaza, Acil Müdahale ve İlaç Barkodu
* **Vaka:**  
  Tıraş Masasında tıraş yapılırken makine kesik yapar.
* **Akış:**
  1. Kuaför açık olan "Tıraş" sürecini duraklatır (`status = paused`).
  2. Ekranda `[+ Acil Müdahale]` süreci açar (`operator = Dr. Özge`).
  3. Dr. Özge ecza dolabından aldığı spreyin barkodunu kameraya tutar. Barkod sistemde kayıtlı değildir.
  4. Sistem durmaz; ekranda *"Yeni Ürün: Adını girin"* der. Dr. Özge *"Yara Spreyi"* yazar, kaydeder.
  5. İlaç sürece bağlanır, yaranın dikiş fotoğrafı yüklenir, müdahale süreci tamamlanır (`status = completed`).
  6. Kuaför duraklatılan "Tıraş" sürecine geri döner ve bitirir.
* **Sonuç:**  
  Sistem hiçbir kural hatası vermez. Tıbbi müdahale, kuaförlük ve tüketilen ilaç tek bir zaman tüneline pürüzsüzce işlenir.

### Simülasyon C: Aynı Kişinin Hem Patron Hem Müşteri Olması
* **Vaka:**  
  Mehmet Bey hem Pati Veteriner Kliniği'nin hem de Demir Oto Servis'in sahibidir. Ayşe Hanım'ın ise hem kedisi hem arabası vardır.
* **Akış:**
  1. Mehmet Bey admin panele girer: Tek tıkla Kliniğinin kafes doluluğunu görür, diğer tıkla Oto Servisinin lift doluluğunu görür.
  2. Ayşe Hanım `yonned.com/t/ayse-yilmaz` linkini açar: Kedisi Tarçın'ın Kadıköy'deki ameliyat durumunu ve arabası BMW'nin Maslak'taki balata değişim fotoğrafını aynı ekranda görür.
* **Sonuç:**  
  İnsan tektir, kimlik tektir. Ne işletmeler birbirine karışır ne de müşteri iki ayrı uygulamayla uğraşmak zorunda kalır.

---

## BÖLÜM 9: ÖZET VE MİMARİ KAZANIMLAR

Bu şartname ile Yonned platformu:
1. **En Düşük Tablo Sayısı, En Yüksek İfade Gücü:** 50 hantal tablo yerine sadece 5 çekirdek tablo (`persons`, `assets`, `process_definitions`, `asset_sessions`, `live_processes`) ile tüm fiziksel dünyayı modeller.
2. **Sıfır Blokajlı Operasyon:** Sahada personelin önüne hiçbir sanal engel çıkarmaz; hızlıdır, akışkandır, insan odaklıdır.
3. **Uluslararası Ölçeklenebilirlik:** Küçük bir veteriner de, 100 bayili küresel bir servis ağı da aynı veri çekirdeği üzerinde sıfır kod değişikliğiyle çalışır.
