---
description: DijitalBelge ile imzalanan ya da onaylanan belgelerin doğrulanması — QR kod, dosya yükleyerek doğrulama sayfası ve API ile doğrulama.
---

# Belge Doğrulama

DijitalBelge'de imzalanan ya da onaylanan her belge sonradan doğrulanabilir: imzanın
geçerli olduğu, belgenin imzadan sonra değiştirilmediği ve imzanın kime, hangi tarihte
ait olduğu kontrol edilir. Doğrulama için üç yol vardır.

![Belge doğrulama yolları](../assets/akislar/dogrulama-yollari.svg)

| Yol | Kim kullanır | Nasıl | Giriş gerekir mi |
|---|---|---|---|
| **1 · QR kod** | Belgenin basılı ya da PDF halini elinde tutan herkes | Belgedeki QR okutulur, sürecin sayfası açılır | Hayır |
| **2 · Dosya yükleyerek** | Belgeyi e-posta ile alan karşı taraf, denetçi, mahkeme | Dosya [doğrulama sayfasına](https://app.dijitalbelge.com/sign/dogrula) yüklenir | Hayır (resimli doğrulama kodu ile) |
| **3 · API ile** | Sizin sisteminiz | Süreçteki imza, imzacı ya da görev bazında doğrulanır | Evet (`X-Client-Id`, `document:read`) |

---

## 1 · QR kod

Her sürecin belgeye basılabilen bir doğrulama QR kodu vardır. QR, sürecin sayfasını
(`https://app.dijitalbelge.com/sign/{accessToken}`) açar; burada belgeler, imzacılar ve
her imzanın durumu görünür.

QR'ın PNG görselini kendi ekranınızda göstermek için:
`GET /process-instances/{processId}/qr` ([Süreç API](../progress.md)).

## 2 · Dosya yükleyerek

Belgeyi alan kişi, hesap açmadan
[app.dijitalbelge.com/sign/dogrula](https://app.dijitalbelge.com/sign/dogrula) sayfasına
dosyayı yükleyerek doğrular. Sayfa, yüklenen dosyanın türüne göre şunları kontrol eder:

| Doğrulama türü | Yüklenen | Ne kontrol edilir |
|---|---|---|
| `PDF` | İmzalı PDF | PDF'teki e-imza ve zaman damgaları: geçerlilik, sertifika zinciri, imzadan sonra değişiklik |
| `PDF_JADES` | PDF + kanıt dosyası (`.jades`) | Kanıtın bu PDF'e ait olduğu; kanıttaki SMS, konum, kimlik kartı, yüz ve video bilgileri |
| `ASICE` | `.asice` container | Container imzası ve içindeki her dosyanın bütünlüğü |
| `JADES` | Yalnızca kanıt dosyası | Kanıt mührünün geçerliliği ve zaman damgası |

Aynı kontrol API'den de yapılabilir: `POST /files/verify` (girişsiz; resimli doğrulama kodu
`GET /public/sign/captcha` ile alınır). Ayrıntılar:
[İmza Formatları ve Doğrulama](../signature-verification.md).

!!! tip "Dijital onayda iki dosya birlikte doğrulanır"
    E-posta, SMS ya da kimlik kartıyla onaylanan belgelerde kanıt PDF'in içinde değil,
    ayrı bir `.jades` dosyasındadır. Karşı tarafa onaylı PDF ile birlikte kanıt dosyasını da
    gönderin; `PDF_JADES` türüyle ikisi birlikte doğrulanır.

## 3 · API ile

Kendi sisteminizdeki bir sürecin imzalarını programlı olarak doğrularsınız. Yanıt her
durumda aynı yapıdadır: `valid`, `message` ve imza ayrıntıları.

| Ne zaman | API |
|---|---|
| İmzacı ID'sini biliyorsanız | `GET …/process-instances/{processId}/signers/{signerId}/signature/verify` |
| Belge ve görev ID'sini biliyorsanız | `GET …/process-instances/{processId}/document/{documentId}/tasks/{taskId}/signature/verify` |

Ayrıntılar ve yanıt alanları: [İmza Formatları ve Doğrulama](../signature-verification.md#dogrulama-endpointleri).

---

## Hangi belgede ne doğrulanır?

| Belge nasıl imzalandı | Ortaya çıkan dosya | Doğrulama |
|---|---|---|
| E-imza / mobil imza ile ([Belge İmzalama](../akislar/belge-imzalama.md)) | İmzalı PDF (PAdES) | PDF tek başına doğrulanır; Adobe Reader, EU DSS ve TÜBİTAK İmzager de açabilir |
| E-imza / mobil imza ile, PDF dışı dosyalar | `.asice` container | Container tek başına doğrulanır; EU DSS ve İmzager de açabilir |
| Dijital onay türleriyle ([Dijital Onay](../akislar/dijital-onay.md)) | Zaman damgalı PDF + `.jades` kanıt | PDF ve kanıt birlikte (`PDF_JADES`) |
| Kimlik doğrulama ([Kimlik Doğrulama](../akislar/kimlik-dogrulama.md)) | Yalnızca `.jades` kanıt | Kanıt tek başına (`JADES`) |
