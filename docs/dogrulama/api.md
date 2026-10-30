---
description: DijitalBelge Doğrulama API — PAdES, ASiC-E, PDF+JAdES, JAdES, CAdES ve XAdES imzalarını API anahtarıyla, süreçten bağımsız doğrulayın.
---

# Doğrulama API

Elinizdeki herhangi bir imzalı dosyayı, API anahtarınızla ve **bir sürece bağlı olmadan**
doğrularsınız. Dosyanın DijitalBelge'de imzalanmış olması gerekmez: başka bir sistemde
e-imza ya da mobil imzayla atılmış imzalar da doğrulanır.

!!! info "Süreç içindeki imzalar ayrıdır"
    DijitalBelge'de başlattığınız bir süreçteki imzaları dosya göndermeden doğrulamak için
    süreç uçlarını kullanın: [Doğrulama Yolları · Süreçteki imzalar](index.md#3-surecteki-imzalar).
    Bu sayfadaki uçlar ise dosyayı sizden alır ve hiçbir süreçle ilişkilendirmez.

## Özet

| Özellik | Değer |
|---|---|
| Base URL | `https://app.dijitalbelge.com/api/external/verify` |
| Kimlik doğrulama | `X-Client-Id`, `X-Client-Secret` ([API Erişimi](../authentication.md)) |
| Yetki (scope) | `verify:document` |
| İstek biçimi | `multipart/form-data` |

| Format | Uç | Dosya alanları |
|---|---|---|
| **PAdES** (imzalı PDF) | `POST /pades` | `file`: PDF |
| **ASiC-E** | `POST /asice` | `file`: `.asice` |
| **PDF + JAdES** | `POST /pdf-jades` | `file`: PDF · `jades`: `.jades` kanıt dosyası |
| **JAdES** (e-imza / mobil imzalı ya da kanıt mührü) | `POST /jades` | `signature`: `.jades` · `file`: imzalanan dosya (yalnızca ayrık imzada) |
| **CAdES** | `POST /cades` | `signature`: `.p7s` · `file`: imzalanan dosya (yalnızca ayrık imzada) |
| **XAdES** | `POST /xades` | `signature`: imzalı XML · `file`: imzalanan dosya (yalnızca ayrık imzada) |

!!! tip "Gömülü mü, ayrık mı?"
    **Gömülü** (attached / enveloped) imzada imzalanan içerik imza dosyasının içindedir;
    yalnızca imza dosyasını gönderirsiniz. **Ayrık** (detached) imzada imza dosyası içeriği
    taşımaz; imzalanan orijinal dosyayı da `file` alanında gönderirsiniz. Ayrık bir imzayı
    `file` olmadan gönderirseniz `400` döner ve mesajda eksik dosya belirtilir.

## Geçerlilik kuralları

Bir imza, aşağıdakilerin **hepsi** sağlanırsa geçerli (`valid: true`) sayılır:

1. **Bütünlük:** İmza değeri doğrulanır ve imzalanan içerik imzadan sonra değişmemiştir.
2. **Sertifika süresi:** İmzacı sertifikası imza atıldığı tarihte geçerlidir.
3. **Güven zinciri:** İmzacı sertifikası güvenilir bir elektronik sertifika hizmet sağlayıcısına (ESHS) zincirlenir.
4. **Zaman damgası:** İmzada zaman damgası varsa o da geçerlidir.

Formatlara özel ek kontroller:

| Format | Ek kontrol |
|---|---|
| PAdES | İmzadan sonra sayfa içeriği değişmemiş olmalı (LTV / zaman damgası eklemeleri değişiklik sayılmaz) |
| ASiC-E | Container'daki her dosyanın özeti manifest'teki değerle eşleşmeli |
| PDF + JAdES | Kanıt mührü bu PDF'e (ya da imzalanmadan önceki haline) ait olmalı |
| XAdES | `SigningCertificate` özeti imzadaki sertifikayla eşleşmeli; aynı `Id` birden fazla elemanda bulunmamalı |

## İstek örnekleri

=== "PAdES"

    ```bash
    curl -X POST https://app.dijitalbelge.com/api/external/verify/pades \
      -H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx" \
      -F "file=@sozlesme-imzali.pdf"
    ```

=== "ASiC-E"

    ```bash
    curl -X POST https://app.dijitalbelge.com/api/external/verify/asice \
      -H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx" \
      -F "file=@belgeler.asice"
    ```

=== "PDF + JAdES"

    ```bash
    curl -X POST https://app.dijitalbelge.com/api/external/verify/pdf-jades \
      -H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx" \
      -F "file=@sozlesme.pdf" \
      -F "jades=@sozlesme_evidence.jades"
    ```

=== "CAdES"

    ```bash
    # Ayrık imza: imza + imzalanan dosya
    curl -X POST https://app.dijitalbelge.com/api/external/verify/cades \
      -H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx" \
      -F "signature=@rapor.docx.p7s" \
      -F "file=@rapor.docx"

    # Gömülü imza: yalnızca .p7s
    curl -X POST https://app.dijitalbelge.com/api/external/verify/cades \
      -H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx" \
      -F "signature=@rapor.p7s"
    ```

=== "XAdES"

    ```bash
    # Gömülü (enveloped / enveloping) imza
    curl -X POST https://app.dijitalbelge.com/api/external/verify/xades \
      -H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx" \
      -F "signature=@e-recete-imzali.xml"

    # Ayrık imza: imza + imzalanan dosya
    curl -X POST https://app.dijitalbelge.com/api/external/verify/xades \
      -H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx" \
      -F "signature=@imza.xml" \
      -F "file=@belge.pdf"
    ```

=== "JAdES"

    ```bash
    curl -X POST https://app.dijitalbelge.com/api/external/verify/jades \
      -H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx" \
      -F "signature=@kanit.jades"
    ```

## Yanıt

Tüm uçlar aynı yapıyı döner. `detectedType` formatı belirtir; o formata ait alan doldurulur.

```json
{
  "detectedType": "XADES",
  "valid": true,
  "message": "XAdES imzası geçerli (1 imza)",
  "xades": [
    {
      "signatureId": "Signature-3f2a",
      "signerName": "AHMET YILMAZ",
      "signingTime": "2026-10-30T14:12:05",
      "integrityValid": true,
      "signatureValueValid": true,
      "failedReferences": [],
      "signatureForm": "ENVELOPING",
      "xadesLevel": "XAdES-BES",
      "signingCertificateMatches": true,
      "certificateValidAtSignTime": true,
      "certificateTrusted": true,
      "hasTimestamp": false,
      "timestampValid": false,
      "certinfo": { "...": "imzacı sertifikasının ayrıntıları" }
    }
  ]
}
```

| Alan | Doldurulduğu format | İçerik |
|---|---|---|
| `detectedType` | Tümü | `PDF`, `ASICE`, `PDF_JADES`, `JADES`, `CADES`, `XADES` |
| `valid` | Tümü | Tüm imzalar geçerli mi |
| `message` | Tümü | Sonucun açıklaması; geçersizse en önemli neden |
| `pdfSignatures[]` | PAdES, PDF + JAdES | PDF'teki her imza ve zaman damgası |
| `asice` | ASiC-E | `signatures[]`, `files[]` (dosya bazında özet eşleşmesi), `allFilesMatch` |
| `jades` | JAdES, PDF + JAdES | JAdES imzası: imzacı / sertifika, zaman damgası; PDF + JAdES'te PDF'e bağı (`documentLinkValid`) |
| `cades[]` | CAdES | Her imzacı: `integrityValid`, `digestMatches`, `certificateTrusted`, `cadesLevel` |
| `xades[]` | XAdES | Her imza: `signatureForm`, `xadesLevel`, `failedReferences`, `signingCertificateMatches` |

### Seviyeler

| Alan | Değerler |
|---|---|
| `cadesLevel` | `CAdES-B-B` (temel), `CAdES-B-T` (zaman damgalı) |
| `xadesLevel` | `XMLDSig` (XAdES nitelikleri yok), `XAdES-BES`, `XAdES-T` (zaman damgalı) |
| `signatureForm` (XAdES) | `ENVELOPED` (imza belgenin içinde), `ENVELOPING` (belge imzanın içinde), `DETACHED` (ayrık) |

## Hatalar

| Kod | Ne zaman |
|---|---|
| `200` + `valid: false` | İmza okundu ama geçersiz; neden `message` alanında |
| `400` | Dosya eksik ya da seçilen formatla uyuşmuyor, ayrık imzada imzalanan dosya gönderilmemiş, imza okunamadı |
| `401` | `X-Client-Id` / `X-Client-Secret` eksik ya da hatalı |
| `403` | Uygulamanın `verify:document` yetkisi yok |
| `413` | Dosya boyutu sınırı aşıldı |
