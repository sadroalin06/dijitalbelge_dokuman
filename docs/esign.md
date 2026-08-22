---
description: E-İmza ile Login API — üçüncü taraf uygulamalara e-imza kullanarak kimlik doğrulama ve giriş (login) entegrasyonu sağlayan DijitalBelge API'si.
---

# E-İmza ile Login API

Üçüncü taraf platformların kendi kullanıcılarını Dijital Belge sistemi ile  e-imza ile giriş yaptırmak için kullandığı API'dir.

## Genel Bakış

### Sümen Uygulaması Nedir?

**Sümen**, Dijital Belge'nin imzalama işlemini yöneten ve yönetmek için geliştirilmiş yazılımıdır:

- **Kullanıcının bilgisayarına kurulur** - Lokal olarak çalışır
- **Tüm imzaları otomatik tanır** - Kullanıcının tüm dijital imzalarını merkezi olarak yönetir
- **E-imza ile otomatik giriş** - Sistem, Sümen üzerindeki imzayı kullanarak kullanıcıyı tanımlar
- **Güvenli entegrasyon** - Platform ve Dijital Belge arasında güvenli veri akışı sağlar

### Login Akışı

```
1. Üçüncü Taraf Platform
   ↓
2. Kullanıcı Bilgisi Topla (TC, Email, Telefon vb.)
   ↓
3. Dijital Belge API'sine Gönder (/external/auth/tx)
   ↓
4. Dijital Belge, geçici bir giriş Token oluşturur
   ↓
5. Sümen uygulamasına token bilgisi gönderilir.Platform kullanıcının PC deki Sümen ile Local websoket ile haberleşir
   ↓
6. Sümen imzalar ve Dijital Belge platformuna gönderim yapar
   ↓
7. Dijital Belge platformun login için gerekli tüm güvenlik doğrulamalarını yapar ve bir auditlog oluşturur
   ↓
8. Sümen platforma websoket üzerinden işlem sonucu döner
   ↓
9. Platform elindeki token ile Dijital Belge platformunda audidlogu okur ve kullanıcısını login yapar
```

---

## Özet

| Özellik | Değer |
|---------|-------|
| Temel URL | `https://app.dijitalbelge.com/api` |
| Temel Path | `/external` |
| Base URL | `https://app.dijitalbelge.com/api/external` |
| Kimlik Doğrulama | X-Client-Id, X-Client-Secret |

---

## Endpoints

### 1. E-İmza ile Login İşlemi Başlat

Kullanıcı bilgilerini gönderip e-imza ile login işlemini başlatır.

#### İstek

```http
POST {baseURL}/auth/tx
```

**Content-Type:** `application/json`

#### Request Body

```json
{
  "email": "ahmet@x.com",
  "ceptel": "xxxxxxxxx",
  "tckn": "12345678901",
  "platformUserId": "U-91",
  "userInfo": {
    "ipAddress": "1.2.3.4",
    "userAgent": "Chrome/120 Windows 11",
    "deviceHint": "DESKTOP",
    "locale": "tr-TR",
    "timeZone": "Europe/Istanbul"
  }
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `email` | string | Evet | Kullanıcının email adresi |
| `ceptel` | string | Evet | Kullanıcının cep telefonu numarası (ülke kodu hariç) |
| `tckn` | string | Evet | T.C. Kimlik Numarası (11 haneli) |
| `platformUserId` | string | Evet | Üçüncü taraf platformdaki kullanıcı ID'si |
| `userInfo` | object | Evet | Kullanıcı cihaz ve ortam bilgileri |
| `userInfo.ipAddress` | string | Evet | Kullanıcının IP adresi |
| `userInfo.userAgent` | string | Evet | Tarayıcı/cihaz bilgisi (User-Agent header) |
| `userInfo.deviceHint` | string | Evet | Cihaz tipi (DESKTOP, MOBILE, TABLET) |
| `userInfo.locale` | string | Evet | Kullanıcının dil-bölge (örn: tr-TR) |
| `userInfo.timeZone` | string | Evet | Kullanıcının saat dilimi (örn: Europe/Istanbul) |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "loginTxId": "tx_eb698381-a758-4cd2-9b3c-aacffd506372",
  "challenge": "9EZlfZMuZcuLc/8ppCjc3r5pWSE0bziAFBp0ZmvZH+Q=",
  "expiresIn": 120
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `loginTxId` | string | Oturum işlem kimliği (login transaction id) |
| `challenge` | string | Sümen uygulamasına iletilip imzalanacak challenge (base64) |
| `expiresIn` | number | Challenge'in geçerlilik süresi (saniye) |

Sümen uygulamasını şu adresten indirebilirsiniz: https://app.dijitalbelge.com/indir

Bu endpoint çağrıldıktan sonra entegrasyon platformu `loginTxId`, `challenge` ve `expiresIn` alanlarını alır. `challenge` değeri Sümen tarafına yönlendirilir ve Sümen tarafından kullanıcının e-imzası ile imzalanır. İmzalama tamamlandığında veya kullanıcı onayladığında, üçüncü taraf platform `GET {baseURL}/auth/tx/{loginTxId}` ile sonucu sorgular ve başarılıysa `loginToken` içeren yanıt döner.

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/auth/tx \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "email": "ahmet@x.com",
    "ceptel": "5441234567",
    "tckn": "12345678901",
    "platformUserId": "U-91",
    "userInfo": {
      "ipAddress": "1.2.3.4",
      "userAgent": "Chrome/120 Windows 11",
      "deviceHint": "DESKTOP",
      "locale": "tr-TR",
      "timeZone": "Europe/Istanbul"
    }
  }'
```

---

### 2. İşlem Sonucunu Kontrol Et 

Login işleminin durumunu kontrol eder. Kullanıcı Sümen'de imzayı onaylayana kadar polling yapılır.

#### İstek

```http
GET {baseURL}/auth/tx/{loginTxId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `loginTxId` | string | İşlem ID'si (önceki endpoint'ten döndürülen) |

#### Başarılı Yanıt (İşlem Tamamlanmadı)

**HTTP 200 OK**

```json
{
  "loginTxId": "TX-20260110-ABC123XYZ",
  "status": "PENDING",
  "message": "İmza onaylanması bekleniyor",
  "expiresIn": 250,
  "timestamp": "2026-01-10T12:31:00.123Z"
}
```

#### Başarılı Yanıt (İşlem Tamamlandı)

**HTTP 200 OK**

```json
{
  "loginTxId": "TX-20260110-ABC123XYZ",
  "status": "USED",
  "message": "İmza başarıyla doğrulandı",
  "loginToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "U-91",
    "email": "ahmet@x.com",
    "tckn": "12345678901",
    "signatureVerified": true
  },
  "timestamp": "2026-01-10T12:31:15.123Z"
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `loginTxId` | string | İşlem kimliği |
| `status` | string | İşlem durumu |
| `message` | string | Durum mesajı |
| `loginToken` | string | Login token'ı (üçüncü taraf platform tarafından kullanılır) |
| `user` | object | Doğrulanan kullanıcı bilgileri |
| `user.id` | string | Platform kullanıcı ID'si |
| `user.email` | string | Kullanıcı email'i |
| `user.tckn` | string | T.C. Kimlik numarası |
| `user.signatureVerified` | boolean | İmza doğrulandı mı |
| `timestamp` | string | Cevap zamanı |

#### Başarısız Yanıt (İşlem Zaman Aşımı)

**HTTP 410 Gone**

```json
{
  "loginTxId": "TX-20260110-ABC123XYZ",
  "status": "EXPIRED",
  "message": "İşlem zaman aşımına uğradı. Lütfen tekrar deneyin",
  "timestamp": "2026-01-10T12:35:45.123Z"
}
```

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/auth/tx/TX-20260110-ABC123XYZ \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 3. Tekrar Doğrulama (Token Detayı)

Bu endpoint, `loginTxId` veya Sümen'den dönen token string ile işlem detaylarını ve sunucunun gözlemlediği bağlamı (IP, TLS, UA vb.) döndürür. Tekrar doğrulama gerektiğinde (ör. audit, manuel inceleme veya ek güvenlik adımları) bu endpoint kullanılır.

#### İstek

```http
GET {baseURL}/auth/tx/{tokenstr}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `tokenstr` | string | `loginTxId` veya doğrulama token'ı |

#### Başarılı Yanıt (Detaylı Obje)

**HTTP 200 OK**

```json
{
  "loginTxId": "tx_eb698381-a758-4cd2-9b3c-aacffd506372",
  "accountId": 202,
  "email": "ahmet@x.com",
  "tcknHash": "sha256:...",
  "ceptel": "xxxxxxxxxxx",
  "platformUserId": "U-91",

  "challenge": "9EZlfZMuZcuLc/8ppCjc3r5pWSE0bziAFBp0ZmvZH+Q=",
  "createdAt": 1672955969528,
  "expiresAt": 1672956089528,

  "status": "PENDING",

  "serverContext": {
    "observedIp": "1.2.3.4",
    "observedUserAgent": "Chrome/120 Windows 11",
    "tlsProtocol": "TLS1.3",
    "serverReceivedAt": 1672955969528
  },

  "platformContext": {
    "ipAddress": "1.2.3.4",
    "userAgent": "Chrome/120 Windows 11",
    "deviceHint": "DESKTOP",
    "locale": "tr-TR",
    "timeZone": "Europe/Istanbul"
  },

  "deviceContext": {
    "hostName": "AHMET-PC",
    "os": "Windows 11",
    "sumenVersion": "2.5.1",
    "certificateSerial": "ABCD1234..."
  }
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `loginTxId` | string | Oturum işlem kimliği |
| `accountId` | number | Hesap ID'si |
| `email` | string | Kullanıcı e-posta adresi |
| `tcknHash` | string | T.C. kimlik numarasının hash'i (gizlilik için) |
| `ceptel` | string | Cep telefonu |
| `platformUserId` | string | Platformdaki kullanıcı ID |
| `challenge` | string | Başlangıç challenge değeri (base64) |
| `createdAt` | long | Oluşturulma zamanı (epoch ms) |
| `expiresAt` | long | Geçerlilik süresi sonu (epoch ms) |
| `status` | string | `LoginTxStatus` (PENDING, VERIFIED, COMPLETED, FAILED, EXPIRED) |
| `serverContext` | object | Backend'in gözlemlediği bağlantı bilgileri (SERVER_OBSERVED) |
| `platformContext` | object | Platformun beyan ettiği kullanıcı ortam bilgileri (PLATFORM_ASSERTED) |
| `deviceContext` | object | Sümen uygulamasının gönderdiği cihaz bilgileri (SUMENAPP_REPORTED) |

Açıklamalar:
- `serverContext` : Sunucu tarafında gözlemlenen IP, TLS protokolü, alınma zamanı gibi bilgiler.
- `platformContext` : Platformun kullanıcıdan topladığı bilgilerin aynısıdır (IP, UA, locale vb.).
- `deviceContext` : Sümen uygulamasından gelen PC/cihaz bilgileri; imza sertifika serisi veya Sümen versiyonu gibi doğrulama amaçlı veriler içerir.

`LoginTxStatus` örnek değerleri: `PENDING`, `USED`, `EXPIRED`.

Açıklama:
- `PENDING`: Login transaction henüz kullanılmadı (Sümen tarafından imzalama bekleniyor).
- `USED`: Kullanıcı Sümen ile doğrulandı ve işlem başarıyla tamamlandı (loginToken üretildi).
- `EXPIRED`: İşlem zaman aşımına uğradı veya başarısız oldu.

---

### 4. Audit Log Çekme

Belirtilen login işlemi için tüm audit log kayıtlarını ve işlem geçmişini döndürür.

#### İstek

```http
GET {baseURL}/auth/tx/{loginTxId}/audit
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `loginTxId` | string | Login işlemi ID'si (örn: `tx_de23d0bf-942f-4c02-a827-a7fb842110ba`) |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "v": 1,
  "meta": {
    "schemaVersion": 1,
    "revocationResult": "SUCCESS"
  },
  "loginTxId": "tx_c268f156-5de1-445d-8668-ad07c35a293b",
  "auditId": "161fc090-454b-40df-9b84-980444ca9a6e",
  "email": "ahmet@x.com",
  "tckn": "xxxxxxxxxxxxxxxxxxx",
  "ceptel": "xxxxxxxxxxxx",
  "status": "SUCCESS",
  "createdAt": "2026-01-11T17:23:36.3341608Z",
  "verifiedAtEpoch": 1768152216,
  "txExpiresAtEpoch": 1768152302,
  "failReason": null,
  "errors": null,
  "policy": "FAIL_CLOSED",
  "crypto": {
    "verifyMethod": "NONEwithRSA",
    "signedContent": "DigestInfo(SHA-256(challenge))",
    "signatureValid": true,
    "challengeHashSha256Hex": "858a7c57692c4e07451dc0d95914a69623c69015b49c6dd42afd67255b908b73",
    "signatureHashSha256Hex": "2539bcd7895e63c700283219e8dc36a578b579517969857bdb340e5591bbe021"
  },
  "device": {
    "deviceId": "dev_fd10de39-4683-49a5-bb5d-522f8d7e4c46",
    "hostName": "xxxxx",
    "osName": "Windows",
    "osVersion": "10 (10.0.26200)",
    "arch": "AMD64",
    "appName": "SumenApp",
    "appVersion": "1.2.0",
    "localIp": "192.168.1.xx",
    "buildHash": "git:cffae2c9fdc21537cf719982a50e814440652b0c"
  },
  "server": {
    "secure": "SERVER_OBSERVED",
    "publicIp": "0:0:0:0:0:0:0:1",
    "userAgent": "SumenApp/1.2.0"
  },
  "platform": {
    "source": "PLATFORM_ASSERTED",
    "userInfo": {
      "ipAddress": "1.2.3.4",
      "userAgent": "Chrome/120 Windows 11",
      "deviceHint": "DESKTOP",
      "locale": "tr-TR",
      "timeZone": "Europe/Istanbul"
    }
  },
  "certificate": {
    "chainVerified": true,
    "leafPublicKeySize": 2048,
    "leafFingerprintSha256Hex": "8ddb3e64548f8c3d8cb36a0e3491d0cc3af37c97d7e0a2221bf293ab16bdf1c2",
    "issuerFingerprintSha256Hex": "38fb238804ef72e6b506730f172cb8e2406146d5d7055164a20ab59ff8636147",
    "leaf": {
      "name": "XXXX XXXX",
      "tc": "XXXXXXXXX",
      "email": "xxxxx@xxxxx.xxx",
      "serialNumber": xxxxxxxxxxxxxx,
      "version": "3",
      "validFrom": "2025-02-11T10:40:06.000+00:00",
      "validTo": "2026-02-11T10:40:06.000+00:00",
      "publicKeyAlgorithm": "RSA",
      "signatureAlgorithm": "SHA384withECDSA",
      "keyUsages": ["digitalSignature", "nonRepudiation"],
      "issuerAttributes": {
        "C": "TR",
        "L": "xxxxxx",
        "O": "TÜRKTRUST Bilgi İletişim ve Bilişim Güvenliği Hizmetleri A.Ş.",
        "CN": "TÜRKTRUST Nitelikli Elektronik Sertifika Hizmetleri H7",
        "OU": "Dayanak: T.C. 5070 sayılı Elektronik İmza Kanunu"
      },
      "subjectAttributes": {
        "C": "TR",
        "L": "xxxxxx",
        "CN": "xxxxxx xxxx",
        "serialNumber": "xxxxxxxxxxx"
      },
      "crlUrls": ["http://www.turktrust.com.tr/sil/TURKTRUST_Nitelikli_SIL_h7.crl"],
      "ocspUrls": ["http://ocsp.turktrust.com.tr"]
    }
  },
  "revocation": {
    "result": "SUCCESS",
    "policy": "FAIL_CLOSED",
    "crl": {
      "url": "http://www.turktrust.com.tr/sil/TURKTRUST_Nitelikli_SIL_h7.crl",
      "revoked": false,
      "thisUpdate": "2026-01-11T17:01:26Z",
      "nextUpdate": "2026-01-12T17:01:26Z",
      "crlHashSha256Hex": "88fe8b642932bdf7e51a3d83382c66b344ecb90737344bebc633f29179e14a03",
      "crlSignatureValid": true
    },
    "ocsp": {
      "url": null,
      "status": "ERROR",
      "responseSignatureValid": false
    }
  },
  "auditBinding": {
    "bindingType": "LOGIN_CHALLENGE",
    "boundHash": "858a7c57692c4e07451dc0d95914a69623c69015b49c6dd42afd67255b908b73",
    "signatureHash": "2539bcd7895e63c700283219e8dc36a578b579517969857bdb340e5591bbe021",
    "certificateFingerprintSha256": "8ddb3e64548f8c3d8cb36a0e3491d0cc3af37c97d7e0a2221bf293ab16bdf1c2",
    "verifiedAt": "2026-01-11T17:23:43.8718617Z"
  }
}
```

**Yanıt Alanları:**

| Alan | Tip | Açıklama |
|------|-----|----------|
| `v` | number | Yanıt şeması versiyonu |
| `meta` | object | Metadata bilgileri |
| `loginTxId` | string | Login işlemi ID'si |
| `auditId` | string | Audit kayıt ID'si |
| `email` | string | Kullanıcı e-posta adresi |
| `tckn` | string | T.C. kimlik numarasının şifrelenmiş hali |
| `ceptel` | string | Cep telefonu numarası |
| `status` | string | İşlem durumu (SUCCESS, FAILED) |
| `createdAt` | string | İşlem oluşturulma zamanı (ISO 8601) |
| `verifiedAtEpoch` | number | Doğrulama zamanı (Unix epoch, saniye) |
| `txExpiresAtEpoch` | number | İşlem süresi sonu (Unix epoch, saniye) |
| `failReason` | string/null | Başarısız oldu ise hata sebebi |
| `errors` | array/null | Hata detayları |
| `crypto` | object | İmza doğrulama bilgileri |
| `crypto.verifyMethod` | string | Doğrulama yöntemi |
| `crypto.signatureValid` | boolean | İmza geçerli mi |
| `crypto.challengeHashSha256Hex` | string | Challenge'ın SHA256 hash değeri |
| `crypto.signatureHashSha256Hex` | string | İmzanın SHA256 hash değeri |
| `device` | object | Cihaz bilgileri (Sümen uygulaması) |
| `device.deviceId` | string | Benzersiz cihaz ID'si |
| `device.hostName` | string | Bilgisayar adı |
| `device.osName` | string | İşletim sistemi adı |
| `device.osVersion` | string | İşletim sistemi versiyonu |
| `device.appVersion` | string | Sümen uygulaması versiyonu |
| `device.localIp` | string | Cihazın yerel IP adresi |
| `server` | object | Sunucu tarafından gözlemlenen bilgiler |
| `server.publicIp` | string | Halka açık IP adresi |
| `server.userAgent` | string | HTTP User-Agent header |
| `platform` | object | Platform tarafından beyan edilen bilgiler |
| `platform.userInfo` | object | Kullanıcı ortam bilgileri |
| `certificate` | object | Sertifika doğrulama bilgileri |
| `certificate.chainVerified` | boolean | Sertifika zinciri doğrulandı mı |
| `certificate.leaf` | object | Leaf sertifikası bilgileri |
| `certificate.leaf.name` | string | Sertifika sahibi adı |
| `certificate.leaf.tc` | string | Sertifika sahibinin TC numarası |
| `certificate.leaf.validFrom` | string | Sertifika geçerlilik başlangıcı |
| `certificate.leaf.validTo` | string | Sertifika geçerlilik sonu |
| `revocation` | object | Sertifika iptal kontrol bilgileri |
| `revocation.crl` | object | CRL (Certificate Revocation List) bilgileri |
| `revocation.ocsp` | object | OCSP (Online Certificate Status Protocol) bilgileri |
| `auditBinding` | object | Audit ve imza bağlanma bilgileri |
| `auditBinding.bindingType` | string | Bağlanma türü (LOGIN_CHALLENGE vb.) |
| `auditBinding.boundHash` | string | Bağlanan hash değeri |
| `auditBinding.signatureHash` | string | İmza hash değeri |
| `auditBinding.verifiedAt` | string | Doğrulama zamanı |

**Yaygın Olay Türleri:**

| Olay | Açıklama |
|------|----------|
| `LOGIN_TX_CREATED` | Login işlemi oluşturuldu |
| `CHALLENGE_GENERATED` | Challenge üretildi |
| `CHALLENGE_SENT` | Challenge kullanıcıya gönderildi |
| `SIGNATURE_RECEIVED` | İmza alındı |
| `SIGNATURE_VERIFIED` | İmza doğrulandı |
| `ANTI_FRAUD_CHECK` | Anti-fraud kontrolleri çalıştırıldı |
| `LOGIN_COMPLETED` | Login başarıyla tamamlandı |
| `LOGIN_FAILED` | Login başarısız oldu |
| `TIMEOUT` | İşlem zaman aşımına uğradı |

#### Başarısız Yanıt (İşlem Bulunamadı)

**HTTP 404 Not Found**

```json
{
  "error": "NOT_FOUND",
  "message": "Belirtilen login işlemi bulunamadı"
}
```

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/auth/tx/tx_de23d0bf-942f-4c02-a827-a7fb842110ba/audit \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## Hata Yanıtları

### 400 Bad Request

```json
{
  "error": "INVALID_REQUEST",
  "message": "Zorunlu alanlar eksik veya hatalı formatda"
}
```

**Yaygın Hataları:**
- `tckn` 11 haneli olmalıdır
- `platformUserId` boş olamaz
- `userInfo` alanları eksik

### 401 Unauthorized

```json
{
  "error": "UNAUTHORIZED",
  "message": "Geçersiz API credentials"
}
```

### 404 Not Found

```json
{
  "error": "NOT_FOUND",
  "message": "İşlem bulunamadı veya zaman aşımına uğradı"
}
```

### 409 Conflict

```json
{
  "error": "SIGNATURE_MISMATCH",
  "message": "E-imza doğrulanmadı. Sümen uygulamasında imzayı kontrol edin"
}
```

### 500 Internal Server Error

```json
{
  "error": "INTERNAL_ERROR",
  "message": "İşlem sırasında bir hata oluştu"
}
```

---

## Kullanım Örneği

### Adım Adım Login Akışı

```bash
#!/bin/bash

# 1. Login işlemini başlat
RESPONSE=$(curl -X POST https://app.dijitalbelge.com/api/external/auth/tx \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "email": "ahmet@x.com",
    "ceptel": "xxxxxxxxx",
    "tckn": "12345678901",
    "platformUserId": "U-91",
    "userInfo": {
      "ipAddress": "1.2.3.4",
      "userAgent": "Chrome/120 Windows 11",
      "deviceHint": "DESKTOP",
      "locale": "tr-TR",
      "timeZone": "Europe/Istanbul"
    }
  }')

TX_ID=$(echo $RESPONSE | jq -r '.loginTxId')
echo "İşlem başlatıldı: $TX_ID"

# 2. İşlem sonucunu poll et (max 5 dakika)
for i in {1..30}; do
  sleep 5
  
  POLL_RESPONSE=$(curl -X GET https://app.dijitalbelge.com/api/external/auth/tx/$TX_ID \
    -H "X-Client-Id: app_xxxxx" \
    -H "X-Client-Secret: secret_xxxxx")
  
  STATUS=$(echo $POLL_RESPONSE | jq -r '.status')
  
  if [ "$STATUS" = "COMPLETED" ]; then
    LOGIN_TOKEN=$(echo $POLL_RESPONSE | jq -r '.loginToken')
    echo "Login başarılı! Token: $LOGIN_TOKEN"
    break
  elif [ "$STATUS" = "EXPIRED" ]; then
    echo "İşlem zaman aşımına uğradı"
    break
  else
    echo "Bekleniyor... (Deneme $i/30)"
  fi
done
```

---

## İmplementasyon Notları

### Polling Stratejisi

- **Poll Aralığı:** 2-5 saniye
- **Maksimum Süre:** 5 dakika (300 saniye)
- **Timeout Kontrolü:** `expiresIn` değeri kontrol edin

### Güvenlik

!!! warning "Dikkat"
    - `loginToken` güvenli bir şekilde saklayın
    - Token'ı tarayıcı tarafında log etmeyin
    - HTTPS üzerinden iletişim kurun
    - `userInfo.ipAddress` ve `userAgent` doğru gönderilmeli (anti-fraud)

### Entegrasyon Kontrol Listesi

- [ ] Sümen uygulaması kullanıcının bilgisayarına kurulu
- [ ] API credentials (Client ID, Client Secret) alınmış
- [ ] HTTPS bağlantısı yapılandırılmış
- [ ] Hata yönetimi implement edilmiş
- [ ] Polling timeout'u set edilmiş
- [ ] userInfo alanları doğru toplanıyor
- [ ] Login token'ı session'da tutulmuş

---

### Sümen API Referansı

Sümen uygulamasının sunduğu lokal API ve WebSocket protokolleri ayrı bir dokümantasyon ile sağlanacaktır. Entegrasyon sırasında Sümen API dokümanına ihtiyaç duyacaksınız; doküman sağlandığında burada bir bağlantı eklenecektir.


## İlgili Kaynaklar

- [Sumen  API](sumen-api.md)
- [Kimlik Doğrulama](authentication.md)
- [Hata Kodları](errors.md)
