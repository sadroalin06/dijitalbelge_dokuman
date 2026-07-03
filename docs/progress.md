# Süreç Yönetimi API

Dijital Belge Sistemi'nde belge işleme süreçlerini yönetmek için kullanılan API'dir.

## Genel Bakış

**Süreç**, imzalama akışının yönetildiği merkezi bir birimdür. Bir süreç içinde:

- **Birden fazla döküman** imzalanabilir veya yüklenebilir
- **Tüm imza akışları** süreç altında gruplanır
- **İmzalama sayfasına** yönlendirme yapılır
- **Benzersiz bir QR kodu** otomatik olarak oluşturulur ve sayfaya basılır

Süreçler **API aracılığıyla oluşturulabilir, yönetilebilir, başlatılabilir, tamamlanabilir veya iptal edilebilir**.

## Özet

| Özellik | Değer |
|---------|-------|
| Temel URL | `https://app.dijitalbelge.com/api` |
| Temel Path | `/external` |
| Base URL | `https://app.dijitalbelge.com/api/external` |
| Kimlik Doğrulama | X-Client-Id, X-Client-Secret |

---

## QR Kod Özelliği

Her oluşturulan sürecin **otomatik olarak benzersiz bir QR kodu** oluşturulur. Bu QR kod:

- **Sürecin kimliğini** taşır ve güvenli bir şekilde kodlanır
- **İmzalama sayfasına basılabilir** ve yazdırılan belgelerde yer alır
- **Mobil cihazlardan** taranarak sürece hızlı erişim sağlar
- **Takip ve doğrulama** amacıyla kullanılır

---

## Endpoint Özeti

| Method | Path | Scope | Açıklama |
|--------|------|-------|----------|
| `POST` | `/process-instances` | `process:start` | Yeni süreç oluştur |
| `GET` | `/process-instances/{processId}` | `process:status` | Süreç detayını getir |
| `PUT` | `/process-instances/{processId}/status/start` | `process:start` | Süreci başlat |
| `PUT` | `/process-instances/{processId}/status/cancel` | `process:start` | Süreci iptal et |
| `PUT` | `/process-instances/{processId}/status/complete` | `process:start` | Süreci tamamla |
| `DELETE` | `/process-instances/{processId}` | `process:start` | Süreci sil |
| `POST` | `/process-instances/{processId}/document/single` | `document:write` | Sürece tekil döküman ekle |
| `POST` | `/process-instances/{processId}/document/document-type` | `process:documenttype:write` | Taslaktan döküman ekle |
| `GET` | `/process-instances/{processId}/document/{documentId}` | `document:read` | Döküman bilgilerini getir |
| `GET` | `/process-instances/{processId}/document/{documentId}/file` | `document:read` | Döküman dosyasını getir (Base64, en son yüklenen hali) |
| `GET` | `/process-instances/{processId}/document/{documentId}/files` | `document:read` | Dökümana bağlı kanıt (EVIDENCE) ve ek (ATTACHMENT) dosyalarının listesini getir |
| `GET` | `/process-instances/{processId}/document/{documentId}/file/{storedFileId}` | `document:read` | Belirli bir dosyayı (ORIGINAL/SIGNED/EVIDENCE/ATTACHMENT) `storedFileId` ile indir (Base64) |
| `DELETE` | `/process-instances/{processId}/document/{documentId}` | `document:write` | Dökümanı sil |
| `POST` | `/process-instances/{processId}/document/{documentId}/signers` | `document:sign` | Dökümana imzacı ekle |
| `DELETE` | `/process-instances/{processId}/document/{documentId}/signer/{signerId}` | `document:sign` | Döküman imzacısını sil |
| `GET` | `/process-instances/{processId}/document/{documentId}/tasks/{taskId}/signature/file` | `document:read` | İmzacının imza kanıt dosyasını (.p7s/JAdES) indir (Base64) |
| `POST` | `/process-instances/{processId}/autosign` | `autosign:write` | Bulut imzalamayı etkinleştir → [detay](autosign.md) |
| `DELETE` | `/process-instances/{processId}/autosign` | `autosign:write` | Bulut imzalamayı devre dışı bırak → [detay](autosign.md) |

---

## Süreç Yönetimi

### 1. Yeni Süreç Oluştur

Yeni bir belge işleme süreci oluşturur.

**Scope:** `process:start`

#### İstek

```http
POST {baseURL}/process-instances
```

**Content-Type:** `application/json`

#### Request Body

```json
{
  "name": "test süreci"
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `name` | string | Hayır | Sürecin adı |

#### Başarılı Yanıt

**HTTP 201 Created**

```json
{
  "id": 147,
  "accountId": 202,
  "createdByUserId": null,
  "name": "Test Süreci",
  "statusCode": "NEW",
  "signers": [],
  "documents": [],
  "createdAt": "2026-01-05T19:59:29.5282888",
  "updatedAt": "2026-01-05T19:59:29.5282888",
  "hasQrCode": false,
  "responsibleBy": null,
  "accessToken": "kQQQioa",
  "tokenExpiry": null
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | number | Sürecin benzersiz ID'si |
| `accountId` | number | Hesap ID'si |
| `createdByUserId` | number | Süreci oluşturan kullanıcı ID'si |
| `name` | string | Sürecin adı |
| `statusCode` | string | Sürecin durum kodu (`NEW`, `STARTED`, `IN_PROGRESS`, `COMPLETED`, `ARCHIVED`, `CANCELED`, `DELETED`) |
| `signers` | array | İmzalayıcılar listesi |
| `documents` | array | Belgeler listesi |
| `createdAt` | string | Oluşturulma tarihi (ISO 8601) |
| `updatedAt` | string | Son güncellenme tarihi (ISO 8601) |
| `hasQrCode` | boolean | QR kod bulunup bulunmadığı |
| `responsibleBy` | string | Sorumlu kişi |
| `accessToken` | string | Erişim token'ı |
| `tokenExpiry` | string | Token geçerlilik süresi |

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "name": "test süreci"
  }'
```

---

### 2. Süreç Detayını Getir

Belirtilen sürecin imzacı ve döküman bilgileriyle birlikte detaylı bilgilerini döndürür.

**Scope:** `process:status`

#### İstek

```http
GET {baseURL}/process-instances/{processId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "id": 147,
  "accountId": 202,
  "createdByUserId": null,
  "name": "Test Süreci",
  "statusCode": "IN_PROGRESS",
  "signers": [
    {
      "id": 1,
      "name": "İmzacı 1",
      "email": "imzaci1@example.com",
      "signedAt": null
    }
  ],
  "documents": [
    {
      "id": 101,
      "name": "Sözleşme.pdf",
      "uploadedAt": "2026-01-05T19:59:29Z"
    }
  ],
  "createdAt": "2026-01-05T19:59:29.5282888",
  "updatedAt": "2026-01-05T19:59:29.5282888",
  "hasQrCode": false,
  "responsibleBy": null,
  "accessToken": "kQQQioa",
  "tokenExpiry": null
}
```

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 3. Süreci Başlat

Belirtilen süreci başlatır. Başlatılan süreç imzacılara bildirim gönderir.

**Scope:** `process:start`

#### İstek

```http
PUT {baseURL}/process-instances/{processId}/status/start
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```
ok
```

#### Örnek cURL

```bash
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/147/status/start \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 4. Süreci İptal Et

Belirtilen süreci iptal eder.

**Scope:** `process:start`

#### İstek

```http
PUT {baseURL}/process-instances/{processId}/status/cancel
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```
ok
```

#### Örnek cURL

```bash
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/147/status/cancel \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 5. Süreci Tamamla

Belirtilen süreci tamamlanmış duruma alır.

**Scope:** `process:start`

#### İstek

```http
PUT {baseURL}/process-instances/{processId}/status/complete
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```
ok
```

#### Örnek cURL

```bash
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/147/status/complete \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 6. Süreci Sil

Belirtilen süreci sistemden siler.

**Scope:** `process:start`

#### İstek

```http
DELETE {baseURL}/process-instances/{processId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Silinecek sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```
(boş)
```

#### Örnek cURL

```bash
curl -X DELETE https://app.dijitalbelge.com/api/external/process-instances/147 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## Döküman Yönetimi

### 7. Sürece Tekil Döküman Ekle

Sürece Base64 formatında bir döküman ekler.

**Scope:** `document:write`

#### İstek

```http
POST {baseURL}/process-instances/{processId}/document/single
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |

#### Request Body

```json
{
  "name": "Sözleşme.pdf",
  "base64": "JVBERi0xLjQK...",
  "fileName": "sozlesme.pdf"
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `name` | string | Evet | Döküman adı |
| `base64` | string | Evet | PDF dosyasının Base64 içeriği |
| `fileName` | string | Evet | Dosya adı |

#### Başarılı Yanıt

**HTTP 201 Created**

```json
{
  "id": 7203,
  "name": "Sözleşme.pdf",
  "statusCode": "PENDING",
  "createdAt": "2026-01-05T20:00:00"
}
```

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/147/document/single \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "name": "Sözleşme.pdf",
    "base64": "JVBERi0xLjQK...",
    "fileName": "sozlesme.pdf"
  }'
```

---

### 8. Taslaktan Döküman Ekle

Tanımlı bir döküman taslağını kullanarak sürece belge ekler. Taslak ID'si ile imzacı bilgileri gönderilir.

**Scope:** `process:documenttype:write`

#### İstek

```http
POST {baseURL}/process-instances/{processId}/document/document-type
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |

#### Request Body

```json
{
  "id": 22,
  "name": "Ticari İletişim İzni",
  "isSign": true,
  "isApprove": true,
  "isUpload": false,
  "document": {
    "base64": "",
    "fileName": "deneme.pdf"
  },
  "signings": [
    {
      "id": 14,
      "signer": {
        "id": 138
      }
    }
  ]
}
```

Detaylı alan açıklamaları için [Taslaktan Döküman Ekleme](progress_doctype.md) sayfasını inceleyin.

#### Başarılı Yanıt

**HTTP 201 Created**

```json
{
  "id": 7203
}
```

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/147/document/document-type \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "id": 22,
    "signings": [{ "id": 14, "signer": { "id": 138 } }]
  }'
```

---

### 9. Döküman Bilgilerini Getir

Süreçteki belirli bir dökümanın detay bilgilerini döndürür.

**Scope:** `document:read`

#### İstek

```http
GET {baseURL}/process-instances/{processId}/document/{documentId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "id": 7203,
  "name": "Sözleşme.pdf",
  "statusCode": "SIGNED",
  "signers": [
    {
      "id": 1,
      "signerName": "Ali Veli",
      "signedAt": "2026-01-06T10:00:00"
    }
  ],
  "createdAt": "2026-01-05T20:00:00",
  "updatedAt": "2026-01-06T10:00:00"
}
```

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147/document/7203 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 10. Döküman Dosyasını Getir (Base64)

Sürece ait dökümanın en son yüklü halini Base64 formatında döndürür.

**Scope:** `document:read`

#### İstek

```http
GET {baseURL}/process-instances/{processId}/document/{documentId}/file
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "accountId": 202,
  "processId": 147,
  "documentId": 7203,
  "fileName": "sozlesme.pdf",
  "content": "JVBERi0xLjQK...",
  "contentType": "application/pdf",
  "signtaskId": 0,
  "filekey": "documents/202/7203/sozlesme.pdf",
  "evidenceJadesBytes": null,
  "evidenceJadesFileName": null,
  "attachments": null,
  "taskIds": null
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `accountId` | number | Hesap ID'si |
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |
| `fileName` | string | Dosya adı |
| `content` | string | Dosyanın Base64 içeriği (`byte[]` alanı Jackson tarafından otomatik Base64'e çevrilir) |
| `contentType` | string | Dosya MIME türü |
| `signtaskId` | number | Bu endpoint için kullanılmaz (her zaman `0`) |
| `filekey` | string | Dosyanın depolama sistemindeki anahtarı (bilgi amaçlı, entegrasyonlarda kullanılmamalı) |
| `evidenceJadesBytes` | string \| null | Bu endpoint için kullanılmaz (`null`) |
| `evidenceJadesFileName` | string \| null | Bu endpoint için kullanılmaz (`null`) |
| `attachments` | array \| null | Bu endpoint için kullanılmaz (`null`) |
| `taskIds` | array \| null | Bu endpoint için kullanılmaz (`null`) |

> ℹ️ Bu yanıt şeması aynı şekilde **"Belirli Bir Dosyayı İndir (storedFileId ile)"** ve **"İmza Dosyasını İndir"** uç noktaları için de geçerlidir.

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147/document/7203/file \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 11. Döküman Dosyalarını Listele (Kanıt ve Ekler)

Dökümana bağlı **EVIDENCE** (kanıt) ve **ATTACHMENT** (ek) dosyalarının metadata listesini döndürür. Ana döküman dosyası (ORIGINAL/SIGNED) bu listeye dahil değildir — onun için **"Döküman Dosyasını Getir (Base64)"** kullanılır.

**Scope:** `document:read`

#### İstek

```http
GET {baseURL}/process-instances/{processId}/document/{documentId}/files
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
[
  {
    "id": 501,
    "fileType": "EVIDENCE",
    "storedFileId": 9001,
    "fileName": "video_kaniti.mp4",
    "filePath": "/external/process-instances/147/document/7203/file/9001",
    "contentType": "video/mp4",
    "size": 1048576,
    "linkedAt": "2026-01-06T10:00:05",
    "isCurrentVersion": null,
    "isOldsign": null,
    "archivedDocumentId": null
  },
  {
    "id": 502,
    "fileType": "ATTACHMENT",
    "storedFileId": 9002,
    "fileName": "ek_belge.pdf",
    "filePath": "/external/process-instances/147/document/7203/file/9002",
    "contentType": "application/pdf",
    "size": 204800,
    "linkedAt": "2026-01-06T10:00:10",
    "isCurrentVersion": null,
    "isOldsign": null,
    "archivedDocumentId": null
  }
]
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | number | Dosya bağlantı kaydının ID'si |
| `fileType` | string | Dosya türü: `EVIDENCE` (imzalama sırasında oluşan kanıt, örn. video) veya `ATTACHMENT` (dökümanla birlikte CAdES ile imzalanan ek) |
| `storedFileId` | number | Dosyayı indirmek için **"Belirli Bir Dosyayı İndir (storedFileId ile)"** uç noktasında kullanılacak ID |
| `fileName` | string | Dosya adı |
| `filePath` | string | Dosyayı indirmek için kullanılacak API path'i |
| `contentType` | string | Dosya MIME türü |
| `size` | number | Dosya boyutu (byte) |
| `linkedAt` | string | Dosyanın dökümana bağlandığı tarih (ISO 8601) |
| `isCurrentVersion`, `isOldsign`, `archivedDocumentId` | - | Bu endpoint için kullanılmaz (her zaman `null`) |

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147/document/7203/files \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 12. Belirli Bir Dosyayı İndir (storedFileId ile)

Yukarıdaki listeden dönen `storedFileId` ile ilgili dosyayı (`ORIGINAL`, `SIGNED`, `EVIDENCE` ya da `ATTACHMENT` türlerinden herhangi biri) Base64 formatında indirir. Yanıt şeması **"Döküman Dosyasını Getir (Base64)"** ile aynıdır.

**Scope:** `document:read`

#### İstek

```http
GET {baseURL}/process-instances/{processId}/document/{documentId}/file/{storedFileId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |
| `storedFileId` | number | İndirilecek dosyanın ID'si (döküman listesinden veya `/files` uç noktasından alınır) |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "accountId": 202,
  "processId": 147,
  "documentId": 7203,
  "fileName": "video_kaniti.mp4",
  "content": "AAAAIGZ0eXBpc29t...",
  "contentType": "video/mp4",
  "signtaskId": 0,
  "filekey": "documents/202/7203/evidence/video_kaniti.mp4",
  "evidenceJadesBytes": null,
  "evidenceJadesFileName": null,
  "attachments": null,
  "taskIds": null
}
```

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147/document/7203/file/9001 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 13. Dökümanı Sil

Süreçten belirli bir dökümanı kaldırır.

**Scope:** `document:write`

#### İstek

```http
DELETE {baseURL}/process-instances/{processId}/document/{documentId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Silinecek dökümanın ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```
Döküman Silindi
```

#### Örnek cURL

```bash
curl -X DELETE https://app.dijitalbelge.com/api/external/process-instances/147/document/7203 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## Döküman İmzacı Yönetimi

### 14. Dökümana İmzacı Ekle

Belirtilen dökümana yeni bir imzacı görevi ekler.

**Scope:** `document:sign`

#### İstek

```http
POST {baseURL}/process-instances/{processId}/document/{documentId}/signers
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |

#### Request Body

```json
{
  "signerId": 138,
  "signerName": "Ali Veli",
  "order": 1,
  "isRequired": true,
  "signatureType": {
    "code": "TCKK_ONBOARDING"
  },
  "promptText": "Lütfen adınızı ve soyadınızı okuyun",
  "videoMaxDurationSeconds": 60,
  "signer": {
    "fullName": "Ali Veli",
    "identityNumber": "12345678901",
    "birthDate": "1990-05-15",
    "expiredDate": "2030-01-01",
    "tcSerial": "A1B2C3D4",
    "phone": "+905551112233",
    "email": "ali.veli@example.com"
  }
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `signerId` | number | Evet | İmzacının ID'si |
| `signerName` | string | Hayır | İmzacının adı |
| `order` | number | Hayır | İmzalama sırası |
| `isRequired` | boolean | Hayır | İmza zorunlu mu |
| `signatureType` | object | Hayır | İmza türü bilgisi |
| `signatureType.code` | string | Hayır | İmza türü kodu (örn: `TCKK_ONBOARDING`) |
| `promptText` | string | Hayır | Video imzalama için imzacıya gösterilecek yönerge metni |
| `videoMaxDurationSeconds` | number | Hayır | Video imzalama için maksimum süre (saniye) |
| `signer` | object | Hayır | İmzacı kimlik bilgileri (TCKK doğrulama akışı için) |
| `signer.fullName` | string | Hayır | İmzacının ad soyadı |
| `signer.identityNumber` | string | Hayır | T.C. Kimlik Numarası (11 haneli) |
| `signer.birthDate` | string | Hayır | Doğum tarihi (`YYYY-MM-DD`) |
| `signer.expiredDate` | string | Hayır | Kimlik belgesinin son geçerlilik tarihi (`YYYY-MM-DD`) |
| `signer.tcSerial` | string | Hayır | TC kimlik kartı seri numarası |
| `signer.phone` | string | Hayır | Telefon numarası |
| `signer.email` | string | Hayır | E-posta adresi |

> ℹ️ `signer` nesnesi, `TCKK_ONBOARDING` gibi kimlik doğrulama gerektiren imza türlerinde kullanılır. Standart imzalama akışlarında bu alan zorunlu değildir.

!!! warning "Önemli: `order` (İmzalama Sırası)"
    `order` alanı imzacıların sırasını belirler. **İmzalama ekranında yalnızca sırası gelen imzacı görünür.**

    - `order: 1` olan imzacı ilk sırada olduğu için süreci açtığında kendisini imzalayacak kişi olarak görür.
    - `order: 2` olan imzacı, 1. sıradaki imzacı imzasını tamamlayana kadar imzalama ekranında **görünmez**.

    **Abonelik akışı örneği:**
    ```
    Abone     → order: 1  (mobil uygulamada süreci açtığında kendini görür)
    İşletmeci → order: 2  (abone imzaladıktan sonra sırası gelir)
    ```

    `order` girilmezse imzacı imzalama ekranında **hiç görünmez**.

#### Başarılı Yanıt

**HTTP 201 Created**

```json
{
  "id": 5,
  "documentInstanceId": 7203,
  "signerId": 138,
  "signerName": "Ali Veli",
  "order": 1,
  "statusCode": "PENDING",
  "signatureType": {
    "code": "TCKK_ONBOARDING"
  },
  "promptText": "Lütfen adınızı ve soyadınızı okuyun",
  "videoMaxDurationSeconds": 60,
  "signer": {
    "fullName": "Ali Veli",
    "identityNumber": "12345678901",
    "birthDate": "1990-05-15",
    "expiredDate": "2030-01-01",
    "tcSerial": "A1B2C3D4",
    "phone": "+905551112233",
    "email": "ali.veli@example.com"
  },
  "createdAt": "2026-01-05T20:00:00"
}
```

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/147/document/7203/signers \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "signerId": 138,
    "order": 1,
    "isRequired": true,
    "signatureType": { "code": "TCKK_ONBOARDING" },
    "promptText": "Lütfen adınızı ve soyadınızı okuyun",
    "videoMaxDurationSeconds": 60,
    "signer": {
      "fullName": "Ali Veli",
      "identityNumber": "12345678901",
      "birthDate": "1990-05-15",
      "expiredDate": "2030-01-01",
      "tcSerial": "A1B2C3D4",
      "phone": "+905551112233",
      "email": "ali.veli@example.com"
    }
  }'
```

---

### 15. Döküman İmzacısını Sil

Belirtilen döküman üzerindeki imzacı görevini kaldırır.

**Scope:** `document:sign`

#### İstek

```http
DELETE {baseURL}/process-instances/{processId}/document/{documentId}/signer/{signerId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |
| `signerId` | number | Kaldırılacak imzacının ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```
İmzacı Silindi
```

#### Örnek cURL

```bash
curl -X DELETE https://app.dijitalbelge.com/api/external/process-instances/147/document/7203/signer/138 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 16. İmza Dosyasını İndir

İmzacının görevi tamamlarken oluşturduğu imza kanıt dosyasını (`.p7s` / JAdES) Base64 formatında indirir. `taskId`, **"Dökümana İmzacı Ekle"** yanıtındaki `id` alanıyla aynıdır. Yanıt şeması **"Döküman Dosyasını Getir (Base64)"** ile aynıdır; ancak `documentId` bu uç nokta için her zaman `0` döner.

**Scope:** `document:read`

#### İstek

```http
GET {baseURL}/process-instances/{processId}/document/{documentId}/tasks/{taskId}/signature/file
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |
| `taskId` | number | İmzalama görevinin (imzacının) ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "accountId": 202,
  "processId": 147,
  "documentId": 0,
  "fileName": "imza_kaniti.p7s",
  "content": "MIIGCwYJKoZIhvcNAQcC...",
  "contentType": "application/pkcs7-signature",
  "signtaskId": 0,
  "filekey": "signatures/202/7203/5/imza_kaniti.p7s",
  "evidenceJadesBytes": null,
  "evidenceJadesFileName": null,
  "attachments": null,
  "taskIds": null
}
```

#### Hata Durumları

| Durum | Açıklama |
|-------|----------|
| 404 | İmzalama görevi bulunamadı |
| 404 | Görev bu sürece ait değil |
| 404 | Yetki hatası (hesap uyuşmazlığı) |
| 404 | Bu göreve ait imza dosyası bulunamadı (imzacı henüz imzalamamış) |

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147/document/7203/tasks/5/signature/file \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## Otomatik İmzalama

Bulut İmzalama (Autosign) endpoint'leri bu sayfadan ayrılmış olup ayrıntılar için [Bulut İmzalama (Autosign)](autosign.md) sayfasını inceleyin.

---

## Süreç Durumları

| Durum | Açıklama |
|-------|----------|
| `NEW` | İlk oluşturulduğunda atanan durum |
| `STARTED` | Başlayınca imzacılara bildirim gider |
| `IN_PROGRESS` | İlk imzacı imzaladığında süreç devam ediyor durumuna geçer |
| `COMPLETED` | Tüm imzacılar imzalamayı tamamladığında süreç tamamlanır |
| `ARCHIVED` | Tamamlanan süreçler, arşiv hizmeti alınmış ise arşive taşınır |
| `CANCELED` | Süreç iptal edilmiş durumda |
| `DELETED` | Süreç silinmiş durumda |

---

## Hata Yanıtları

### 400 Bad Request

```json
{
  "error": "INVALID_REQUEST",
  "message": "Request parametreleri hatalı"
}
```

### 401 Unauthorized

```json
{
  "error": "UNAUTHORIZED",
  "message": "Geçersiz veya eksik kimlik doğrulama"
}
```

### 403 Forbidden

```json
{
  "error": "FORBIDDEN",
  "message": "Bu işlem için yeterli yetki yok veya IP adresi yetkisiz"
}
```

### 404 Not Found

```json
{
  "error": "NOT_FOUND",
  "message": "İstenilen süreç bulunamadı"
}
```

### 409 Conflict

```json
{
  "error": "CONFLICT",
  "message": "Sürecin mevcut durumunda bu işlem gerçekleştirilemez"
}
```

### 500 Internal Server Error

```json
{
  "error": "INTERNAL_ERROR",
  "message": "Sunucuda bir hata oluştu"
}
```

---

## Kullanım Örnekleri

### Tam Akış Örneği

```bash
# 1. Yeni süreç oluştur
PROCESS_ID=$(curl -s -X POST https://app.dijitalbelge.com/api/external/process-instances \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"name":"test süreci"}' | jq -r '.id')

# 2. Dökümana imzacı ekle
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/document/7203/signers \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"signerId": 138, "order": 1}'

# 3. Süreci başlat
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/status/start \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"

# 4. Süreci tamamla
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/status/complete \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## Kimlik Doğrulama

DijitalBelge External API'ye yapılan tüm istekler **entegrasyon bazlı kimlik doğrulama** ile korunmaktadır. API'yi kullanabilmek için size özel `ClientId` ve `ClientSecret` bilgileri gerekmektedir.

### Yetkilendirme Header'ları

Tüm API isteklerine aşağıdaki header'ları eklemeniz zorunludur:

| Header | Açıklama |
|--------|----------|
| `X-Client-Id` | Entegrasyon Client ID |
| `X-Client-Secret` | Entegrasyon Client Secret |

!!! warning
    `X-Client-Secret` bilgisi gizli tutulmalı ve herkese açık ortamlarda saklanmamalıdır.

### Örnek İstekler

=== "cURL"

    ```bash
    curl -X POST https://app.dijitalbelge.com/api/external/process-instances \
      -H "X-Client-Id: app_xxxxx" \
      -H "X-Client-Secret: secret_xxxxx" \
      -H "Content-Type: application/json" \
      -d '{"name":"test süreci"}'
    ```

=== "Java"

    ```java
    HttpHeaders headers = new HttpHeaders();
    headers.set("X-Client-Id", "app_xxxxx");
    headers.set("X-Client-Secret", "secret_xxxxx");
    ```

=== "JavaScript"

    ```javascript
    fetch("https://app.dijitalbelge.com/api/external/process-instances", {
      method: "POST",
      headers: {
        "X-Client-Id": "app_xxxxx",
        "X-Client-Secret": "secret_xxxxx",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({name: "test süreci"})
    });
    ```

=== "Python"

    ```python
    import requests

    headers = {
        "X-Client-Id": "app_xxxxx",
        "X-Client-Secret": "secret_xxxxx"
    }

    requests.post(
        "https://app.dijitalbelge.com/api/external/process-instances",
        headers=headers,
        json={"name": "test süreci"}
    )
    ```

Daha fazla bilgi için [Kimlik Doğrulama](authentication.md) sayfasını ziyaret edin.

---

## Sınırlamalar

- Her API çağrısı için maksimum 30 saniye timeout vardır
- Dakika başına maksimum 100 istek yapılabilir
- Süreç adı maksimum 255 karakterden oluşabilir

---

## İlgili Kaynaklar

- [API Referansı](reference-api.md)
- [Kimlik Doğrulama](authentication.md)
- [Hata Kodları](errors.md)
- [Taslaktan Döküman Ekleme](progress_doctype.md)
- [İmzacı Yönetimi](signers.md)
