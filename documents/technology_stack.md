# Yonned Teknoloji Yığını ve Dağıtım Şartnamesi (V1.0)
**Tarih:** 28 Ekim 2026  
**Durum:** Kesinleşti  
**Temel Felsefe:** *%100 Ücretsiz & Açık Kaynak, Sıfır Docker (Bare-Metal Linux Performansı), TypeScript Monorepo, Doğrudan Git Tabanlı Dağıtım (Push ➔ Pull)*

---

## 1. Mimari Kararlar ve Seçim Gerekçeleri

### A. Neden "Docker'sız" (Bare-Metal Native Linux)?
1. **Maksimum Donanım Verimi:** Docker katmanı (bridge network, sanal dosya sistemi, container overhead) aradan çıkarıldığında; `node102` üzerindeki 9 GB RAM ve 3 vCPU doğrudan işletim sistemine (Debian 13) ve uygulamalara ayrılır.
2. **I/O Hızı:** PostgreSQL ve Node.js doğrudan Linux çekirdeği (kernel) üzerinden NVMe/SSD diske yazar. Veritabanı okuma/yazma performansı 2 ila 3 kat artar.
3. **Sıfır Operasyonel Baş Ağrısı:** Container çökmesi, Docker socket izinleri, sanal IP yönlendirmeleri ile uğraşılmaz. Süreç yönetimi Debian'ın yerel motoru (`systemd` veya `pm2`) ile yönetilir.
4. **Basit Dağıtım (Deployment):** Local'de kodlanır $\rightarrow$ `git push` $\rightarrow$ Sunucuda `git pull && pnpm build && pm2 restart` $\rightarrow$ **10 saniyede canlıda!**

---

## 2. Teknoloji Yığını Katmanları

```
┌────────────────────────────────────────────────────────────────────────┐
│                      YONNED MONOREPO (TypeScript)                      │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  [1. VERİTABANI & ORM]                                                 │
│  • PostgreSQL 17 (Debian 13 Native)                                    │
│  • Drizzle ORM (Hafif, tip güvenli, SQL'e birebir yakın)              │
│                                                                        │
│  [2. BACKEND API & WEBSOCKET]                                          │
│  • Node.js (v22 LTS) + Fastify                                         │
│  • @fastify/websocket (Canlı Müşteri Takip Akışı)                      │
│                                                                        │
│  [3. WEB ADMİN & MÜŞTERİ TRACKER]                                      │
│  • Next.js 15 (React 19, App Router)                                   │
│  • Vanilla CSS Tasarım Sistemi (Glassmorphism, Modern Tipografi)       │
│                                                                        │
│  [4. MOBİL UYGULAMA (Saha Çalışanı)]                                   │
│  • React Native + Expo (Kamera, QR, Barkod Vizörü)                    │
│                                                                        │
│  [5. REVERSE PROXY & SSL]                                              │
│  • Caddy Server (Otomatik Let's Encrypt SSL, HTTP/3, Cloudflare Uyumlu)│
│                                                                        │
│  [6. MEDYA & DEPOLAMA (Node104)]                                       │
│  • MinIO Server (Tek Binary, 1 TB HDD /mnt/data S3 Deposu)             │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Katman Detayları ve Kullanılacak Araçlar

### 3.1. Veritabanı: Yerel PostgreSQL 17 + Drizzle ORM
* **Konum:** `node102` (Yerel kurulum: `apt install postgresql-17`)
* **ORM:** **Drizzle ORM** (TypeScript)
  * **Neden Drizzle?** Prisma gibi arka planda ağır C++ binary'leri çalıştırmaz. Sadece TypeScript üretir; hafıza tüketimi sıfırdır.
  * SQL DDL şemamızdaki `persons`, `assets`, `live_processes` tabloları doğrudan TypeScript tiplerine dönüşür (`$inferSelect`, `$inferInsert`).
  * `drizzle-kit push` komutuyla şema değişiklikleri 1 saniyede veritabanına yansıtılır.

### 3.2. Backend API: Fastify + WebSocket
* **Konum:** `node102` (Port: `3001`)
* **Neden Fastify?**
  * Express'ten 2.5 kat daha hızlıdır, saniyede on binlerce isteği mikrosaniyeler içinde işler.
  * `@fastify/websocket` eklentisi ile tek çatı altında hem REST API hem canlı soket sunar.
  * Müşteri takip ekranı sokete bağlanır; sahada hekim "Mama verildi" dediği an müşterinin ekranındaki zaman tüneli yeşile döner.

### 3.3. Web Admin & Müşteri Takip Ekranı: Next.js + Vanilla CSS
* **Konum:** `node102` (Port: `3000`)
* **İki Temel Arayüz:**
  1. `/admin/*` $\rightarrow$ Patron & Bayi Yöneticisi Paneli (Kafes dolulukları, süreç legoları, çalışanlar, raporlar).
  2. `/t/:token` $\rightarrow$ Müşteri Canlı Takip Ekranı (Uygulamasız, şifresiz, mobil tarayıcıda açılan modern durum kartı).
* **CSS Felsefesi:** Vanilla CSS. Tailwind'in katı sınıfları yerine modern CSS değişkenleri (`--accent`, `--surface`), cam efekti (glassmorphism), karanlık/aydınlık mod ve Google Fonts (Outfit / Inter) ile lüks bir görünüm.

### 3.4. Mobil Uygulama: React Native (Expo)
* **Kullanıcı:** Saha Personeli (Veteriner, teknisyen, kuaför, oto yıkamacı, tamirci).
* **Neden Expo?**
  * %100 Ücretsiz ve açık kaynaklı. Tek kodla hem iOS hem Android çıktısı verir.
  * `expo-camera`: Tek bir vizörle hem QR kodları (`loc_`, `ast_`, `ses_`) hem de ilaç/parça EAN barkodlarını ışık hızında okur.
  * Backend ile aynı TypeScript tiplerini paylaşır.

### 3.5. Ters Vekil ve Güvenlik: Caddy + Cloudflare (Free)
* **Konum:** `node102` (Port `80`, `443`)
* **Neden Caddy?**
  * Nginx'teki gibi 100 satırlık karmaşık konfigürasyonlara gerek yoktur.
  * Let's Encrypt SSL sertifikasını tamamen otomatik üretir ve yeniler.
  * Cloudflare'in arkasında tam performansla çalışır (Cloudflare Proxy / Flexible / Full Strict SSL).

### 3.6. Medya ve Fotoğraf Depolama: MinIO (S3)
* **Konum:** `node104` (Port `9000`, Mount: `/mnt/data`)
* **Neden MinIO?**
  * Docker'a ihtiyaç duymaz; tek bir Linux binary dosyasıdır (`/usr/local/bin/minio`).
  * `systemd` servisi olarak ayağa kalkar, `node104`ün 1 TB'lık diskini AWS S3 uyumlu bir depoya dönüştürür.
  * Mobil uygulama çektiği yaralanma, ameliyat veya araç hasar fotoğraflarını doğrudan bu S3 servisine yükler.

---

## 4. Monorepo Dizin Yapısı (pnpm Workspaces)

Tek bir git deposu altında tüm sistemin hiyerarşisi:

```
yonned/
├── apps/
│   ├── api/                 # Fastify Backend REST & WebSocket (node102)
│   ├── web/                 # Next.js Web Admin & Müşteri Tracker (node102)
│   └── mobile/              # React Native Expo Saha Uygulaması
│
├── packages/
│   ├── db/                  # Drizzle ORM Şeması, Migration'lar ve DB Client
│   └── shared/              # Ortak TypeScript Tipleri, Sabitler, Enums
│
├── documents/               # Mimari, Donanım ve Veri Şartnameleri
│   ├── data_structures.md   # V1.0 Veri Yapıları Şartnamesi
│   ├── nodes.md             # Altyapı Düğümleri Envanteri (node102 & node104)
│   └── technology_stack.md  # Bu Belge
│
├── package.json             # pnpm workspace kök dosyası
└── pnpm-workspace.yaml
```

---

## 5. Canlıya Alma ve Güncelleme Akışı (Git-Native CD)

1. **Geliştirme:** Local makinede `/Users/tucibeyin/Desktop/yonned` üzerinde kodlama yapılır ve test edilir.
2. **Push:** Değişiklikler GitHub'a gönderilir:
   ```bash
   git commit -m "feat: Add dynamic process catalog builder"
   git push origin main
   ```
3. **Sunucuda Güncelleme (`node102` üzerinde):**
   ```bash
   cd /var/www/yonned
   git pull origin main
   pnpm install
   pnpm --filter @yonned/db db:push
   pnpm --filter @yonned/api build
   pnpm --filter @yonned/web build
   pm2 restart all
   ```
   *Tüm süreç 15 saniyede sıfır kesintiyle (zero-downtime) güncellenir.*
