# Yonned İşletim Sistemi ve Altyapı Konfigürasyon Şartnamesi (OS Configuration Spec)
**Belge Türü:** Sistem ve Sunucu Konfigürasyon Kaydı (OS & Infrastructure Configuration SSOT)  
**Tarih:** 28 Ekim 2026  
**Durum:** Uygulanmış ve Doğrulanmış Sistem Ayarları  
**İşletim Sistemi:** Debian GNU/Linux 13 (Trixie) - 64-bit (Kernel 6.12)  

---

## 1. SUNUCU TOPOLOJİSİ VE ROLLER

| Sunucu Adı | IP Adresi | Donanım (vCPU / RAM / Disk / Port) | Rol ve Servisler | Durum |
| :--- | :---: | :--- | :--- | :---: |
| **`node102`** | `185.205.194.173` | 3 vCPU / 9 GB RAM / 80 GB SSD / 10 Gbps | **Üretim (Production):** Compute, PostgreSQL 17, Redis 7, FastAPI, Nginx, CrowdSec | Aktif |
| **`node103`** | `185.205.194.236` | 3 vCPU / 8 GB RAM / 80 GB SSD / 10 Gbps | **Staging (Laboratuvar):** Tam bağımsız hepsi-bir-arada test ortamı (DB, Redis, API, Test Koşumu) | Aktif |
| **`node104`** | `82.39.86.94` | 2 vCPU / 3 GB RAM / 10 GB OS + 1 TB HDD / 1 Gbps | **Medya Deposu (Storage):** MinIO S3 Nesne Depolama (`/mnt/data`), Veritabanı Yedek Arşivi | Aktif |
| **`node101`** | `185.205.194.88` | 1 vCPU / 1 GB RAM / 20 GB SSD | Yedek / Boşta (Standby) | Boşta |
| **`node105`** | `185.205.194.144`| 3 vCPU / 8 GB RAM / 80 GB SSD | Yedek / Boşta (Standby) | Boşta |

---

## 2. KULLANICI, DİZİN VE ERİŞİM YETKİLERİ

* **Yönetici Kullanıcı:** `tucibeyin`
  * Tüm düğümlerde şifresiz `sudo` yetkisi yapılandırılmış ve doğrulanmıştır (`sudo whoami -> root`).
  * SSH erişimi yalnızca genel anahtar (Public Key) ile açıktır, parola ile girişler kapalıdır.
* **Proje Monorepo Dizin Standardı:**
  * Kök Dizin: `/var/www/yonned.com/`
  * Dizin Sahipliği: `tucibeyin:tucibeyin`
  * Dizin İzinleri: `drwxr-xr-x (755)`
  * Uygulama Komutu:
    ```bash
    sudo mkdir -p /var/www/yonned.com
    sudo chown -R tucibeyin:tucibeyin /var/www/yonned.com
    sudo chmod 755 /var/www/yonned.com
    ```

---

## 3. ZAMAN DİLİMİ VE SAAT SENKRONİZASYONU (TIMEZONE & NTP)

Veritabanı zaman damgalarında, loglarda ve WebSocket canlı takip akışlarında zaman kaymalarını sıfırlamak için tüm sunucular standart **UTC** zaman dilimine sabitlenmiştir:

```bash
sudo timedatectl set-timezone UTC
sudo timedatectl set-ntp true
```
* **Doğrulama Çıktısı:**
  * `Time zone: Etc/UTC (UTC, +0000)`
  * `System clock synchronized: yes`
  * `NTP service: active`

---

## 4. ÇEKİRDEK VE AĞ OPTİMİZASYONU (SYSCTL)

10 Gbps yüksek bant genişliği, on binlerce eşzamanlı WebSocket bağlantısı ve Redis arkaplan kayıt (bgsave) operasyonları için `/etc/sysctl.d/99-yonned.conf` dosyası tüm aktif sunucularda yapılandırılmıştır:

```ini
# /etc/sysctl.d/99-yonned.conf

# 1. Redis Arkaplan Kayıt ve Bellek Aşımı
vm.overcommit_memory = 1
vm.swappiness = 10

# 2. Yüksek Eşzamanlılık ve Soket Kuyruk Limitleri (10 Gbps)
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.core.netdev_max_backlog = 10000

# 3. Dosya Tanımlayıcı ve İzleyici Sayıları
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 1024

# 4. TCP Hızlı Geri Kazanım ve Canlı Tutma (Keepalive)
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_intvl = 15
net.ipv4.tcp_keepalive_probes = 5
```

* **Yürürlüğe Koyma:**
  ```bash
  sudo sysctl -p /etc/sysctl.d/99-yonned.conf
  ```

---

## 5. DOSYA VE SOKET SINIRLARI (ULIMITS)

İşletim sisteminin varsayılan 1024 dosya sınırı yüksek eşzamanlı soket isteklerini engellememesi için `/etc/security/limits.d/99-yonned.conf` dosyasında 65.535'e yükseltilmiştir:

```text
# /etc/security/limits.d/99-yonned.conf
* soft nofile 65535
* hard nofile 65535
root soft nofile 65535
root hard nofile 65535
tucibeyin soft nofile 65535
tucibeyin hard nofile 65535
```

---

## 6. TEMEL SİSTEM PAKETLERİ (DEBIAN 13 / TRIXIE)

Sunucularda derleme, Python sanal ortamı ve veritabanı sürücüleri için gerekli asgari native paketler:

```bash
sudo DEBIAN_FRONTEND=noninteractive apt update && sudo apt install -y \
    curl \
    wget \
    git \
    htop \
    jq \
    unzip \
    build-essential \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    libpq-dev \
    procps \
    nftables
```

---

## 7. SERVİS PORT VE GÜVENLİK DAĞILIMI

* **Ters Vekil (Nginx):** Port 80 (HTTP $\rightarrow$ HTTPS) ve Port 443 (HTTPS TLS 1.3).
* **Uvicorn / FastAPI:** Yalnızca `127.0.0.1:8000` (Dışarıya tamamen kapalı).
* **PostgreSQL 17:** Yalnızca `127.0.0.1:5432` (Dışarıya tamamen kapalı).
* **Redis 7:** Yalnızca `127.0.0.1:6379` (Dışarıya tamamen kapalı).
* **MinIO S3 (`node104`):** Port 9000 (Sadece yetkili API IP'lerine açık).
