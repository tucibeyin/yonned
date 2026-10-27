# Yonned Donanım ve Altyapı Düğümleri (Infrastructure Nodes)
**Son Güncelleme:** 28 Ekim 2026  
**İşletim Sistemi:** Debian GNU/Linux 13 (Trixie) - x86_64 Kernel 6.12  
**Konum:** Amsterdam, Kuzey Hollanda (DeluxHost)  
**Erişim:** SSH anahtarı ile doğrudan (`ssh node101` .. `ssh node105`)

---

## 1. Düğüm Envanteri ve Özellikler

| Düğüm | IP Adresi | vCPU | RAM | Disk / Mount | Ağ Portu | Birincil Rol / Öneri |
| :--- | :--- | :---: | :---: | :--- | :---: | :--- |
| **`node101`** | `185.205.194.232` | 2 | 8 GB | 80 GB Hızlı SSD (`/`) | 10 Gbps | **Compute 1:** Master DB / API Gateway / Reverse Proxy |
| **`node102`** | `185.205.194.173` | 3 | 9 GB | 80 GB Hızlı SSD (`/`) | 10 Gbps | **Compute 2:** Uygulama Sunucusu (API / Web Admin / Worker) |
| **`node103`** | `185.205.194.236` | 3 | 8 GB | 80 GB Hızlı SSD (`/`) | 10 Gbps | **Compute 3:** DB Replika / Redis Cache / WebSocket Sunucusu |
| **`node104`** | `82.39.86.94` | 2 | 3 GB | 10 GB OS + **1 TB HDD** (`/mnt/data`) | 1 Gbps | **Storage 1:** S3 Medya Depolama (MinIO / Fotoğraflar) + Yedek |
| **`node105`** | `96.62.250.101` | 2 | 3 GB | 10 GB OS + **1 TB HDD** (`/mnt/data`) | 1 Gbps | **Storage 2:** Medya Replikasyonu (MinIO Cluster) + Soğuk Yedek |

### Toplam Altyapı Kapasitesi:
* **İşlem Gücü:** 12 vCPU
* **Toplam Bellek (RAM):** ~31 GB RAM
* **Hızlı SSD Depolama (Compute için):** ~240 GB SSD (NVMe hızında)
* **Büyük Veri Depolama (Medya/Yedek için):** **2 TB HDD** (`/mnt/data`)

---

## 2. Mimari Dağıtım ve Rol Planı

Bu 5 düğüm, projenin büyüklüğü için adeta biçilmiş kaftandır. Donanım profilleri ikiye ayrılmaktadır:

### A. Hesaplama ve Veritabanı Kümesi (Compute Cluster: `node101`, `node102`, `node103`)
* **Hızlı SSD ve Yüksek RAM (Toplam 25 GB RAM, 10 Gbps Ağ):**
  * `node101` + `node102` + `node103` arasında Docker Swarm veya hafif k3s (Kubernetes) / doğrudan Docker Compose kümesi kurulabilir.
  * **Veritabanı:** PostgreSQL (Hızlı SSD üzerinde, yüksek I/O performansı).
  * **Önbellek & Canlı Takip:** Redis (Gerçek zamanlı müşteri takibi ve WebSocket bildirimleri).
  * **Uygulamalar:** API backend ve Web Admin paneli.

### B. Medya, Fotoğraf ve Yedekleme Kümesi (Storage Cluster: `node104`, `node105`)
* **2 TB Büyük Depolama Alanı (`/mnt/data`):**
  * Operatörlerin çektiği ameliyat, tıraş, araç hasar ve bakım fotoğrafları, hasta kabul evrakları.
  * S3 uyumlu bir nesne depolama motoru (örn. **MinIO** veya **SeaweedFS**) çalıştırılarak AWS S3 maliyeti ödemeden kendi bağımsız fotoğraf/medya sunucumuz kurulabilir.
  * `node104` ve `node105` birbirine replike olarak çalışır (1 TB + 1 TB ayna/yedek).
  * Veritabanının saatlik ve günlük şifreli yedekleri buraya arşivlenir.
