---
description: DijitalBelge belge imzalama akışı — belgeleri e-imza ya da mobil imza ile, merkezi imza ekranından ya da kendi uygulamanızın içinden imzalatın.
---

# Belge İmzalama

Belgelerinizi **nitelikli elektronik imzayla** imzalatırsınız. 5070 sayılı Elektronik
İmza Kanunu'na göre nitelikli elektronik imza, ıslak imzayla aynı hukuki sonucu doğurur.

**Kullanım örnekleri:** iş sözleşmesi, kira sözleşmesi, resmî yazışmalar, kurum içi onay
gerektiren belgeler, tedarikçi sözleşmeleri.

## İki entegrasyon modeli

İmzanın **nerede** atıldığına göre iki model vardır. Süreç, belge ve imzacı hazırlığı
iki modelde de aynıdır; fark imzacının imzayı hangi ekranda attığıdır.

![Belge imzalama entegrasyon modelleri](../assets/akislar/imzalama-modelleri.svg)

| | A · Merkezi imza ekranı | B · Uygulama içi imza |
|---|---|---|
| **İmza nerede atılır** | DijitalBelge imza ekranında (`/sign/{accessToken}`) | Sizin uygulamanızın kendi ekranında |
| **İmzacı deneyimi** | Uygulamanızdan imza ekranına yönlendirilir ya da e-posta / SMS bağlantısıyla gelir | Uygulamanızdan hiç ayrılmaz |
| **Sizin geliştirmeniz** | Yalnızca API: süreç, belge, imzacı, webhook | API + Sümen entegrasyonu + kendi imza ekranınız |
| **Desteklenen imza türleri** | Tümü: e-imza, mobil imza, dijital onay türleri | E-imza (`EIMZA`, Sümen ile) |
| **Birden çok uygulamanız varsa** | Hepsi aynı imza ekranını kullanır; imza ekranı tek yerde güncellenir | Her uygulamada ayrı ayrı entegrasyon yapılır |
| **Ne zaman seçilir** | Hızlı entegrasyon, birden çok uygulama, farklı imza türleri | İmzanın kendi ürününüzün içinde, kesintisiz bir akışta atılması gerektiğinde |

!!! tip "Hangisiyle başlamalı?"
    Çoğu entegrasyon için **A · Merkezi imza ekranı** önerilir: daha az geliştirme
    gerektirir, tüm imza türlerini destekler ve imza ekranındaki iyileştirmeler
    uygulamalarınıza kendiliğinden yansır.

## İmza türleri

| Kod | Ad | İmzacının ihtiyacı |
|---|---|---|
| `EIMZA` | Elektronik İmza | Bilgisayarında takılı e-imza kartı / USB token ve [Sümen](../sumen-api.md) uygulaması |
| `MOBILE_IMZA` | Mobil İmza | Mobil imza özelliği açık SIM kart (Turkcell, Vodafone, Türk Telekom) |

Bir belgede birden çok imzacı olabilir ve her imzacıya ayrı tür verilebilir.
Örneğin şirket yetkilisi `EIMZA`, müşteri `MOBILE_IMZA` ile imzalayabilir.

---

## A · Merkezi imza ekranı

Uygulamanız süreci hazırlar ve imzacıyı DijitalBelge imza ekranına gönderir. İmza
ekranı e-imza, mobil imza ve dijital onay türlerinin hepsini kendisi yönetir.

![Merkezi imza ekranıyla belge imzalama akışı](../assets/akislar/belge-imzalama.svg)

| # | Ne yapılır | API | Ayrıntı |
|---|---|---|---|
| 1 | Süreç oluşturulur | `POST /process-instances` | [Süreç API](../progress.md) |
| 2 | Belge eklenir: PDF yüklenir ya da hazır bir taslaktan üretilir | `POST …/document/single` · `POST …/document/document-type` | [Döküman API](../documents.md) · [Taslaktan Döküman](../progress_doctype.md) |
| 3 | İmzacılar eklenir ve her birine imza türü verilir | `POST …/document/{documentId}/signers` | [İmzacı API](../signers.md) |
| 4 | Süreç başlatılır; yanıttaki `accessToken` saklanır | `PUT …/status/start` | [Süreç API](../progress.md) |
| 5 | İmzacı imza ekranına gelir: uygulamanızdaki "İmzala" butonuyla yönlendirilir ya da DijitalBelge'nin gönderdiği e-posta / SMS bağlantısıyla | `https://app.dijitalbelge.com/sign/{accessToken}` | |
| 6 | İmzacı imza ekranında e-imza ya da mobil imza ile imzalar | — | |
| 7 | Her imzada webhook gelir; `allSigned: true` ise belgenin tüm imzacıları imzalamıştır | `DOCUMENT_SIGNED` | [Webhook](../webhook.md) |
| 8 | İmzalı belge indirilir | `GET …/document/{documentId}/file` | [Döküman API](../documents.md) |

---

## B · Uygulama içi imza

İmzacı uygulamanızdan ayrılmadan, sizin ekranınızda imzalar. Uygulamanız
DijitalBelge'den belgenin **imzalama token'ını** alır ve imzacının bilgisayarındaki
[Sümen](../sumen-api.md) uygulamasına `signDocument` komutuyla iletir. Sümen belgenin
özetini DijitalBelge'den alır, e-imza kartıyla imzalar ve imzayı DijitalBelge'ye kendisi
gönderir; belge içeriği uygulamanızdan geçmez.

![Uygulama içi belge imzalama akışı](../assets/akislar/belge-imzalama-uygulama-ici.svg)

| # | Ne yapılır | API | Ayrıntı |
|---|---|---|---|
| 1 | Süreç oluşturulur, belge ve imzacı (`EIMZA`) eklenir | A modelindeki 1–3. adımlar | [Süreç API](../progress.md) |
| 2 | Süreç başlatılır; yanıttaki `accessToken` saklanır | `PUT …/status/start` | [Süreç API](../progress.md) |
| 3 | Belgelerin imzalama token'ları alınır: her belge için `docsigfiles[].token` | `GET /api/files/process/{accessToken}` | |
| 4 | İmzacı sizin ekranınızda e-imza cihazını, sertifikasını seçer ve PIN'ini girer | Sümen `devices` | [Sümen API](../sumen-api.md) |
| 5 | Uygulamanız Sümen'e imzalama komutunu gönderir | Sümen `signDocument` | [Sümen API](../sumen-api.md) |
| 6 | Sümen özeti alır, kartla imzalar ve DijitalBelge'ye gönderir | (Sümen yapar) | |
| 7 | Sümen sonucu uygulamanıza döner | WebSocket yanıtı | |
| 8 | Webhook gelir; imzalı belge indirilir | `DOCUMENT_SIGNED` · `GET …/document/{documentId}/file` | [Webhook](../webhook.md) |

!!! warning "İmzalama token'ını imzacıdan başkasına göstermeyin"
    `accessToken` ve belgenin imzalama token'ı, o belgeyi imzalama yetkisi taşır.
    Token'ları yalnızca imzacının oturumunda kullanın; log'a ya da URL'ye yazmayın.
    Belgeyi yalnızca, sertifikasındaki TC kimlik numarası imzacıyla eşleşen kişi imzalayabilir.

!!! info "Gereksinimler"
    - İmzacının bilgisayarında [Sümen](../sumen-api.md) kurulu ve çalışır olmalı.
    - Uygulamanız Sümen'e tarayıcıdan, yerel WebSocket bağlantısıyla bağlanır.
    - Mobil imza ve dijital onay türleri bu modelde desteklenmez; bunlar için A modelini kullanın.

---

## Diğer seçenekler

!!! info "PDF dışındaki dosyalar"
    Word, XML gibi PDF olmayan dosyalar için süreç tipi `DOSYA_IMZALAMA` seçilir; dosya
    değiştirilmeden ayrık imzalanır (CAdES / ASiC-E). Ayrıntılar: [Dosya İmzalama](../dosya-imzalama.md).

!!! tip "İnsan müdahalesi olmadan imza"
    Kurum adına sunucuda saklanan bir sertifikayla otomatik imza için
    [Bulut İmzalama (Autosign)](../autosign.md) sayfasına bakın.

## İmzayı doğrulama

İmzalı belgenin geçerliliği hem API'den hem de herkese açık doğrulama sayfasından
kontrol edilebilir: [İmza Formatları ve Doğrulama](../signature-verification.md).

## Örnekler

- [Karşılıklı Elektronik Sözleşme İmzalama](../examples/karsilikli-sozlesme-imzalama.md)
- [Abonelik Sözleşmesi İmzalama](../examples/abonelik-sozlesmesi.md) (Senaryo A)
- [Taslaktan Dinamik Süreç Başlatma](../examples/taslaktan-dinamik-surec.md)
