---
description: DijitalBelge belge imzalama akışı — belgeleri e-imza ya da mobil imza ile, ıslak imza yerine geçen nitelikli elektronik imzayla imzalatın.
---

# Belge İmzalama

Belgelerinizi **nitelikli elektronik imzayla** imzalatırsınız. 5070 sayılı Elektronik
İmza Kanunu'na göre nitelikli elektronik imza, ıslak imzayla aynı hukuki sonucu doğurur.

**Kullanım örnekleri:** iş sözleşmesi, kira sözleşmesi, resmî yazışmalar, kurum içi onay
gerektiren belgeler, tedarikçi sözleşmeleri.

![Belge imzalama akışı](../assets/akislar/belge-imzalama.svg)

## İmza türleri

| Kod | Ad | İmzacının ihtiyacı |
|---|---|---|
| `EIMZA` | Elektronik İmza | Bilgisayarında takılı e-imza kartı / USB token ve [Sümen](../sumen-api.md) uygulaması |
| `MOBILE_IMZA` | Mobil İmza | Mobil imza özelliği açık SIM kart (Turkcell, Vodafone, Türk Telekom) |

Bir belgede birden çok imzacı olabilir ve her imzacıya ayrı tür verilebilir.
Örneğin şirket yetkilisi `EIMZA`, müşteri `MOBILE_IMZA` ile imzalayabilir.

## Adımlar

| # | Ne yapılır | API | Ayrıntı |
|---|---|---|---|
| 1 | Süreç oluşturulur | `POST /process-instances` | [Süreç API](../progress.md) |
| 2 | Belge eklenir: PDF yüklenir ya da hazır bir taslaktan üretilir | `POST …/document/single` · `POST …/document/document-type` | [Döküman API](../documents.md) · [Taslaktan Döküman](../progress_doctype.md) |
| 3 | İmzacılar eklenir ve her birine imza türü verilir | `POST …/document/{documentId}/signers` | [İmzacı API](../signers.md) |
| 4 | Süreç başlatılır | `PUT …/status/start` | [Süreç API](../progress.md) |
| 5 | DijitalBelge imzacıya e-posta / SMS ile imza bağlantısı gönderir | — | |
| 6 | İmzacı belgeyi e-imza ya da mobil imza ile imzalar | — | |
| 7 | Her imzada webhook gelir; `allSigned: true` ise belgenin tüm imzacıları imzalamıştır | `DOCUMENT_SIGNED` | [Webhook](../webhook.md) |
| 8 | İmzalı belge indirilir | `GET …/document/{documentId}/file` | [Döküman API](../documents.md) |

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
