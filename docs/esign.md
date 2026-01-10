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
| Temel URL | `https://api.dijitalbelge.com/api` |
| Temel Path | `/external` |
| Base URL | `https://api.dijitalbelge.com/api/external` |
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
  "ceptel": "5443476573",
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

Bu endpoint çağrıldıktan sonra entegrasyon platformu `loginTxId`, `challenge` ve `expiresIn` alanlarını alır. `challenge` değeri Sümen tarafına yönlendirilir ve Sümen tarafından kullanıcının e-imzası ile imzalanır. İmzalama tamamlandığında veya kullanıcı onayladığında, üçüncü taraf platform `GET {baseURL}/auth/tx/{loginTxId}/poll` ile sonucu sorgular ve başarılıysa `loginToken` içeren yanıt döner.

#### Örnek cURL

```bash
curl -X POST https://api.dijitalbelge.com/api/external/auth/tx \
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

### 2. İşlem Sonucunu Kontrol Et (Polling)

Login işleminin durumunu kontrol eder. Kullanıcı Sümen'de imzayı onaylayana kadar polling yapılır.

#### İstek

```http
GET {baseURL}/auth/tx/{loginTxId}/poll
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
  "status": "COMPLETED",
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
curl -X GET https://api.dijitalbelge.com/api/external/auth/tx/TX-20260110-ABC123XYZ/poll \
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
  "ceptel": "5443476573",
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

`LoginTxStatus` örnek değerleri: `PENDING`, `VERIFIED` (Sümen tarafından imza doğrulandı ancak login token henüz üretilmedi), `COMPLETED` (loginToken üretildi), `FAILED`, `EXPIRED`.

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
- `ceptel` format hatalı
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
RESPONSE=$(curl -X POST https://api.dijitalbelge.com/api/external/auth/tx \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "email": "ahmet@x.com",
    "ceptel": "5443476573",
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
  
  POLL_RESPONSE=$(curl -X GET https://api.dijitalbelge.com/api/external/auth/tx/$TX_ID \
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

Örnek referans (eklenecek): `sumen-api.md`

## İlgili Kaynaklar

- [Süreç Yönetimi API](progress.md)
- [Kimlik Doğrulama](authentication.md)
- [Hata Kodları](errors.md)
