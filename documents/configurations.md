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
| **`A`** | `yonned.com` | `185.205.194.232` (`node102`) | ☁️ Proxied | Ana portal ve web arayüzü (Port 8000) |
| **`A`** | `api.yonned.com` | `185.205.194.232` (`node102`) | ☁️ Proxied | Canlı FastAPI REST Servisi (Port 8000) |
| **`A`** | `ws.yonned.com` | `185.205.194.232` (`node102`) | ☁️ Proxied | Canlı WebSocket Akışı (Port 8000) |
| **`A`** | `staging.yonned.com` | `185.205.194.232` (`node102`) | ☁️ Proxied | Staging Web Arayüzü (Port 8001) |
| **`A`** | `staging-api.yonned.com` | `185.205.194.232` (`node102`) | ☁️ Proxied | Staging Test API Servisi (Port 8001) |
| **`A`** | `staging-ws.yonned.com` | `185.205.194.232` (`node102`) | ☁️ Proxied | Staging WebSocket Akışı (Port 8001) |
| **`CNAME`** | `www.yonned.com` | `yonned.com` | ☁️ Proxied | www ana domaine yönlendirme |

### 1.2. SSL / TLS Şifreleme Modu
* **SSL/TLS Encryption Mode:** **`Full`**
  * **İstemci ➔ Cloudflare (Edge):** Cloudflare otomatik olarak Google Trust Services / Let's Encrypt imzalı resmi evrensel sertifika sunar (Tarayıcılarda %100 geçerli yeşil kilit).
  * **Cloudflare ➔ node102 (Origin):** `node102` üzerinde üretilen **100 Yıllık (2126'ya kadar geçerli) 4096-bit RSA OpenSSL Sertifikası** (`/etc/ssl/certs/yonned.crt` ve `/etc/ssl/private/yonned.key`) kullanılır.
  * **Sıfır Bakım (Ömür Boyu):** Certbot yenileme hataları, 3 aylık süre dolmaları veya manuel sertifika taşıma zahmeti tamamen sıfırlanmıştır. Uçtan uca trafik kesintisiz şifrelenir.
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
* **Origin IP Maskeleme:** Gerçek sunucu IP'leri gizlenir. Dışarıdan gelen doğrudan IP taramaları Nginx seviyesinde reddedilir.

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

| Sunucu Adı | Genel IP | WireGuard Mesh IP | Donanım (vCPU / RAM / Disk / Port) | Rol ve Servisler | Durum |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **`node102`** | `185.205.194.232` | `10.10.0.2` | 3 vCPU / 9 GB RAM / 80 GB SSD / 10 Gbps | **Ana Hesaplama & Veri Düğümü (Compute & DB):**<br>• `yonned_prod` (Port 8000, PostgreSQL `yonned_prod_db`, Redis Port 6379)<br>• `yonned_staging` (Port 8001, PostgreSQL `yonned_staging_db`, Redis Port 6380)<br>• Nginx, CrowdSec, nftables, WireGuard | **Aktif (Çift Ortam)** |
| **`node104`** | `109.110.170.251` | `10.10.0.4` | 2 vCPU / 3 GB RAM / 10 GB OS + 1 TB HDD / 1 Gbps | **Medya Kasası (Storage Vault):**<br>• MinIO S3 (`/mnt/data/minio`) - Sadece `10.10.0.4:9000`<br>• IAM İzolasyonu: `yonned_prod` & `yonned_staging`<br>• Bucket: `yonned-prod-media` & `yonned-staging-media`<br>• Veritabanı Arşiv Yedekleri | **Aktif** |

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

* **Ters Vekil (Nginx - `node102`):** Port 80 (HTTP $\rightarrow$ HTTPS) ve Port 443 (HTTPS TLS 1.3).
* **Canlı API (yonned_prod):** `127.0.0.1:8000` (Nginx `api.yonned.com` ve `yonned.com` arkasında).
* **Staging API (yonned_staging):** `127.0.0.1:8001` (Nginx `staging-api.yonned.com` arkasında).
* **PostgreSQL 17 (`node102`):** `127.0.0.1:5432` (`yonned_prod_db` ve `yonned_staging_db`).
* **Redis Prod (`node102`):** `127.0.0.1:6379` (`yonned_prod_redis`).
* **Redis Staging (`node102`):** `127.0.0.1:6380` (`yonned_staging_redis`).
* **WireGuard Mesh (`node102` <-> `node104`):** UDP Port 51820 (Kernel-native şifreli özel ağ `10.10.0.0/24`).
* **MinIO S3 (`node104`):** `10.10.0.4:9000` (Genel internete TAMAMEN KAPALI; yalnızca WireGuard üzerinden `node102`'ye açık - `yonned-prod-media` & `yonned-staging-media`).

---

## 9. SYSTEMD SERVİS MİMARİSİ VE STANDART İSİMLENDİRME

Tüm servisler, API'ler ve arkaplan worker'ları doğrudan Linux `systemd` servisi olarak konuşlandırılmıştır:

### 9.1. Üretim Servisleri (`yonned_prod`)
| Servis Dosyası | Açıklama | Port / Süreç | Kaynak Limiti |
| :--- | :--- | :--- | :--- |
| **`yonned_prod_api.service`** | FastAPI ASGI Web & REST API | Port `8000` (4 Workers) | Sınırsız / Tam Kapasite |
| **`yonned_prod_critical_worker.service`** | Acil durum, SMS/OTP, kritik kuyruk | Async Python Worker | Öncelikli Süreç |
| **`yonned_prod_worker.service`** | Medya işleme, raporlama, arşiv | Async Python Worker | Standart Süreç |
| **`yonned_prod_redis.service`** | Canlı Cache & PubSub | Port `6379` | Sistem Varsayılanı |

### 9.2. Staging Servisleri (`yonned_staging`)
| Servis Dosyası | Açıklama | Port / Süreç | Kaynak Limiti |
| :--- | :--- | :--- | :--- |
| **`yonned_staging_api.service`** | Staging Test API Servisi | Port `8001` (2 Workers) | `MemoryMax=2G`, `CPUQuota=80%` |
| **`yonned_staging_critical_worker.service`** | Staging acil durum kuyruk testleri | Async Python Worker | `MemoryMax=1G`, `CPUQuota=50%` |
| **`yonned_staging_worker.service`** | Staging genel görev kuyruğu | Async Python Worker | `MemoryMax=1G`, `CPUQuota=50%` |
| **`yonned_staging_redis.service`** | Staging Cache & PubSub | Port `6380` | `maxmemory 512mb` |

* **Yönetim Komutları:**
  ```bash
  # Canlı servisleri yönet
  sudo systemctl restart yonned_prod_api yonned_prod_critical_worker yonned_prod_worker
  sudo systemctl status 'yonned_prod_*'

  # Staging servislerini yönet
  sudo systemctl restart yonned_staging_api yonned_staging_critical_worker yonned_staging_worker yonned_staging_redis
  sudo systemctl status 'yonned_staging_*'

  # Canlı log takibi
  sudo journalctl -u yonned_prod_api -f --no-pager
  sudo journalctl -u yonned_staging_api -f --no-pager
  ```

---

## 10. DOĞRULAMA VE SAĞLIK KONTROLLERİ (HEALTH CHECK)

* **Canlı ve Staging Sağlık Kontrolleri:**
  ```bash
  # Üretim Sağlık Ucu (Port 8000)
  curl -s http://127.0.0.1:8000/health
  # Çıktı: {"status":"healthy","service":"yonned-api","environment":"production","version":"1.0.0"}

  # Staging Sağlık Ucu (Port 8001)
  curl -s http://127.0.0.1:8001/health
  # Çıktı: {"status":"healthy","service":"yonned-api","environment":"staging","version":"1.0.0"}
  ```
* **Veritabanı İzolasyon Doğrulaması:**
  ```bash
  # Canlı DB kontrolü
  PGPASSWORD='yonned_secure_pwd_2026' psql -h 127.0.0.1 -U yonned_prod -d yonned_prod_db -c '\dt'

  # Staging DB kontrolü
  PGPASSWORD='yonned_staging_secret_2026' psql -h 127.0.0.1 -U yonned_staging -d yonned_staging_db -c '\dt'

  # İzolasyon testi: Staging kullanıcısı Canlı DB'ye ERİŞEMEZ (FATAL: permission denied)
  PGPASSWORD='yonned_staging_secret_2026' psql -h 127.0.0.1 -U yonned_staging -d yonned_prod_db -c '\conninfo'
  ```
* **Redis İzolasyon Doğrulaması:**
  ```bash
  # Üretim Redis (Port 6379)
  redis-cli -p 6379 ping  # PONG

  # Staging Redis (Port 6380)
  redis-cli -p 6380 ping  # PONG
  ```

---

## 11. WIREGUARD MESH AĞI VE MINIO S3 İZOLASYONU

### 11.1. Ağ Topolojisi ve Çekirdek Düzeyinde Şifreleme (Kernel-Native Overlay)
`node102` (Compute & DB) ile `node104` (Storage Vault) arasındaki tüm veri akışı, Linux çekirdeğinde yerel olarak koşan **WireGuard** (`wg0`) tüneli üzerinden ChaCha20-Poly1305 algoritmasıyla şifrelenir.

| Düğüm | Genel IP | WireGuard IP (`wg0`) | Dinleme Portu | Eşleşen Düğüm (Peer) |
| :--- | :---: | :---: | :---: | :--- |
| **`node102`** | `185.205.194.232` | `10.10.0.2/24` | UDP `51820` | `node104` (`109.110.170.251:51820`) |
| **`node104`** | `109.110.170.251` | `10.10.0.4/24` | UDP `51820` | `node102` (`185.205.194.232:51820`) |

* **Hizmet Yönetimi:**
  ```bash
  sudo systemctl enable --now wg-quick@wg0
  sudo wg show
  ```
* **Gecikme Süresi (Latency):** Tünel üzerinden RTT ortalama `4.4 ms`, paket kaybı `%0`.

### 11.2. MinIO S3 İnternet İzolasyonu (Port Shielding)
MinIO servisi genel internete (`0.0.0.0`) **asla bağlanmaz**.
* `/etc/minio/minio.conf` dosyasında dinleme adresi doğrudan WireGuard IP'sine bağlanmıştır:
  ```bash
  MINIO_OPTS="--address 10.10.0.4:9000 --console-address 10.10.0.4:9001"
  ```
* **Dış Dünya Testi:** Genel IP üzerinden `http://109.110.170.251:9000` adresine gelen bağlantılar işletim sistemi çekirdeğince anında reddedilir (`Connection refused`).
* **Önyükleme Güvencesi:** `/etc/sysctl.d/99-minio.conf` dosyasına `net.ipv4.ip_nonlocal_bind=1` eklenerek servislerin açılış sırasından bağımsız olarak güvenle başlaması sağlanmıştır.

### 11.3. MinIO IAM Kullanıcı ve Bucket İzolasyonu
Üretim ve Staging ortamları için MinIO Client (`mc`) ile ayrı IAM kullanıcıları ve en az yetki (Least Privilege) ilkeli IAM politikaları oluşturulmuştur:

| Ortam | IAM Kullanıcısı | Erişim Yetkisi Verilen Bucket | Politika Adı |
| :--- | :--- | :--- | :--- |
| **Üretim (`yonned_prod`)** | `yonned_prod` | `yonned-prod-media` & `yonned-prod-media/*` | `yonned-prod-policy` |
| **Staging (`yonned_staging`)** | `yonned_staging` | `yonned-staging-media` & `yonned-staging-media/*` | `yonned-staging-policy` |

* **Politika Şablonu (Örnek: `yonned-prod-policy`):**
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetBucketLocation",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads"
        ],
        "Resource": ["arn:aws:s3:::yonned-prod-media"]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:AbortMultipartUpload",
          "s3:DeleteObject",
          "s3:GetObject",
          "s3:ListMultipartUploadParts",
          "s3:PutObject"
        ],
        "Resource": ["arn:aws:s3:::yonned-prod-media/*"]
      }
    ]
  }
  ```

### 11.4. Çapraz Erişim İzolasyon Testi (Doğrulandı)
* `yonned_prod` kullanıcısının `yonned-staging-media` bucket'ına erişimi: `AccessDenied` (%100 Engellendi).
* `yonned_staging` kullanıcısının `yonned-prod-media` bucket'ına erişimi: `AccessDenied` (%100 Engellendi).
* `node102` API üzerinden Python `minio` istemcisi ile yükleme, sağlama ve silme işlemleri tünel üzerinden başarıyla test edilmiş ve onaylanmıştır.



