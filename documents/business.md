# Yonned İş Modeli, Süreçler ve Ürün Vizyonu (V1.0 - Master Business Spec)
**Belge Türü:** Tek Gerçek Kaynağı (Single Source of Truth - Business SSOT)  
**Tarih:** 28 Ekim 2026  
**Durum:** Kesinleşmiş ve Onaylanmış Ana İş Belgesi  
**Felsefe:** *Kişi-Merkezli Varlık Ekosistemi (Yonned Citizen), Çift Yönlü Değer Akışı (Hizmet Veren & Hizmet Alan Simetrisi), Viral Ağ Etkisi (Flywheel)*

---

## 1. ÜRÜN VİZYONU VE TEMEL FELSEFE

### 1.1. Yonned Nedir?
Yonned; yalnızca bir sektöre hapsedilmiş klasik bir B2B ERP yazılımı **değildir**. 

Yonned; fiziksel dünyada varlıkları olan ve bu varlıklar üzerinde operasyon yürüten insanların **kendi varlıklarıyla yaşadığı, hem hizmet verip hem hizmet alabildiği yaşayan bir ekosistemdir.**

### 1.2. "Yonned Bireyi" (The Yonned Citizen)
Geleneksel yazılımlar insanı bir role kilitler: *"Sen sadece müşterisin"* veya *"Sen sadece patronsun"*.

Yonned'de ise insan tektir ve merkezdedir:
* **Her bireyin bir "Varlık Cüzdanı" (Asset Wallet) vardır:**
  * Bireyin özel varlıkları olabilir: Köpeği (*Tarçın*), Arabası (*34 ABC 123*), Telefonu (*iPhone 15*).
  * Bireyin işlettiği varlıkları olabilir: Kliniği (*Pati Veteriner*), Oto Yıkaması (*Demir Detailing*), Atölyesi.
* **Birey aynı gün içinde iki tarafta da yaşar:**
  * Gündüz kliniğinde ameliyat yapan, kafesleri yöneten bir **Hizmet Veren (Patron / Operatör)**,
  * Akşam arabasını servise bıraktığında balata değişimini telefonundan canlı izleyen bir **Hizmet Alan (Müşteri)**!

```
                                ┌──────────────────────┐
                                │   👤 YONNED BİREYİ   │
                                │    (Ali Yılmaz)      │
                                └──────────┬───────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
        [HİZMET VEREN (Patron / Usta)]          [HİZMET ALAN (Müşteri)]
        Kendi İşletme Varlıkları:               Kendi Özel Varlıkları:
        • "Ali Usta Oto Detailing"              • Köpeği "Tarçın"
        • 2 Yıkama Peronu, 1 Boya Fırını        • Arabası "34 ABC 123"
        • Yanında çalışan 2 çırak               • Telefonu "iPhone 15"
                        │                                     │
                        ▼                                     ▼
        Başkalarının arabalarına                Köpeğini "Pati Kliniği"ne
        pasta-cila yapar, fatura                bırakır, ameliyatını Yonned'den
        keser, veri besler, para kazanır.       canlı izler, hizmet satın alır.
```

---

## 2. DEĞER ÖNERİSİ (VALUE PROPOSITION)

### 2.1. İşletme Sahibi (Patron) İçin:
* **Kuşbakışı Hakimiyet:** Kaç şubesi, kaç katı olursa olsun; kafes, masa veya lift doluluklarını saniyesinde izler.
* **Süreç Özgürlüğü:** Süreçleri kendi belirler (şablon kütüphanesi). İster veterinerlik yapsın, ister oto detailing, ister kuyumculuk; yazılımı dükkanına göre şekillendirir.
* **Sıfır Donanım & Bulut Maliyeti:** Pahalı AWS S3 faturaları veya lisans ücretleri ödemez.

### 2.2. Saha Çalışanı (Operatör) İçin:
* **Sıfır Bürokrasi:** Islak, eldivenli veya yağlı ellerle uzun formlar doldurmaz.
* **Evrensel Tarayıcı:** Tek bir kamera vizörüyle kafes QR'ını, hasta QR'ını veya ilaç barkodunu saniyede okutur.
* **Sıfır Blokaj:** Sistemde olmayan yeni bir ilaç mı geldi? Hata almaz; adını yazar, geçer. Araya acil müdahale mi girdi? İşi kilitlemeden müdahaleyi kaydeder.

### 2.3. Hizmet Alan (Müşteri) İçin:
* **Uygulama İndirme Zorunluluğu Yok:** SMS veya WhatsApp'tan gelen `yonned.com/t/token` linkine tıklar.
* **Tam Şeffaflık ve Güven:** "Dostum şu an nerede? Ameliyat başladı mı? Arabamın hangi parçası değişti?" sorularının cevabını canlı fotoğraflar ve zaman damgalarıyla izler.
* **Tüm Varlıklar Tek Ekranda:** Kedisinin aşı karnesini de arabasının servis geçmişini de aynı profil altında saklar.

---

## 3. VİRAL AĞ ETKİSİ VE BÜYÜME ÇARKI (THE FLYWHEEL)

Geleneksel B2B yazılımlar yavaş büyür çünkü sadece işletmelere tek tek satış yaparlar. Yonned ise **çift taraflı ağ etkisiyle kendi kendini büyütür:**

```
                  ┌──────────────────────────────────────────────┐
                  │ 1. İşletme Yonned'i Kullanmaya Başlar        │
                  │    (Örn: Pati Veteriner Kliniği)             │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 2. Ayda 500 Müşteriye Canlı Takip Linki Gider │
                  │    (Müşteriler Yonned kalitesini deneyimler) │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 3. Müşterilerin İçindeki İşletme Sahipleri   │
                  │    (Oto yıkamacı, tamirci, terzi, diş hekimi)│
                  │    "Bunu kendi dükkanımda da kullanmalıyım!" │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 4. Yeni İşletmeler Sıfır Reklamla Katılır    │
                  │    (Çark katlanarak hızlanır!)               │
                  └──────────────────────────────────────────────┘
```

---

## 4. GELİR VE MONETİZASYON STRATEJİSİ (BUSINESS MODEL)

Yonned, küçük esnaftan uluslararası zincirlere kadar uzanan çok katmanlı ve adil bir fiyatlandırma modeline sahiptir:

### 4.1. Freemium / Başlangıç Katmanı (Micro Tier)
* **Hedef:** Tek kişilik atölyeler, mobil çalışan teknisyenler, küçük butik dükkanlar.
* **Özellik:** 1 Bayi, 1 Kullanıcı, ayda 100 aktif süreç kaydı $\rightarrow$ **ÜCRETSİZ.**
* **Amaç:** Pazar penetrasyonu sağlamak ve platformu standart kılmak.

### 4.2. B2B Profesyonel Abonelik (SaaS Subscription)
* **Hedef:** Kliniker, oto servisler, çok çalışanlı işletmeler.
* **Fiyatlandırma:** Bayi başı + Aktif operatör kotası (Örn: 29$ / ay / şube).
* **Kapsam:** Sınırsız süreç, sınırsız QR basımı, özel şablonlar, detaylı analitik ve raporlar.

### 4.3. Katma Değerli Hizmetler (Add-Ons)
* **Akıllı Bildirim Paketi:** Müşteriye doğrudan WhatsApp Business API ve SMS ile giden durum bildirimleri (kullanım başı mikropayments).
* **Kurumsal Çoklu Şube (Enterprise):** 10'dan fazla bayisi olan zincirler için merkezi denetim, özel SLA ve konsolide ciro/performans raporlaması.

---

## 5. SEKTÖREL GENİŞLEME VE PAZARA GİRİŞ (GO-TO-MARKET)

Sistemimiz tamamen generic (Kişi - Aset - Süreç) olduğu için aynı altyapıyla sırayla dikey sektörleri fetheder:

| Aşama | Sektör / Dikey | Neden Bu Sıra? | Aset / Süreç Örneği |
| :---: | :--- | :--- | :--- |
| **Faz 1** | **Veteriner Klinikleri** | Güven ve takip ihtiyacının en yüksek olduğu sektör. Hasta sahipleri duygusal bağ taşır, canlı takibe bayılır. | Kedi Tarçın $\rightarrow$ Ameliyat, Tıraş, Pansuman, Aşı. |
| **Faz 2** | **Oto Servis & Detailing** | Yüksek işlem hacmi, parça tüketimi ve fiziksel istasyon (lift, peron) takibi ihtiyacı. | 34 ABC 123 $\rightarrow$ Yağ Bakımı, Seramik Kaplama, Balata. |
| **Faz 3** | **Teknik Servis & Cihaz Tamiri** | Seri no/IMEI takibi, bekleme rafları ve arıza test süreçleri. | iPhone 15 $\rightarrow$ Ekran Değişimi, Anakart Lehim, Test. |
| **Faz 4** | **Zanaat & Özel Üretim Atölyeleri**| Kuyumcular, özel dikim terziler, mobilya restorasyon atölyeleri. | Elbise / Mücevher $\rightarrow$ Prova, Kesim, Taş Dizimi. |

---

## 6. KULLANICI DENEYİMİ VE ROLLERİN AKIŞKANLIĞI

Yonned uygulamasını açan bir birey, profil fotoğrafına tıklayarak tek dokunuşla dünyasını değiştirir:

```
┌────────────────────────────────────────────────────────┐
│  👤 Ali Yılmaz (Giriş Yapıldı)                         │
├────────────────────────────────────────────────────────┤
│  AKTİF ÇALIŞMA ALANI:                                  │
│  🟢 Ali Usta Detailing (Patron / Düzenleyici Modu)      │
│     • Peron 1: 🔴 34 YZ 999 (Yıkama devam ediyor)      │
│     • Peron 2: 🟢 Boş                                   │
│     • [+ Süreç Başlat]  [📷 QR Tara]  [📊 Raporlar]    │
├────────────────────────────────────────────────────────┤
│  [🔄 Mod Değiştir / Kişisel Varlıklarım]                │
│  🚗 Kişisel Takip Modu (Sorgulayıcı)                   │
│     • 🐾 Kedi Tarçın: Pati Kliniğinde (Ameliyat Bitti) │
│     • 🚙 BMW 3.20: Maslak Serviste (Parça Bekleniyor)  │
└────────────────────────────────────────────────────────┘
```

Bu akışkanlık sayesinde kullanıcı hiçbir zaman iki farklı uygulama indirmek veya farklı hesaplarla giriş yapmak zorunda kalmaz. **İş hayatı ve kişisel varlıkları aynı ekosistemin içinde barış içinde akar.**

---

## 7. VARLIK PAYLAŞIMI VE SADE YETKİ FELSEFESİ (ASSET SHARING)

Yonned'de kafa karıştıran roller, karmaşık matrisler veya katı paketler yoktur. 
Tek bir evrensel gerçek vardır:

> **"Kişi kendi asetin patronudur. Varlığını dilediği insanla paylaşabilir; paylaşılan kişinin haklarını tamamen bağımsız seçebileceği 4 temel izinle kendisi belirler."**

```
┌────────────────────────────────────────────────────────┐
│  ASET PAYLAŞ: "Kedi Tarçın" veya "Pati Kliniği"        │
├────────────────────────────────────────────────────────┤
│  Kiminle Paylaşacaksın? : [ Kişi / Telefon Seç ]       │
│                                                        │
│  İzinler (Dilediğini aç, dilediğini kapat):            │
│  [✅] 1. Görüntüle ➔ Canlı takibi, geçmişi, veriyi görsün
│  [✅] 2. Değiştir  ➔ Var olan veriyi/notu güncelleyebilsin
│  [✅] 3. Ekle      ➔ Yeni süreç, olay, kayıt ekleyebilsin
│  [❌] 4. Sil       ➔ Kayıtları veya aseti silebilsin   │
│                                                        │
│  [ PAYLAŞ ]                                            │
└────────────────────────────────────────────────────────┘
```

### Hayatın İçinden Örnek Kombinasyonlar:
* **Stajyer / Yeni Asistan:** `Görüntüle: Açık`, `Ekle: Açık`, `Değiştir: Kapalı`, `Sil: Kapalı` *(Yeni ameliyat notu veya acil durum ekleyebilir ama geçmiş veriyi değiştiremez veya silemez - Hukuki ve Tıbbi Güvenlik).*
* **Eş / Eşit Ortak:** Dördü birden açık (`Görüntüle + Değiştir + Ekle + Sil`).
* **Müşteri / Sessiz Ortak / Gözlemci:** Yalnızca `Görüntüle: Açık`.
* **Kıdemli Usta / Hekim:** `Görüntüle: Açık`, `Değiştir: Açık`, `Ekle: Açık`, `Sil: Kapalı`.

---

## 8. EVRENSEL ASET PARADİGMASI: "HER ŞEY BİR ASETTİR"
*(The Universal Asset Paradigm: Symmetry of Person, Thing, and Process)*

Yonned dünyasında mimari ve zihinsel sadeliğin zirvesi şudur:
**Kişi (İnsan), Fiziksel Olan Şey (Mekan & Nesne) ve Fiziksel/Zamansal Süreç (İş & Eylem) aslında tek ve aynı "Aset" mantığıyla davranır.**

```
                                ┌───────────────────────────┐
                                │     EVRENSEL ASET (ASSET) │
                                └─────────────┬─────────────┘
                                              │
             ┌────────────────────────────────┼────────────────────────────────┐
             ▼                                ▼                                ▼
    [ 🏢 FİZİKSEL ŞEY ]              [ ⏱️ ZAMANSAL SÜREÇ ]             [ 👤 İNSAN / AKTÖR ]
    • Klinik / Dükkan                • Ameliyat / Operasyon            • Veteriner Hekim
    • Kat, Oda, Kafes, Lift          • Periyodik Bakım                 • Usta / Teknisyen
    • Kedi (Tarçın), Araba (BMW)     • Tıraş / Pansuman                • Stajyer / Çırak
    • İlaç / Sarf Malzemesi          • Aşı / Anlık Müdahale            • Müşteri / Varlık Sahibi
             │                                │                                │
             └────────────────────────────────┼────────────────────────────────┘
                                              │
                                              ▼
                         ORTAK DAVRANIŞ VE YETKİ MODELİ:
                     ┌───────────────────────────────────┐
                     │  1. GÖRÜNTÜLE  (can_view)         │
                     │  2. DEĞİŞTİR   (can_edit)         │
                     │  3. EKLE       (can_add)          │
                     │  4. SİL        (can_delete)       │
                     └───────────────────────────────────┘
```

### Neden Bu Paradigma Devrimseldir?
1. **Zihinsel Yük Sıfırdır:** Kullanıcı ya da yazılımcı farklı nesneler için 10 farklı izin ve rol sistemi öğrenmez. Kliniği ortağıyla paylaşırken de, kedisini eşiyle paylaşırken de, bir ameliyat sürecini stajyere devrederken de aynı 4 kutuyu (Görüntüle, Değiştir, Ekle, Sil) kullanır.
2. **Süreç Bir Asettir:** Bir ameliyat veya detaylı araç restorasyonu zaman içinde yaşayan dinamik bir varlıktır. Tıpkı bir araba gibi; kimin yürüttüğü (sahibi/operatörü), hangi aşamada olduğu, geçmiş kayıtları ve fotoğrafları vardır. Müşteriye paylaşıldığında sadece `Görüntüle` yetkisi verilir; cerraha `Görüntüle + Değiştir + Ekle` yetkisi verilir.
3. **İnsan Bir Varlıktır:** İnsan bir yandan sisteme giriş yapan bilinçtir; diğer yandan işletme için bir yetkinlik ve çalışma kapasitesidir. Bir şubeye hekim veya çırak atamak, o kişiyi işletme aset ağacına bağlamaktan ve ona 4 fiilden gerekenleri tanımaktan ibarettir.
4. **Hizmet Veren & Hizmet Alan Simetrisi:** İster hizmet satan bir patron ol, ister hizmet alan bir müşteri; sistemle kurduğun ilişki değişmez: Varlığını seç, izinlerini belirle ve akışı başlat.




