# Döküman API

Bu döküman, bir **süreç (process)** içindeki dökümanları ve döküman imzacılarını yönetmek için kullanılan API uç noktalarını açıklar. Döküman eklemeden önce ilgili sürecin oluşturulmuş olması gerekir — bkz. [Süreç API](progress.md).

## Özet

| Özellik | Değer |
|---------|-------|
| Temel URL | `https://app.dijitalbelge.com/api` |
| Temel Path | `/external` |
| Base URL | `https://app.dijitalbelge.com/api/external` |
| Kimlik Doğrulama | X-Client-Id, X-Client-Secret |

---

## Endpoint Özeti

| Method | Path | Scope | Açıklama |
|--------|------|-------|----------|
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

---

## `visibleSignature` Nesnesi (İmza / Alan Konumu)

`visibleSignature`, bir imzanın veya metin/QR alanının PDF üzerinde **nerede ve nasıl** görüneceğini tanımlar. Bir belgeye imzacı eklenen **her uç noktada** kullanılabilir:

- [Sürece Tekil Döküman Ekle](#1-surece-tekil-dokuman-ekle) — `signings[].visibleSignature`, `adds[].visibleSignature`
- [Taslaktan Döküman Ekle](progress_doctype.md#imzac-tanm-signings) — `signings[].visibleSignature` (taslakta konum tanımlıysa opsiyonel, override için kullanılabilir)
- [Dökümana İmzacı Ekle](#8-dokumana-imzac-ekle) — `visibleSignature` (taslak bağlantısı olmadığından **zorunludur**)

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `pageNumber` | Integer | Hayır | İmzanın/alanın basılacağı PDF sayfa numarası |
| `originX` | Integer | Hayır | Sayfa üzerindeki X koordinatı |
| `originY` | Integer | Hayır | Sayfa üzerindeki Y koordinatı |
| `width` | Integer | Hayır | Alanın genişliği |
| `height` | Integer | Hayır | Alanın yüksekliği |
| `data` | String | Hayır | `image: false` ise belge üzerinde görünecek metin (ör. `"Genel Müdür Ali Veli"`) — E-İmza ve Mobil İmza için kullanılır. `image: true` ise bu alana görselleştirilecek imza resmi **Base64** olarak gönderilir |
| `image` | Boolean | Hayır | `data` alanının nasıl yorumlanacağını belirler: `true` ise `data` bir Base64 **resim**, `false`/belirtilmezse `data` bir **metin**dir |
| `fontSize` | Integer | Hayır | Metin font boyutu |
| `textColor` | String | Hayır | Metin rengi (hex, ör. `#000000`) |
| `backgroundColor` | String | Hayır | Arka plan rengi (hex, ör. `#ffffff`) |
| `alignment` | String (enum) | Hayır | Metin/alan hizalaması: `LEFTTOP`, `CENTER`, `RIGHTBOTTOM` |

!!! note "`data` / `image` İlişkisi"
    - **E-İmza / Mobil İmza:** `image: false` (veya belirtilmezse) `data`, belge üzerinde görünecek **isim/ünvan metnidir** (ör. `"Genel Müdür Ali Veli"`).
    - `image: true` verilirse `data` alanına, belge üzerinde görselleştirilecek **imza resmi Base64** olarak gönderilir.

!!! warning "`visibleSignature` zorunludur"
    `visibleSignature` gönderilmezse istek **hata** ile sonuçlanır.

---

## Döküman Yönetimi

### 1. Sürece Tekil Döküman Ekle

Sürece Base64 formatında bir döküman ekler. İsteğe bağlı `signings` ve `adds` alanları doldurulursa, herhangi bir **Döküman Taslağı (DocumentType)**'na referans vermeden, bu belgeye özel **tek kullanımlık** imzacı ve alan (metin/QR) yapısı tanımlanır — kalıcı bir DocumentType kaydı oluşturulmaz. Bu alanlar boş/`null` bırakılırsa mevcut davranış (imzacı/alan ataması yapılmaz) aynen devam eder.

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
  "fileName": "sozlesme.pdf",
  "signings": [
    {
      "signer": { "id": 138 },
      "stepOrder": 1
    },
    {
      "signer": {
        "fullName": "Ali Veli",
        "email": "ali.veli@example.com",
        "phone": "+905551112233",
        "identityNumber": "12345678901"
      },
      "stepOrder": 2,
      "signatureType": { "id": 3 }
    }
  ],
  "adds": [
    {
      "addType": "QR",
      "docqr": false,
      "visibleSignature": { "pageNumber": 1, "originX": 400, "originY": 50, "width": 80, "height": 80 }
    }
  ]
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `name` | string | Evet | Döküman adı |
| `base64` | string | Evet | PDF dosyasının Base64 içeriği |
| `fileName` | string | Evet | Dosya adı |
| `signings` | array | Hayır | Bu belgeye özel, tek kullanımlık imzacı tanımları. Bkz. [signings alanı](#signings-tek-kullanımlık-imzacı-tanımı) |
| `adds` | array | Hayır | Bu belgeye özel, tek kullanımlık metin/QR alan tanımları. Bkz. [adds alanı](#adds-tek-kullanımlık-metinqr-alan-tanımı) |

##### `signings` (Tek Kullanımlık İmzacı Tanımı)

Her eleman, belgeye bir imza görevi ekler.

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `signer` | object | **Evet** | İmzacı bilgisi (aşağıya bakın) |
| `stepOrder` | number | Hayır | İmzalama ekranında görünme sırası. **Belirtilmezse, `signings` dizisindeki sırasına göre otomatik olarak 1'den başlayarak atanır** (yani boş bırakmak imzacıyı görünmez yapmaz — bu davranış [Taslaktan Döküman Ekleme](progress_doctype.md)'deki `signings.stepOrder` kuralından farklıdır) |
| `signatureType` | object | Hayır | `{ "id": <SignatureType ID> }`. Belirtilmezse varsayılan olarak **EIMZA** kullanılır |
| `visibleSignature` | object | **Evet** | İmza/metin görünürlük konumu — bkz. [`visibleSignature` Nesnesi](#visiblesignature-nesnesi-imza-alan-konumu). **Belirtilmezse istek hata verir.** |
| `promptText` | string | Hayır | Yalnızca `signatureType` `TCKK_ONBOARDING` ise kullanılır — imzacıya gösterilecek yönerge metni |
| `videoMaxDurationSeconds` | number | Hayır | Yalnızca `signatureType` `TCKK_ONBOARDING` ise kullanılır. Belirtilmezse varsayılan **30** |

**`signer` nesnesi — imzacı çözümleme kuralları:**

| Alan | Açıklama |
|------|----------|
| `id` | Doluysa hesaba kayıtlı **mevcut bir imzacı** referans alınır; diğer alanlar yok sayılır |
| `userId` | `id` boşken doluysa, sistem kullanıcısı ile ilişkili **dahili imzacı** oluşturulur; ad/e-posta/telefon/TC bilgisi bu kullanıcıdan alınır (aşağıdaki alanlar yok sayılır) |
| `fullName`, `email`, `phone`, `identityNumber` | `id` ve `userId` boşsa, bu alanlarla **yeni harici imzacı** oluşturulur |
| `partyTypeId` | Hayır — belirtilmezse varsayılan `1` kullanılır |

!!! warning "signer zorunludur"
    Her `signings` elemanında `signer` alanı gönderilmelidir; boş geçilirse istek `400 Bad Request` ile reddedilir.

##### `adds` (Tek Kullanımlık Metin/QR Alan Tanımı)

Her eleman, belgeye bir metin veya QR alanı ekler (döküman taslağındaki `DocumentTypeAdd` yapısının tek kullanımlık karşılığıdır).

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `addType` | string | Hayır | `TEXT` veya `QR` |
| `content` | string | Hayır | Sabit içerik. `addType: "QR"` iken boş bırakılırsa, otomatik olarak sürecin imzalama linkine (`/sign/{token}`) yönlenen bir QR üretilir |
| `fieldName` | string | Hayır | Alanı dinamik bir form değeriyle eşlemek için kullanılan anahtar |
| `docqr` | boolean | Hayır | Bu alanın belge doğrulama QR'ı olarak işaretlenip işaretlenmeyeceği |
| `visibleSignature` | object | Hayır | Alanın belge üzerindeki konumu — bkz. [`visibleSignature` Nesnesi](#visiblesignature-nesnesi-imza-alan-konumu) |

> ℹ️ `storeadd` alanı bu endpoint için desteklenmez; gönderilse dahi her zaman `false` olarak işlenir.

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

### 2. Taslaktan Döküman Ekle

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

### 3. Döküman Bilgilerini Getir

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

### 4. Döküman Dosyasını Getir (Base64)

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

### 5. Döküman Dosyalarını Listele (Kanıt ve Ekler)

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

### 6. Belirli Bir Dosyayı İndir (storedFileId ile)

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

### 7. Dökümanı Sil

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
(boş)
```

#### Örnek cURL

```bash
curl -X DELETE https://app.dijitalbelge.com/api/external/process-instances/147/document/7203 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## Döküman İmzacı Yönetimi

### 8. Dökümana İmzacı Ekle

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
  "visibleSignature": {
    "pageNumber": 1,
    "originX": 35,
    "originY": 416,
    "width": 200,
    "height": 75,
    "data": "Ali Veli",
    "image": false,
    "fontSize": 14,
    "textColor": "#000000",
    "backgroundColor": "#ffffff",
    "alignment": "CENTER"
  },
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
| `visibleSignature` | object | **Evet** | İmzanın belge üzerindeki konumu — bkz. [`visibleSignature` Nesnesi](#visiblesignature-nesnesi-imza-alan-konumu). **Belirtilmezse istek hata verir.** |
| `signer` | object | Hayır | İmzacı kimlik bilgileri (TCKK doğrulama akışı için) |
| `signer.fullName` | string | Hayır | İmzacının ad soyadı |
| `signer.identityNumber` | string | Hayır | T.C. Kimlik Numarası (11 haneli) |
| `signer.birthDate` | string | Hayır | Doğum tarihi (`YYYY-MM-DD`) |
| `signer.expiredDate` | string | Hayır | Kimlik belgesinin son geçerlilik tarihi (`YYYY-MM-DD`) |
| `signer.tcSerial` | string | Hayır | TC kimlik kartı seri numarası |
| `signer.phone` | string | Hayır | Telefon numarası |
| `signer.email` | string | Hayır | E-posta adresi |

> ℹ️ `signer` nesnesi, `TCKK_ONBOARDING` gibi kimlik doğrulama gerektiren imza türlerinde kullanılır. Standart imzalama akışlarında bu alan zorunlu değildir.

!!! warning "Önemli: `visibleSignature` (İmza Konumu) zorunludur"
    Bu endpoint ile eklenen imzacı, döküman taslağındaki önceden tanımlı bir `signings` sırasına bağlı **değildir** — bu yüzden imzanın PDF üzerinde nereye basılacağı taslak tarafından otomatik belirlenmez. **`visibleSignature` (`pageNumber`, `originX`, `originY`, `width`, `height`) gönderilmezse istek hata verir.**

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
  "visibleSignature": {
    "id": 7554,
    "pageNumber": 1,
    "originX": 35,
    "originY": 416,
    "width": 200,
    "height": 75
  },
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
    "visibleSignature": {
      "pageNumber": 1,
      "originX": 35,
      "originY": 416,
      "width": 200,
      "height": 75
    },
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

### 9. Döküman İmzacısını Sil

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

### 10. İmza Dosyasını İndir

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

## Hata Yanıtları

Genel hata yanıt biçimleri için bkz. [Süreç API – Hata Yanıtları](progress.md#hata-yanıtları).

---

## İlgili Kaynaklar

- [Süreç API](progress.md)
- [Taslaktan Döküman Ekleme](progress_doctype.md)
- [API Referansı](reference-api.md)
- [Hata Kodları](errors.md)
