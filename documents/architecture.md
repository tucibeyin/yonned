# Yonned Sistem ve Ağ Mimarisi Şartnamesi (V1.0)
**Tarih:** 28 Ekim 2026  
**Durum:** Kesinleşti  
**Temel Felsefe:** *Çok Katmanlı Güvenlik (Defense-in-Depth), CrowdSec Savunması, Bare-Metal Performansı ve Düşük Gecikmeli Ağ*

---

## 1. Uçtan Uca Sistem ve Ağ Mimarisi

Sistem; dış dünyadaki istemcilerden (Mobil, Web, Müşteri) veritabanına ve medya deposuna kadar katmanlı bir ağ topolojisi üzerinde çalışır:

```
[ İSTEMCİLER / SAHA ]
  ├── 📱 Mobil Uygulama (Flutter - Saha Personeli)
  ├── 💻 Web Admin Paneli (Patron & Yöneticiler)
  └── 🌐 Canlı Müşteri Tracker (SMS/WhatsApp Linki - Tarayıcı)
              │
              ▼ HTTPS (Port 443)
┌────────────────────────────────────────────────────────────────────────┐
│  KATMAN 1: CLOUDFLARE (Edge / CDN / DNS)                               │
│  • Global Anycast DNS                                                  │
│  • Temel DDoS Koruması & Bot Yönetimi                                  │
│  • Full (Strict) SSL Termination                                       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼ Şifreli Trafik
┌────────────────────────────────────────────────────────────────────────┐
│  KATMAN 2: NODE102 (Compute & Core Application)                        │
│                                                                        │
│  🛡️ CROWDSEC SAVUNMA KATMANI:                                          │
│  ├── CrowdSec Agent: SSH ve Caddy loglarını gerçek zamanlı analiz eder.│
│  └── Firewall Bouncer (nftables): Saldırgan IP'leri kapıda banlar.     │
│                                                                        │
│  🌐 TERS VEKİL & SSL (Caddy Server - Port 80, 443):                    │
│  ├── Let's Encrypt / Cloudflare SSL Yönetimi                           │
│  ├── /admin & /t/* ➔ Statik Dosyalar / Jinja2 Şablonları              │
│  ├── /api/*        ➔ FastAPI Backend (127.0.0.1:8000)                  │
│  └── /ws           ➔ WebSocket Canlı Takip Akışı                       │
│                                                                        │
│  ⚙️ UYGULAMA MOTORU (systemd):                                         │
│  ├── Yonned FastAPI Backend (Python Uvicorn Async Workers)             │
│  ├── Redis 7 (Canlı Soket Mesajlaşması, Pub/Sub ve Önbellek)           │
│  └── PostgreSQL 17 (İlişkisel Veritabanı - NVMe SSD)                   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼ Özel / Şifreli İletişim (Port 9000)
┌────────────────────────────────────────────────────────────────────────┐
│  KATMAN 3: NODE104 (Object Storage & Backup Vault)                     │
│                                                                        │
│  🛡️ CROWDSEC (Sadece SSH ve Port 9000 Koruması)                        │
│                                                                        │
│  📦 MinIO S3 Object Storage (/mnt/data - 1 TB HDD):                    │
│  ├── Operatörlerin çektiği ameliyat, tıraş, hasar fotoğrafları         │
│  ├── Hasta evrakları, tahlil PDF'leri                                  │
│  └── node102 Veritabanı Yedekleri (Günlük şifreli arşiv)               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ağ Güvenliği ve CrowdSec Mimarisi

Sistemde güvenliği tek bir noktaya bırakmayan **Çok Katmanlı Savunma (Defense-in-Depth)** uygulanır:

### 2.1. CrowdSec Nasıl Çalışır?
* **Konum:** Hem `node102` hem `node104` üzerinde yerel Linux servisi (`systemd`).
* **Çalışma Prensibi:**
  1. **Log İzleme:** `/var/log/auth.log` (SSH) ve Caddy HTTP erişim loglarını saniye saniye okur.
  2. **Senaryo Tespiti:** 
     * SSH kaba kuvvet (brute-force) denemeleri,
     * API uç noktalarını tarayan web crawler ve botlar,
     * SQL Enjeksiyonu ve XSS taramaları.
  3. **Anında Cezalandırma (Bouncer):**  
     `crowdsec-firewall-bouncer-nftables` paketi Linux çekirdeği düzeyinde (Kernel firewall) saldırgan IP'yi anında banlar. Paket sunucuya hiç giremez!
  4. **Kolektif İstihbarat (Community Blocklist):**  
     Dünyada başka bir CrowdSec kullanıcısına saldırmış olan kötü niyetli IP'ler önceden listeye alınır ve bizim sunucumuza hiç yaklaşamaz.

### 2.2. Port Güvenliği ve Erişim Tablosu
Sunucularda gereksiz hiçbir port dış dünyaya açık tutulmaz:

| Port | Protokol | Servis | Dış Dünyaya Açık mı? | Güvenlik Önlemi |
| :---: | :---: | :--- | :---: | :--- |
| **`22`** | TCP | SSH | Evet (Kısıtlı) | Yalnızca SSH Key ile giriş (Parola kapalı) + CrowdSec koruması |
| **`80`** | TCP | HTTP | Evet | Doğrudan HTTPS'e (443) yönlendirilir |
| **`443`**| TCP | HTTPS | Evet | Caddy + Cloudflare Proxy + WAF |
| **`8000`**| TCP| FastAPI | **HAYIR** | Sadece `127.0.0.1` (Caddy arkasında) |
| **`5432`**| TCP| PostgreSQL | **HAYIR** | Sadece `127.0.0.1` (Dışarıdan erişilemez) |
| **`6379`**| TCP| Redis | **HAYIR** | Sadece `127.0.0.1` (Dışarıdan erişilemez) |
| **`9000`**| TCP| MinIO S3 (`node104`)| İsteğe bağlı / Korumalı | Sadece `node102` IP'sine izin verilir veya Caddy arkasından imzalı URL ile sunulur |

---

## 3. Gerçek Zamanlı İletişim Mimarisi (Canlı Takip Akışı)

Müşterinin cep telefonundaki zaman tünelinin hekim işlem yaptığı anda **sayfayı yenilemeden** anında güncellenmesini sağlayan akış:

```
[ Saha Hekimi / Flutter ] 
       │ 
       ▼ 1. "Dikiş atıldı + Fotoğraf" (POST /api/processes/event)
[ FastAPI Backend ]
       │
       ├──► 2. PostgreSQL'e kaydeder (live_processes tablosu)
       ├──► 3. MinIO'ya fotoğrafı gönderir (node104)
       │
       ▼ 4. Redis Pub/Sub kanalına mesaj fırlatır: "session:xyz:update"
[ Redis ]
       │
       ▼ 5. Canlı dinleyen WebSocket bağlantısına iletir
[ FastAPI WebSocket Yöneticisi ]
       │
       ▼ 6. Açık soket üzerinden JSON basar
[ Müşteri Canlı Takip Ekranı (Web Browser) ] ➔ Ekranda yeşil tik yanar, fotoğraf belirir!
```

---

## 4. Servis Yönetimi ve Dayanıklılık (Linux systemd)

Tüm servisler işletim sisteminin yerel servis yöneticisi (`systemd`) ile çalıştırılır. Elektrik kesintisi veya sunucu yeniden başlamasında her şey otomatik olarak ayağa kalkar.

### `node102` Üzerindeki Servisler:
```bash
systemctl status postgresql    # Veritabanı
systemctl status redis         # Önbellek & Soket
systemctl status caddy         # Web Sunucusu & SSL
systemctl status crowdsec      # Güvenlik Ajanı
systemctl status yonned-api    # FastAPI Backend Servisi
```

### Örnek `yonned-api.service` Konfigürasyonu:
```ini
[Unit]
Description=Yonned FastAPI Core Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=yonned
WorkingDirectory=/var/www/yonned/backend
Environment="PATH=/var/www/yonned/backend/venv/bin"
ExecStart=/var/www/yonned/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

---

## 5. Dağıtım ve Yedekleme Mimarisi

### Otomatik Günlük Yedekleme (node102 ➔ node104):
1. Her gece saat 03:00'te `node102` üzerinde cron tetiklenir.
2. `pg_dump` ile veritabanı şifreli gzip dosyası haline getirilir.
3. SSH anahtarı ile doğrudan `node104`ün `/mnt/data/backups/` dizinine güvenle aktarılır.
4. Son 30 günün yedekleri saklanır, eskiler otomatik silinir.
