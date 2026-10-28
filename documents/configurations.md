# Yonned İşletim Sistemi ve Altyapı Konfigürasyon Şartnamesi (OS Configuration Spec)
**Belge Türü:** Sistem ve Sunucu Konfigürasyon Kaydı (OS & Infrastructure Configuration SSOT)  
**Tarih:** 28 Ekim 2026  
**Durum:** Uygulanmış ve Doğrulanmış Sistem Ayarları  
**İşletim Sistemi:** Debian GNU/Linux 13 (Trixie) - 64-bit (Kernel 6.12)  

---

## 1. DIŞ GİRİŞ KAPISI: CLOUDFLARE EDGE VE GÜVENLİK AYARLARI

Yonned dünyasının dış dünyaya açılan ilk ve tek giriş kapısı **Cloudflare Edge Katmanı**dır. İstemciler (mobil uygulama, admin paneli ve müşteri takipçisi) sunucu IP'lerine asla doğrudan ulaşamaz; tüm trafik Cloudflare üzerinden süzülerek gelir.

### 1.1. DNS Yapılandırması ve Yönlendirme Matrisi (Proxy Status: ☁️ Proxied)
Tüm kayıtlarda Cloudflare Proxy (Turuncu Bulut) **ZORUNLUDUR**:

| Kayıt Tipi | İsim / Host | Hedef / Değer | Proxy Durumu | Açıklama |
| :--- | :--- | :--- | :---: | :--- |
| **`A`** | `yonned.com` | `185.205.194.173` (`node102`) | ☁️ Proxied | Ana portal ve web arayüzü |
| **`A`** | `api.yonned.com` | `185.205.194.173` (`node102`) | ☁️ Proxied | Üretim FastAPI REST Servisi |
| **`A`** | `ws.yonned.com` | `185.205.194.173` (`node102`) | ☁️ Proxied | Canlı WebSocket Akışı |
| **`A`** | `staging.yonned.com` | `185.205.194.236` (`node103`) | ☁️ Proxied | Bağımsız Staging Web Arayüzü |
| **`A`** | `staging-api.yonned.com` | `185.205.194.236` (`node103`) | ☁️ Proxied | Staging Test API Servisi |
| **`CNAME`** | `www.yonned.com` | `yonned.com` | ☁️ Proxied | www ana domaine yönlendirme |

### 1.2. SSL / TLS Şifreleme Modu
* **SSL/TLS Encryption Mode:** **`Full (Strict)`**
  * Neden Full (Strict)? İstemci-Cloudflare arası değil, Cloudflare ile `node102`/`node103` arasındaki trafik de uçtan uca TLS ile şifrelenir (Man-in-the-Middle saldırısı imkansızlaşır).
* **Cloudflare Origin CA Sertifikası (15 Yıllık Kusursuz Çözüm):**
  * Let's Encrypt / Certbot 3 ayda bir yenilenme hatalarına ve cron arızalarına tabidir.
  * Bunun yerine Cloudflare Dashboard üzerinden üretilen **15 yıllık Origin CA Sertifikası** Nginx sunucusuna kurulur (`/etc/ssl/certs/yonned.origin.pem` ve `/etc/ssl/private/yonned.origin.key`).
* **Minimum TLS Sürümü:** `TLS 1.3` (Eski mobil cihaz fallback için: `TLS 1.2`).
* **Always Use HTTPS:** `ON` (Tüm HTTP istekleri anında HTTPS'e çevrilir).
* **Automatic HTTPS Rewrites:** `ON`.

### 1.3. Ağ ve WebSocket Ayarları (Network Tab)
* **WebSockets:** **`ON` (Aktif)**
  * Canlı müşteri takip sayfası (`/ws/tracker/{token}`) ve saha personeli anlık bildirimleri için kesintisiz çift yönlü TCP tüneli sağlar.
* **gRPC:** `ON` (İleride mobil RPC hızlandırması için).
* **HTTP/3 (with QUIC):** `ON` (Mobil ağlarda hızlı bağlantı kurma ve paket kaybında sıfır bekleme).

### 1.4. Güvenlik ve WAF Politikaları (Security Tab)
* **Security Level:** `Medium`
* **Bot Fight Mode:** `ON` (Otomatik kötü niyetli botları ve veri kazıyıcıları engeller).
* **DDoS Koruması:** Cloudflare Anycast altyapısı L3/L4 ve L7 saldırılarını otomatik emer.
* **Origin IP Maskeleme:** Gerçek sunucu IP'leri (`185.205.194.173` ve `185.205.194.236`) gizlenir. Dışarıdan gelen doğrudan IP taramaları Nginx seviyesinde reddedilir.

### 1.5. Nginx Tarafında Cloudflare Gerçek IP Çözümleme (Real IP Restoration)
Cloudflare vekil görevi gördüğü için Nginx loglarında ve CrowdSec'te müşterinin gerçek IP'sini (`CF-Connecting-IP`) görebilmek için `/etc/nginx/conf.d/cloudflare-real-ip.conf` yapılandırması kullanılır:
```nginx
# Cloudflare Resmi IPv4 Blokları
set_real_ip_from 173.245.48.0/20;
set_real_ip_from 103.21.244.0/22;
set_real_ip_from 103.22.200.0/22;
set_real_ip_from 103.31.4.0/22;
set_real_ip_from 141.101.64.0/18;
set_real_ip_from 108.162.192.0/18;
set_real_ip_from 190.93.240.0/20;
set_real_ip_from 188.114.96.0/20;
set_real_ip_from 197.234.240.0/22;
set_real_ip_from 198.41.128.0/17;
set_real_ip_from 162.158.0.0/15;
set_real_ip_from 104.16.0.0/13;
set_real_ip_from 104.24.0.0/14;
set_real_ip_from 172.64.0.0/13;
set_real_ip_from 131.0.72.0/22;

real_ip_header CF-Connecting-IP;
```

---

## 2. SUNUCU TOPOLOJİSİ VE ROLLER

| Sunucu Adı | IP Adresi | Donanım (vCPU / RAM / Disk / Port) | Rol ve Servisler | Durum |
| :--- | :---: | :--- | :--- | :---: |
| **`node102`** | `185.205.194.173` | 3 vCPU / 9 GB RAM / 80 GB SSD / 10 Gbps | **Üretim (Production):** Compute, PostgreSQL 17, Redis 7, FastAPI, Nginx, CrowdSec | Aktif |
| **`node103`** | `185.205.194.236` | 3 vCPU / 8 GB RAM / 80 GB SSD / 10 Gbps | **Staging (Laboratuvar):** Tam bağımsız hepsi-bir-arada test ortamı (DB, Redis, API, Test Koşumu) | Aktif |
| **`node104`** | `82.39.86.94` | 2 vCPU / 3 GB RAM / 10 GB OS + 1 TB HDD / 1 Gbps | **Medya Deposu (Storage):** MinIO S3 Nesne Depolama (`/mnt/data`), Veritabanı Yedek Arşivi | Aktif |

---

## 3. KULLANICI, DİZİN VE ERİŞİM YETKİLERİ

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

## 4. ZAMAN DİLİMİ VE SAAT SENKRONİZASYONU (TIMEZONE & NTP)

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

## 5. ÇEKİRDEK VE AĞ OPTİMİZASYONU (SYSCTL)

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

## 6. DOSYA VE SOKET SINIRLARI (ULIMITS)

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

## 7. TEMEL SİSTEM PAKETLERİ (DEBIAN 13 / TRIXIE)

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

## 8. SERVİS PORT VE GÜVENLİK DAĞILIMI

* **Ters Vekil (Nginx):** Port 80 (HTTP $\rightarrow$ HTTPS) ve Port 443 (HTTPS TLS 1.3).
* **Uvicorn / FastAPI:** Yalnızca `127.0.0.1:8000` (Dışarıya tamamen kapalı).
* **PostgreSQL 17:** Yalnızca `127.0.0.1:5432` (Dışarıya tamamen kapalı).
* **Redis 7:** Yalnızca `127.0.0.1:6379` (Dışarıya tamamen kapalı).
* **MinIO S3 (`node104`):** Port 9000 (Sadece yetkili API IP'lerine açık).

---

## 9. SYSTEMD SERVİS MİMARİSİ VE UVICORN YÖNETİMİ

Yonned API servisi, container soyutlamaları olmadan doğrudan Linux `systemd` servisi olarak `/etc/systemd/system/yonned-api.service` dosyasında tanımlanmıştır:

```ini
[Unit]
Description=Yonned Backend FastAPI ASGI Service
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=tucibeyin
Group=tucibeyin
WorkingDirectory=/var/www/yonned.com/backend
EnvironmentFile=/var/www/yonned.com/backend/.env
ExecStart=/var/www/yonned.com/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5s
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

* **Yönetim Komutları:**
  ```bash
  # Servisi başlat / durdur / yeniden başlat
  sudo systemctl daemon-reload
  sudo systemctl enable --now yonned-api
  sudo systemctl restart yonned-api
  sudo systemctl status yonned-api

  # Canlı log akışını izle
  sudo journalctl -u yonned-api -f --no-pager
  ```

---

## 10. DOĞRULAMA VE SAĞLIK KONTROLLERİ (HEALTH CHECK)

* **Yerel Sağlık Kontrolü:**
  ```bash
  curl -s http://127.0.0.1:8000/health
  # Yanıt: {"status":"healthy","service":"yonned-api","environment":"production","version":"1.0.0"}
  ```
* **Veritabanı ve Redis Durum Teyidi:**
  ```bash
  PGPASSWORD='yonned_secure_pwd_2026' psql -h 127.0.0.1 -U yonned -d yonned_db -c '\dt'
  redis-cli ping
  ```


