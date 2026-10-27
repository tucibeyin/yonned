# Yonned Donanım ve Altyapı Düğümleri (Infrastructure Nodes)
**Son Güncelleme:** 28 Ekim 2026  
**İşletim Sistemi:** Debian GNU/Linux 13 (Trixie) - x86_64 Kernel 6.12  
**Konum:** Amsterdam, Kuzey Hollanda (DeluxHost)  
**Erişim:** SSH anahtarı ile doğrudan (`ssh node101` .. `ssh node105`)

---

## 1. Aktif V1.0 Üretim Mimarisi (2-Düğümlü Odaklı Model)

Sistemin ilk fazında kaynak israfını önlemek, operasyonel karmaşıklığı sıfıra indirmek ve diğer sunucuları serbest bırakmak amacıyla **2 Düğümlü Mimari (Node102 + Node104)** seçilmiştir.

En yüksek RAM kapasitesine sahip olan **`node102`** tüm hesaplama ve veritabanı yükünü üstlenirken, 1 TB depolamalı **`node104`** medya ve nesne depolama sunucusu olarak görev yapar.

```
┌────────────────────────────────────────────────────────┐       ┌────────────────────────────────────────────────────────┐
│               NODE102 (COMPUTE & DATABASE)             │       │               NODE104 (OBJECT STORAGE)                 │
├────────────────────────────────────────────────────────┤       ├────────────────────────────────────────────────────────┤
│  IP: 185.205.194.173  |  3 vCPU  |  9 GB RAM           │       │  IP: 82.39.86.94  |  2 vCPU  |  3 GB RAM               │
│  Disk: 80 GB Hızlı SSD  |  Port: 10 Gbps               │       │  Disk: 10 GB OS + 1 TB HDD (/mnt/data)  |  Port: 1 Gbps│
├────────────────────────────────────────────────────────┤       ├────────────────────────────────────────────────────────┤
│  • Caddy / Reverse Proxy (Otomatik SSL / Port 80, 443) │       │  • MinIO / S3 Object Storage Service                   │
│  • PostgreSQL 17 (İlişkisel Veritabanı)                 │       │    (Fotoğraflar, ameliyat kayıtları, hasta evrakları)  │
│  • Redis (Canlı Takip, WebSocket Pub/Sub & Önbellek)   │◄─────►│  • Otomatik Veritabanı Yedekleme Arşivi                │
│  • Yonned Core API (Fastify / TypeScript)              │ (Özel │    (Günlük/Haftalık şifreli DB dump arşivi)            │
│  • Yonned Web Admin & Tracker (Next.js SSR/Static)     │  Ağ)  │                                                        │
└────────────────────────────────────────────────────────┘       └────────────────────────────────────────────────────────┘
```

### Kaynak Tüketim Analizi (Neden Bu İkili Fazlasıyla Yeterli?):

#### `node102` (Hesaplama & Veri Yükü):
* **Kullanılabilir Bellek:** ~8.7 GB RAM
* **Servis Dağılımı:**
  * PostgreSQL 17: ~1.5 GB
  * Redis: ~300 MB
  * API Sunucusu: ~500 MB
  * Web Admin & Tracker: ~500 MB
  * Caddy (Proxy & SSL): ~50 MB
* **Toplam Yük:** **~2.85 GB** (Mevcut RAM'in sadece %33'ü!)
* **Kalan Güç:** ~5.8 GB boş RAM işletim sistemi disk önbelleği ve anlık yük dalgalanmaları için güvencedir.

#### `node104` (Medya & Depolama Yükü):
* **Kullanılabilir Bellek:** ~2.9 GB RAM
* **Depolama:** `/mnt/data` üzerinde **1.000 GB (1 TB)** HDD.
* **Servis:** MinIO (~400 MB RAM harcar).
* **Kapasite:** Ortalama 1 MB büyüklüğünde **1.000.000 adet görseli** dışarıya bağımlı olmadan sıfır maliyetle depolar.

---

## 2. Genel Düğüm Envanteri (Mevcut Altyapı)

| Düğüm | IP Adresi | vCPU | RAM | Disk / Mount | Ağ Portu | V1.0 Rolü |
| :--- | :--- | :---: | :---: | :--- | :---: | :--- |
| **`node102`** | `185.205.194.173` | **3** | **9 GB** | **80 GB SSD** (`/`) | **10 Gbps** | 🟢 **AKTİF COMPUTE:** DB, Redis, API, Web Admin, Proxy |
| **`node104`** | `82.39.86.94` | **2** | **3 GB** | **1 TB HDD** (`/mnt/data`) | **1 Gbps** | 🟢 **AKTİF STORAGE:** MinIO S3 Medya Deposu + Yedek |
| `node101` | `185.205.194.232` | 2 | 8 GB | 80 GB SSD (`/`) | 10 Gbps | ⚪ **SERBEST:** Diğer projeler / Gelecekte Compute 2 |
| `node103` | `185.205.194.236` | 3 | 8 GB | 80 GB SSD (`/`) | 10 Gbps | ⚪ **SERBEST:** Diğer projeler / Gelecekte DB Replika |
| `node105` | `96.62.250.101` | 2 | 3 GB | 1 TB HDD (`/mnt/data`) | 1 Gbps | ⚪ **SERBEST:** Diğer projeler / Gelecekte Storage 2 |

---

## 3. Gelecekte Yatay Büyüme (Scaling Plan)

Yarın platformdaki işletme ve canlı işlem hacmi 10 katına çıktığında:
1. `node101` veya `node103` havuza dahil edilerek PostgreSQL veritabanı ayrıştırılabilir.
2. `node105` MinIO kümesine eklenerek medya depolaması 2 TB çift taraflı aynaya (mirrored replication) dönüştürülebilir.
3. Uygulama kodunda tek bir satır bile değiştirmeden sadece Docker ortam değişkenleri güncellenerek bu geçiş yapılabilir.
