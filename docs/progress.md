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
| Temel URL | `https://api.dijitalbelge.com/api` |
| Temel Path | `/external` |
| Base URL | `https://api.dijitalbelge.com/api/external` |
| Kimlik Doğrulama | X-Client-Id, X-Client-Secret |

---

## QR Kod Özelliği

Her oluşturulan sürecin **otomatik olarak benzersiz bir QR kodu** oluşturulur. Bu QR kod:

- **Sürecin kimliğini** taşır ve güvenli bir şekilde kodlanır
- **İmzalama sayfasına basılabilir** ve yazdırılan belgelerde yer alır
- **Mobil cihazlardan** taranarak sürece hızlı erişim sağlar
- **Takip ve doğrulama** amacıyla kullanılır

s
---

## Endpoints

### 1. Yeni Süreç Oluştur

Yeni bir belge işleme süreci oluşturur.

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
| `name` | string | Evet | Sürecin adı |

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
| `statusCode` | string | Sürecin durum kodu (NEW, STARTED, IN_PROGRESS, COMPLETED, ARCHIVED, CANCELED, DELETED) |
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
curl -X POST https://api.dijitalbelge.com/api/external/process-instances \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "name": "test süreci"
  }'
```

---

### 2. Süreci Başlat

Belirtilen süreci başlatır.

#### İstek

```http
PUT {baseURL}/process-instances/{processId}/status/start
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | string | Sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "id": "proc-12345",
  "name": "test süreci",
  "status": "STARTED",
  "startedAt": "2026-01-10T10:31:00Z"
}
```

#### Örnek cURL

```bash
curl -X PUT https://api.dijitalbelge.com/api/external/process-instances/proc-12345/status/start \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 3. Süreci İptal Et

Belirtilen süreci iptal eder.

#### İstek

```http
PUT {baseURL}/process-instances/{processId}/status/cancel
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | string | Sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "id": "proc-12345",
  "name": "test süreci",
  "status": "CANCELLED",
  "cancelledAt": "2026-01-10T10:32:00Z"
}
```

#### Örnek cURL

```bashdijitalbelge.com/api/external/process-instances/proc-12345/status/cancel \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxxi/external/process-instances/proc-12345/status/cancel \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Süreci Tamamla

Belirtilen süreci tamamlanan duruma alır.

#### İstek

```hhttps://api.dijitalbelge.comttp
PUT /api/external/process-instances/{processId}/status/complete
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | string | Sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "id": "proc-12345",
  "name": "test süreci",
  "status": "COMPLETED",
  "completedAt": "2026-01-10T10:33:00Z"
}
```

#### Örnek cURL

```bash
curl -X PUT https://api.dijitalbelge.com/api/external/process-instances/proc-12345/status/complete \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 5. Süreç Detayını Getir

Belirtilen sürecin detaylı bilgilerini döndürür.

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

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | number | Sürecin benzersiz ID'si |
| `accountId` | number | Hesap ID'si |
| `createdByUserId` | number | Süreci oluşturan kullanıcı ID'si |
| `name` | string | Sürecin adı |
| `statusCode` | string | Sürecin durum kodu |
| `signers` | array | İmzalayan taraflar listesi |
| `documents` | array | Sürece ait belgeler listesi |
| `createdAt` | string | Oluşturulma tarihi |
| `updatedAt` | string | Son güncellenme tarihi |
| `hasQrCode` | boolean | QR kod bulunup bulunmadığı |
| `responsibleBy` | string | Sorumlu kişi |
| `accessToken` | string | Erişim token'ı |
| `tokenExpiry` | string | Token geçerlilik süresi |

#### Örnek cURL

```bash
curl -X GET https://api.dijitalbelge.com/api/external/process-instances/147 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

### 6. Süreci Sil

Belirtilen süreci sistemden siler.

#### İstek

```http
DELETE {baseURL}/process-instances/{processId}
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Silinecek sürecin ID'si |

#### Başarılı Yanıt

**HTTP 204 No Content**

Başarılı silme işleminden sonra hiçbir içerik döndürülmez.

#### Örnek cURL

```bash
curl -X DELETE https://api.dijitalbelge.com/api/external/process-instances/147 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

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
PROCESS_ID=$(curl -X POST https://api.dijitalbelge.com/api/external/process-instances \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"name":"test süreci"}' | jq -r '.id')

# 2. Süreci başlat
curl -X PUT https://api.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/status/start \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"

# 3. Süreci tamamla
curl -X PUT https://api.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/status/complete \
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
    curl -X POST https://api.dijitalbelge.com/api/external/process-instances \
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
    fetch("https://api.dijitalbelge.com/api/external/process-instances", {
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
        "https://api.dijitalbelge.com/api/external/process-instances",
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
