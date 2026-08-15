# Süreç Yönetimi API

Dijital Belge Sistemi'nde belge işleme süreçlerini yönetmek için kullanılan API'dir.

## Genel Bakış

**Süreç**, imzalama akışının yönetildiği merkezi bir birimdür. Bir süreç içinde:

- **Birden fazla döküman** imzalanabilir veya yüklenebilir
- **Tüm imza akışları** süreç altında gruplanır
- **İmzalama sayfasına** yönlendirme yapılır
- **Benzersiz bir QR kodu** otomatik olarak oluşturulur ve sayfaya basılır

Süreçler **API aracılığıyla oluşturulabilir, yönetilebilir, başlatılabilir, tamamlanabilir veya iptal edilebilir**.

---

## Süreç Tipleri (processType)

Bir sürecin nasıl işleyeceğini `processType` alanı belirler. Süreç oluşturulurken bu alan gönderilmezse **varsayılan olarak `BELGE_IMZALAMA` kullanılır**.

| Değer | Açıklama |
|-------|----------|
| `BELGE_IMZALAMA` | **(Varsayılan)** Belge üzerinde PDF imzalama işlemi yapılır. İmzacılar, dökümanı `DocumentSigningTask` üzerinden PDF olarak imzalar. |
| `DIJITAL_ONAY` | Metin tabanlı dijital onay işlemi yapılır. Onaylayan kişi metni onaylar; onay dosyası oluşturularak metne bağlanır. |
| `DOSYA_IMZALAMA` | Herhangi bir dosya türü (PDF, DOCX, XML vb.) CAdES ayrık imzayla imzalanır. Sürece eklenen tüm belgeler, tüm imzacılar tarafından imzalanır. Her imza `.p7s` formatında ayrık olarak saklanır. |
| `DIJITAL_KIMLIK_DOGRULAMA` | Belge imzalanmaz; bir kişinin kimliği TCKK NFC çip okuma + yüz/video doğrulama ile teyit edilir. İmzacı gizli bir "signing control" belgesine bağlanır, gerçek bir dosya üretilmez. |

!!! info "Varsayılan Değer"
    `processType` alanı **"Yeni Süreç Oluştur"** isteğinde gönderilmezse süreç otomatik olarak `BELGE_IMZALAMA` tipinde oluşturulur.

---

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
| `POST` | `/process-instances/{processId}/autosign` | `autosign:write` | Bulut imzalamayı etkinleştir → [detay](autosign.md) |
| `DELETE` | `/process-instances/{processId}/autosign` | `autosign:write` | Bulut imzalamayı devre dışı bırak → [detay](autosign.md) |

> ℹ️ Döküman ekleme/silme, döküman dosyası indirme ve döküman imzacı yönetimi uç noktaları için bkz. [Döküman API](documents.md).

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
  "name": "test süreci",
  "processType": "BELGE_IMZALAMA"
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `name` | string | Hayır | Sürecin adı |
| `processType` | string | Hayır | Süreç tipi. **Gönderilmezse varsayılan olarak `BELGE_IMZALAMA` kullanılır.** Olası değerler için [Süreç Tipleri](#süreç-tipleri-processtype) bölümüne bakın. |

#### Başarılı Yanıt

**HTTP 201 Created**

```json
{
  "id": 147,
  "accountId": 202,
  "createdByUserId": null,
  "name": "Test Süreci",
  "statusCode": "NEW",
  "processType": "BELGE_IMZALAMA",
  "signers": [],
  "documents": [],
  "createdAt": "2026-01-05T19:59:29.5282888",
  "updatedAt": "2026-01-05T19:59:29.5282888",
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
| `processType` | string | Süreç tipi (bkz. [Süreç Tipleri](#süreç-tipleri-processtype)). Belirtilmemişse `BELGE_IMZALAMA` |
| `signers` | array | İmzalayıcılar listesi |
| `documents` | array | Belgeler listesi |
| `createdAt` | string | Oluşturulma tarihi (ISO 8601) |
| `updatedAt` | string | Son güncellenme tarihi (ISO 8601) |
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

## Döküman ve Döküman İmzacı Yönetimi

Sürece döküman ekleme/silme, döküman ve ilişkili dosyaları (kanıt/ek) indirme ve döküman bazlı imzacı yönetimi işlemleri ayrı bir sayfaya taşınmıştır: **[Döküman API](documents.md)**.

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

- [Döküman API](documents.md)
- [API Referansı](reference-api.md)
- [Kimlik Doğrulama](authentication.md)
- [Hata Kodları](errors.md)
- [Taslaktan Döküman Ekleme](progress_doctype.md)
- [İmzacı Yönetimi](signers.md)
