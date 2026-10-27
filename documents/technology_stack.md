# Yonned Teknoloji Yığını Şartnamesi (V1.0)
**Tarih:** 28 Ekim 2026  
**Durum:** Kesinleşti  
**Temel Felsefe:** *Python (FastAPI), Flutter (Cross-Platform Mobile), Saf HTML/CSS (Hafif Web), PostgreSQL + Redis, Sıfır-Docker (Native systemd), %100 Ücretsiz*

---

## 1. Mimari Seçimler ve Temel Felsefe

Gereksiz katmanlar, ağır derleyiciler ve Docker sanallaştırma yükü tamamen kaldırılmıştır. Sistem doğrudan Debian 13 üzerinde yerel Linux servisleri (`systemd`) olarak çalışır.

### Temel Prensipler:
1. **Bakımı En Kolay Backend:** Python (FastAPI). Temiz, okunabilir, asenkron ve otomatik Swagger API dokümantasyonuna sahip.
2. **Kusursuz Mobil Deneyim:** Flutter. Tek kod tabanı ile hem iOS hem Android'de 60/120 FPS akıcı kamera ve barkod tarama.
3. **Sıfır Derleme Yüklü Web:** Saf HTML5, Vanilla CSS ve modern JavaScript. `node_modules` karmaşası olmadan mikrosaniyeler içinde açılan sayfalar.
4. **Yerel Veri ve Önbellek:** PostgreSQL 17 (İlişkisel Veri) + Redis (Canlı Takip ve Pub/Sub).
5. **Git-Native Dağıtım:** Local makinede geliştir $\rightarrow$ `git push` $\rightarrow$ `node102`de `git pull && systemctl restart yonned` $\rightarrow$ Anında canlıda!

---

## 2. Teknoloji Katmanları Tablosu

| Katman | Teknoloji | Konum / Çalışma Şekli | Görevi / Neden Seçildi? |
| :--- | :--- | :--- | :--- |
| **Mobil Uygulama** | **Flutter (Dart)** | iOS & Android | Saha personeli için akıcı kamera, QR & barkod okuma (`mobile_scanner`). |
| **Backend API** | **Python (FastAPI)** | `node102` (systemd / Uvicorn) | Asenkron REST API, WebSocket, otomatik `/docs` Swagger üretimi. |
| **Veritabanı** | **PostgreSQL 17** | `node102` (Native Debian paketi) | JSONB, recursive hiyerarşi ve tüm ilişkisel operasyonlar. |
| **Önbellek & Soket**| **Redis** | `node102` (Native Debian paketi) | Canlı müşteri takip akışı, oturum önbellekleme ve pub/sub. |
| **Web Admin & Tracker**| **HTML5 + Vanilla CSS + JS** | `node102` (Jinja2 / Caddy) | Sıfır build süresi, ultra hafif, lüks ve modern tasarım sistemi. |
| **Ters Vekil & SSL** | **Nginx + Certbot** | `node102` (systemd / apt) | Endüstri standardı ters vekil, CrowdSec ile %100 yerel log uyumu, otomatik Let's Encrypt SSL. |
| **Ağ & Host Güvenliği**| **CrowdSec + Firewall Bouncer** | `node102` & `node104` (systemd) | Kaba kuvvet saldırılarını, port taramalarını engeller; kötü IP'leri nftables ile banlar. |
| **Medya Depolama** | **MinIO (Tek Binary)**| `node104` (systemd / `/mnt/data`) | 1 TB disk üzerinde S3 uyumlu yerel fotoğraf/evrak deposu. |

---

## 3. Katman Detayları

### 3.1. Backend API: Python (FastAPI)
* **Konum:** `node102` (Dahili port: `127.0.0.1:8000`)
* **Servis:** `systemd` (`/etc/systemd/system/yonned-api.service`)
* **Önemli Kütüphaneler:**
  * `fastapi`: Modern, yüksek performanslı web çatısı.
  * `uvicorn[standard]`: Asenkron ASGI web sunucusu.
  * `sqlalchemy[asyncio]` + `asyncpg`: PostgreSQL için en sağlam asenkron ORM ve sürücü.
  * `pydantic-v2`: Işık hızında veri doğrulama ve serileştirme.
  * `redis-py`: Canlı soket iletişimi ve önbellek.
* **Otomatik API Dokümantasyonu:**
  * Kod yazıldığı an `https://api.yonned.com/docs` adresinde Swagger arayüzü hazırdır. Flutter mobil geliştirme yaparken API'yi test etmek son derece kolaylaşır.

### 3.2. Web Arayüzleri: Saf HTML + Vanilla CSS + Modern JS
* **Neden Frameworksüz?** Ağır Node.js bağımlılıkları (`npm/node_modules`) olmadan, sunucuyu yormayan, bakımı 10 yıl sonra bile kolay olan bir yapı.
* **İki Temel Ekran:**
  1. **`/admin` (Patron & Bayi Paneli):**  
     FastAPI Jinja2 şablonları veya statik HTML/JS ile sunulur. Bayi seçimi, canlı kafes doluluk haritası, süreç tanımlama sihirbazı.
  2. **`/t/:token` (Müşteri Canlı Takip Sayfası):**  
     Müşteriye SMS/WhatsApp ile giden link. Mobil tarayıcıda açılır açılmaz WebSocket ile bağlanır; hekim ameliyatta dikiş attığı veya mama verdiği an ekranda canlı yeşil tik yanar ve fotoğraf görünür.
* **Görsel Tasarım (CSS):**
  * Modern koyu/açık tema (Dark/Light mode).
  * Cam efekti (Glassmorphism), temiz kartlar ve Google Fonts (`Outfit` / `Inter`).

### 3.3. Mobil Saha Uygulaması: Flutter
* **Kullanıcı:** Veteriner hekim, teknisyen, çırak, kuaför, oto yıkama ustası.
* **Temel Yetenekler:**
  * **Evrensel Tarayıcı (Universal Scanner):** `mobile_scanner` paketi ile kamerayı açar açmaz mekan QR'ı, hasta QR'ı veya ilaç barkodu tek vizörde çözülür.
  * **Hızlı Aksiyon Butonları:** Tek elle kullanım için tasarlanmış büyük, akıcı butonlar (`[Başlat]`, `[Tamamla]`, `[İlaç Okut]`, `[Fotoğraf Çek]`).
  * **Çevrimdışı Dayanıklılık (Offline-Friendly):** İnternet anlık kopsa bile veriyi yerel SQLite/Hive içinde saklayıp bağlantı gelince sunucuya iletir.

### 3.4. Altyapı ve Sunucu Yönetimi (Debian 13 Native)
* **`node102` (Compute & DB):**
  * PostgreSQL 17: `systemctl status postgresql`
  * Redis: `systemctl status redis`
  * Yonned API: `systemctl status yonned-api`
  * Caddy: `systemctl status caddy`
* **`node104` (Media Storage):**
  * MinIO: `systemctl status minio` (`/mnt/data` 1 TB HDD'ye bağlı)

---

## 4. Proje Dizin Yapısı (Temiz ve Modüler)

```
yonned/
├── backend/                 # Python FastAPI Uygulaması
│   ├── app/
│   │   ├── api/             # API Router'ları (auth, assets, processes, scanner)
│   │   ├── core/            # Config, güvenlik, database bağlantıları
│   │   ├── models/          # SQLAlchemy Veritabanı Modelleri
│   │   ├── schemas/         # Pydantic Şemaları
│   │   └── services/        # İş Mantığı (Logic)
│   ├── main.py              # Uygulama Giriş Noktası
│   └── requirements.txt     # Python Bağımlılıkları
│
├── frontend/                # Web Admin & Müşteri Tracker (HTML/CSS/JS)
│   ├── static/              # CSS, JS, Logolar, İkonlar
│   │   ├── css/style.css    # Premium Vanilla CSS Tasarım Sistemi
│   │   └── js/app.js        # WebSocket & API İletişim Kodları
│   └── templates/           # Jinja2 HTML Şablonları (admin, tracker)
│
├── mobile/                  # Flutter Mobil Uygulaması
│   ├── lib/
│   │   ├── screens/         # Tarayıcı, Süreç Kartı, İstasyon Ekranı
│   │   ├── services/        # API ve WebSocket İstemcisi
│   │   └── main.dart        # Flutter Giriş Noktası
│   └── pubspec.yaml         # Flutter Bağımlılıkları
│
├── deploy/                  # Linux systemd ve Caddy Konfigürasyonları
│   ├── yonned-api.service   # systemd servis dosyası
│   └── Caddyfile            # Caddy ters vekil ve SSL ayarları
│
└── documents/               # Mimari ve Tasarım Şartnameleri
```

---

## 5. Canlıya Alma ve Güncelleme (Git Push ➔ Pull)

1. **Local'de Geliştir:** Kod yazılır ve test edilir.
2. **Push:**
   ```bash
   git add .
   git commit -m "feat: add process engine and universal scanner"
   git push origin main
   ```
3. **Sunucuda Güncelle (`node102` üzerinde):**
   ```bash
   cd /var/www/yonned
   git pull origin main
   source venv/bin/activate
   pip install -r backend/requirements.txt
   alembic upgrade head
   sudo systemctl restart yonned-api
   ```
   *Hiçbir Docker katmanı olmadan 5 saniyede canlıda!*
