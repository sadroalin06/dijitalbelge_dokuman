---
description: Mobil İmza ile Login API — üçüncü taraf uygulamalara mobil imza kullanarak kimlik doğrulama ve giriş (login) entegrasyonu sağlayan DijitalBelge API'si.
---

# Mobil İmza ile Login API

Üçüncü taraf platformların kendi kullanıcılarını Dijital Belge sistemi ile mobil imza kullanarak giriş yaptırmak için kullandığı API'dir.

## Genel Bakış

### Mobil İmza Nedir?

**Mobil İmza**, GSM operatörleri tarafından sunulan ve SIM kart tabanlı çalışan yasal bir elektronik imza yöntemidir:

- **SIM kartı üzerinde çalışır** - Telefona ek bir uygulama kurulması gerekmez
- **GSM operatörü altyapısı kullanır** - Turkcell, Vodafone, Türk Telekom gibi operatörler üzerinden çalışır
- **PIN ile imzalama** - Kullanıcı, telefonuna gelen isteği PIN kodu ile onaylar
- **Yasal geçerlilik** - 5070 sayılı Elektronik İmza Kanunu kapsamında nitelikli elektronik imza sayılır

### Login Akışı

```
1. Üçüncü Taraf Platform
   ↓
2. Kullanıcı Bilgisi Topla (TC, Email, Telefon, Operatör vb.)
   ↓
3. Operatör Listesini Çek (/external/auth/operators)
   ↓
4. Dijital Belge API'sine Gönder (/external/auth/{operator}/mobiltx)
   ↓
5. Dijital Belge, GSM operatörüne imza isteği gönderir
   ↓
6. Kullanıcının telefonuna imza isteği gelir ve PIN ile onaylar
   ↓
7. Platform /external/auth/{operator}/mobil/{loginTxId} ile durumu polling yapar
   ↓
8. İmza başarıyla onaylandığında Dijital Belge bir auditlog oluşturur
   ↓
9. Platform elindeki token ile Dijital Belge platformunda auditlogu okur ve kullanıcısını login yapar
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

### 1. Desteklenen Operatörleri Listele

Sistemin desteklediği GSM operatörlerinin listesini döndürür. Mobil imza işlemi başlatmadan önce bu endpoint çağrılarak desteklenen operatörler öğrenilmelidir.

#### İstek

```http
GET {baseURL}/auth/operators
```

#### Başarılı Yanıt

**HTTP 200 OK**

```json
[
  "TURKCELL",
  "TURK_TELEKOM",
  "VODAFONE"
]
```

Dönen değerler, diğer endpoint'lerde `{operator}` path parametresi olarak kullanılır.

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/auth/operators \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 2. Mobil İmza ile Login İşlemi Başlat

Kullanıcı bilgilerini ve seçilen operatörü gönderip mobil imza ile login işlemini başlatır. Bu çağrı başarılı olduğunda GSM operatörü kullanıcının telefonuna imza isteği gönderir.

#### İstek

```http
POST {baseURL}/auth/{operator}/mobiltx
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `operator` | string | Operatör kodu (önceki endpoint'ten alınan `operatorCode`, örn: `TURKCELL`) |

**Content-Type:** `application/json`

#### Request Body

```json
{
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
  "loginTxId": "mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9",
  "challenge": "v8RAgZcFlbLjbkwwrG+2h6+DNsjSVjF81KIm2cxWrNk=",
  "expiresIn": 120
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `loginTxId` | string | Mobil imza işlem kimliği |
| `challenge` | string | Operatör tarafından imzalanacak challenge (base64) |
| `expiresIn` | number | İşlemin geçerlilik süresi (saniye) |

Bu endpoint çağrıldıktan sonra kullanıcının telefonuna GSM operatörü üzerinden bir imza isteği gönderilir. Kullanıcı telefonda PIN girerek isteği onaylar. Platform bu sürede `loginTxId` ile polling yaparak sonucu kontrol eder.

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/auth/TURKCELL/mobiltx \
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

### 3. İmza Durumunu Kontrol Et

Mobil imza işleminin durumunu kontrol eder. Kullanıcı telefonunda PIN girip imzayı onaylayana kadar polling yapılır.

#### İstek

```http
GET {baseURL}/auth/{operator}/mobil/{loginTxId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `operator` | string | Operatör kodu (örn: `TURKCELL`) |
| `loginTxId` | string | İşlem ID'si (önceki endpoint'ten döndürülen, örn: `mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9`) |

#### Başarılı Yanıt (İmza Bekleniyor)

**HTTP 200 OK**

```json
{
  "loginTxId": "mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9",
  "operator": "TURKCELL",
  "status": "PENDING",
  "message": "İmza onayı bekleniyor",
  "expiresIn": 85,
  "timestamp": "2026-01-10T12:31:00.123Z"
}
```

#### Başarılı Yanıt (İmza Onaylandı)

**HTTP 200 OK**

```json
{
  "loginTxId": "mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9",
  "operator": "TURKCELL",
  "status": "USED",
  "message": "Mobil imza başarıyla doğrulandı",
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
| `operator` | string | Kullanılan GSM operatörü |
| `status` | string | İşlem durumu (`PENDING`, `USED`, `EXPIRED`) |
| `message` | string | Durum mesajı |
| `loginToken` | string | Login token'ı — yalnızca `status: USED` iken döner |
| `user` | object | Doğrulanan kullanıcı bilgileri — yalnızca `status: USED` iken döner |
| `user.id` | string | Platform kullanıcı ID'si |
| `user.email` | string | Kullanıcı email'i |
| `user.tckn` | string | T.C. Kimlik numarası |
| `user.signatureVerified` | boolean | Mobil imza doğrulandı mı |
| `expiresIn` | number | İşlemin kalan geçerlilik süresi (saniye) |
| `timestamp` | string | Cevap zamanı |

**`status` Değerleri:**

| Değer | Açıklama |
|-------|----------|
| `PENDING` | İmza isteği gönderildi, kullanıcı henüz onaylamadı |
| `USED` | Kullanıcı mobil imzayı onayladı, işlem başarıyla tamamlandı |
| `EXPIRED` | İşlem zaman aşımına uğradı veya kullanıcı reddetti |

#### Başarısız Yanıt (İşlem Zaman Aşımı)

**HTTP 410 Gone**

```json
{
  "loginTxId": "mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9",
  "operator": "TURKCELL",
  "status": "EXPIRED",
  "message": "İşlem zaman aşımına uğradı. Lütfen tekrar deneyin",
  "timestamp": "2026-01-10T12:35:45.123Z"
}
```

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/auth/TURKCELL/mobil/mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 4. Audit Log Çekme

Belirtilen mobil imza login işlemi için tüm audit log kayıtlarını ve işlem geçmişini döndürür.

#### İstek

```http
GET {baseURL}/auth/tx/{loginTxId}/audit
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `loginTxId` | string | Mobil imza işlem ID'si (örn: `mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9`) |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "v": 1,
  "meta": {
    "schemaVersion": 1,
    "revocationResult": "SUCCESS"
  },
  "loginTxId": "mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9",
  "auditId": "271ac190-554b-41df-0b84-980444ca9a7f",
  "email": "ahmet@x.com",
  "tckn": "xxxxxxxxxxxxxxxxxxx",
  "ceptel": "xxxxxxxxxxxx",
  "operator": "TURKCELL",
  "status": "SUCCESS",
  "createdAt": "2026-01-11T17:23:36.3341608Z",
  "verifiedAtEpoch": 1768152216,
  "txExpiresAtEpoch": 1768152302,
  "failReason": null,
  "errors": null,
  "policy": "FAIL_CLOSED",
  "mobile": {
    "verifyMethod": "MOBILE_SIGNATURE",
    "signatureValid": true,
    "operator": "TURKCELL",
    "msisdn": "905441234567"
  },
  "server": {
    "secure": "SERVER_OBSERVED",
    "publicIp": "1.2.3.4",
    "userAgent": "Chrome/120 Windows 11"
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
    "leaf": {
      "name": "XXXX XXXX",
      "tc": "XXXXXXXXX",
      "email": "xxxxx@xxxxx.xxx",
      "serialNumber": "xxxxxxxxxxxxxx",
      "version": "3",
      "validFrom": "2025-02-11T10:40:06.000+00:00",
      "validTo": "2026-02-11T10:40:06.000+00:00",
      "publicKeyAlgorithm": "RSA",
      "signatureAlgorithm": "SHA384withECDSA",
      "keyUsages": ["digitalSignature", "nonRepudiation"],
      "issuerAttributes": {
        "C": "TR",
        "O": "Turkcell İletişim Hizmetleri A.Ş.",
        "CN": "Turkcell Mobil İmza CA"
      },
      "subjectAttributes": {
        "C": "TR",
        "CN": "XXXX XXXX",
        "serialNumber": "xxxxxxxxxxx"
      }
    }
  },
  "revocation": {
    "result": "SUCCESS",
    "policy": "FAIL_CLOSED",
    "ocsp": {
      "url": "http://ocsp.turkcell.com.tr",
      "status": "GOOD",
      "responseSignatureValid": true
    }
  },
  "auditBinding": {
    "bindingType": "MOBILE_CHALLENGE",
    "boundHash": "858a7c57692c4e07451dc0d95914a69623c69015b49c6dd42afd67255b908b73",
    "signatureHash": "2539bcd7895e63c700283219e8dc36a578b579517969857bdb340e5591bbe021",
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
| `operator` | string | Kullanılan GSM operatörü |
| `status` | string | İşlem durumu (SUCCESS, FAILED) |
| `createdAt` | string | İşlem oluşturulma zamanı (ISO 8601) |
| `verifiedAtEpoch` | number | Doğrulama zamanı (Unix epoch, saniye) |
| `txExpiresAtEpoch` | number | İşlem süresi sonu (Unix epoch, saniye) |
| `failReason` | string/null | Başarısız oldu ise hata sebebi |
| `errors` | array/null | Hata detayları |
| `mobile` | object | Mobil imza doğrulama bilgileri |
| `mobile.verifyMethod` | string | Doğrulama yöntemi |
| `mobile.signatureValid` | boolean | İmza geçerli mi |
| `mobile.operator` | string | GSM operatörü |
| `mobile.msisdn` | string | Kullanıcının MSISDN numarası |
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
| `revocation.ocsp` | object | OCSP (Online Certificate Status Protocol) bilgileri |
| `auditBinding` | object | Audit ve imza bağlanma bilgileri |
| `auditBinding.bindingType` | string | Bağlanma türü (MOBILE_CHALLENGE) |
| `auditBinding.boundHash` | string | Bağlanan hash değeri |
| `auditBinding.signatureHash` | string | İmza hash değeri |
| `auditBinding.verifiedAt` | string | Doğrulama zamanı |

**Yaygın Olay Türleri:**

| Olay | Açıklama |
|------|----------|
| `MOBILE_TX_CREATED` | Mobil imza işlemi oluşturuldu |
| `OPERATOR_REQUEST_SENT` | Operatöre imza isteği gönderildi |
| `MOBILE_SIGNATURE_PENDING` | Kullanıcının telefonuna istek iletildi, onay bekleniyor |
| `MOBILE_SIGNATURE_RECEIVED` | Kullanıcı imzayı onayladı |
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
curl -X GET https://app.dijitalbelge.com/api/external/auth/tx/mobiltx_882ee773-7905-49b9-b688-7d0b6230c9b9/audit \
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

**Yaygın Hatalar:**
- `tckn` 11 haneli olmalıdır
- `ceptel` geçerli bir GSM numarası olmalıdır
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
  "message": "Mobil imza doğrulanmadı. Operatör ile iletişim kurun"
}
```

### 422 Unprocessable Entity

```json
{
  "error": "OPERATOR_ERROR",
  "message": "GSM operatörü isteği işleyemedi. Kullanıcının mobil imza hizmeti aktif olmayabilir"
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

# 1. Desteklenen operatörleri listele
OPERATORS=$(curl -s -X GET https://app.dijitalbelge.com/api/external/auth/operators \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx")

echo "Desteklenen operatörler: $OPERATORS"

# 2. Mobil imza işlemini başlat (TURKCELL örneği)
RESPONSE=$(curl -s -X POST https://app.dijitalbelge.com/api/external/auth/TURKCELL/mobiltx \
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
  }')

TX_ID=$(echo $RESPONSE | jq -r '.loginTxId')
echo "Mobil imza isteği gönderildi: $TX_ID"
echo "Kullanıcı telefonunda PIN girmeyi bekliyor..."

# 3. İmza durumunu poll et (max 2 dakika)
for i in {1..24}; do
  sleep 5

  POLL_RESPONSE=$(curl -s -X GET \
    "https://app.dijitalbelge.com/api/external/auth/TURKCELL/mobil/$TX_ID" \
    -H "X-Client-Id: app_xxxxx" \
    -H "X-Client-Secret: secret_xxxxx")

  STATUS=$(echo $POLL_RESPONSE | jq -r '.status')

  if [ "$STATUS" = "USED" ]; then
    LOGIN_TOKEN=$(echo $POLL_RESPONSE | jq -r '.loginToken')
    echo "Mobil imza başarılı! Token: $LOGIN_TOKEN"
    break
  elif [ "$STATUS" = "EXPIRED" ]; then
    echo "İşlem zaman aşımına uğradı"
    break
  else
    echo "Bekleniyor... (Deneme $i/24)"
  fi
done
```

---

## İmplementasyon Notları

### Polling Stratejisi

- **Poll Aralığı:** 3-5 saniye
- **Maksimum Süre:** 2 dakika (120 saniye)
- **Timeout Kontrolü:** `expiresIn` değeri kontrol edin

### Güvenlik

!!! warning "Dikkat"
    - `loginToken` güvenli bir şekilde saklayın
    - Token'ı tarayıcı tarafında log etmeyin
    - HTTPS üzerinden iletişim kurun
    - `userInfo.ipAddress` ve `userAgent` doğru gönderilmeli (anti-fraud)
    - Kullanıcının seçtiği operatör ile kayıtlı telefon numarası uyuşmalıdır

### Entegrasyon Kontrol Listesi

- [ ] Kullanıcının GSM operatörü tespit edilmiş (listeden seçtirilmiş)
- [ ] Kullanıcının mobil imza hizmeti GSM operatöründe aktif
- [ ] API credentials (Client ID, Client Secret) alınmış
- [ ] HTTPS bağlantısı yapılandırılmış
- [ ] Hata yönetimi implement edilmiş (özellikle `OPERATOR_ERROR`)
- [ ] Polling timeout'u set edilmiş
- [ ] userInfo alanları doğru toplanıyor
- [ ] Login token'ı session'da tutulmuş

---

## İlgili Kaynaklar

- [E-İmza Login API](esign.md)
- [Kimlik Doğrulama](authentication.md)
- [Hata Kodları](errors.md)
