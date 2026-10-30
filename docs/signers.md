---
description: DijitalBelge Signer (İmzacı) API'si ile e-imza ve mobil imza süreçlerine imzacı ekleme, arama ve yönetme uç noktaları.
---

# Signer API (External)

Bu doküman, **Signer (İmzacı)** yönetimi için kullanılan **External Signer API** uç noktalarını açıklar.  
API, entegrasyon uygulamaları tarafından kullanılmak üzere tasarlanmıştır. İmzacı tanımı hesabınızdaki tanımlı ünvanlara yapılır. Tanımlamadan önce ünvan listesini çekmeniz gerekmektedir

---

## Base Path

```
https://app.dijitalbelge.com/api
```
---

## 🔐 Authentication & Authorization

Bu API **OAuth2 kullanmaz**.  
Kimlik doğrulama **Client ID / Client Secret** başlıkları ile yapılır.

### Gerekli HTTP Header’lar

| Header | Açıklama |
|------|---------|
| `X-Client-Id` | Entegrasyon Client ID |
| `X-Client-Secret` | Entegrasyon Client Secret |
| `Content-Type` | `application/json` |

---

### Scope Bazlı Yetkilendirme

| Scope | Açıklama |
|------|---------|
| `signer:read` | İmzacı ve ünvan listesi okuma |
| `signer:managment` | İmzacı ekleme / güncelleme / silme |

---

## 📌 Tanımlı Ünvan Listesi (PartyType)

İmzacı ekleme işleminden önce, hesabınıza tanımlı ünvanların listelenmesi gerekir.

PartyType (Ünvan) listesi **[Reference API](reference-api.md#party-types)** ile çekilir.

**Endpoint:**
```http
GET /external/referance/partytype
```

**Scope:** `signer:read`

**Örnek Yanıt:**
```json
[
  { "id": 1, "name": "Müşteri" },
  { "id": 2, "name": "Çalışan" }
]
```

Daha detaylı bilgi için [Reference API - Party Types](reference-api.md#party-types) sayfasını ziyaret edin.

---

## 📥 Bulk Insert

### Endpoint
```
POST /external/signers/bulk-insert
```

### Required Scope
```
signer:managment
```

### Request Body (Signer List)

İstek gövdesi **Signer** nesnelerinden oluşan bir JSON dizisidir.

### Alanlar

| Alan | Tip | Zorunlu | Açıklama |
|----|----|----|----|
| `fullName` | `String` | ✅ | İmzacının ad soyadı |
| `email` | `String` | ✅ | E-posta adresi |
| `phone` | `String` | ❌ | Telefon numarası |
| `identityNumber` | `String` | ✅ | TCKN / Kimlik No |
| `partyTypeId` | `Long` | ✅ | Ünvan ID |
| `signerType` | `String` | ❌ | İmzacı türü: `INDIVIDUAL` (varsayılan), `CORPORATE` ya da `SEAL` — bkz. [İmzacı türleri](#imzac-turleri) |
| `institutionId` | `Long` | Kurumsalda ⚠️ | Kurumsal imzacının bağlı olduğu, daha önce oluşturulmuş kurum |
| `institutionTitle` | `String` | Kurumsalda ⚠️ | `institutionId` verilmezse yeni kurumun ünvanı |
| `institutionTaxNumber` | `String` | ❌ | Yeni kurumun vergi numarası (10 haneli VKN ya da 11 haneli TCKN) |
| `institutionTaxOffice` | `String` | ❌ | Yeni kurumun vergi dairesi |


> ⚠️ `email`, `fullName`,`partyTypeId` veya `identityNumber` alanlarının **hepsi** dolu olmalıdır.

---

## 🏷️ İmzacı türleri

Her imzacının bir türü vardır. Tür, imzacının kimin adına imzaladığını ve `identityNumber`
alanında ne tutulduğunu belirler.

| `signerType` | Kim | `identityNumber` | Kurum |
|---|---|---|---|
| `INDIVIDUAL` | Kendi adına imzalayan kişi (varsayılan) | Kişinin TCKN'si | Yok |
| `CORPORATE` | Bir kurumun yetkili personeli; kurum adına imzalar | Personelin TCKN'si | Zorunlu: `institutionId` ya da `institutionTitle` |
| `SEAL` | Kurumun elektronik mührü (e-mühür); kişiye değil kuruma aittir | Kurumun VKN'si; şahıs şirketinde TCKN | Yok |

=== "Bireysel"

    ```json
    {
      "signerType": "INDIVIDUAL",
      "fullName": "Ali Veli",
      "email": "ali.veli@example.com",
      "identityNumber": "12345678901",
      "partyTypeId": 6
    }
    ```

=== "Kurumsal (yeni kurum)"

    ```json
    {
      "signerType": "CORPORATE",
      "fullName": "Ayşe Demir",
      "email": "ayse.demir@firma.com.tr",
      "identityNumber": "12345678901",
      "partyTypeId": 6,
      "institutionTitle": "Örnek Teknoloji A.Ş.",
      "institutionTaxNumber": "1234567890",
      "institutionTaxOffice": "Kadıköy"
    }
    ```

=== "Kurumsal (mevcut kurum)"

    ```json
    {
      "signerType": "CORPORATE",
      "fullName": "Mehmet Kaya",
      "email": "mehmet.kaya@firma.com.tr",
      "identityNumber": "10987654321",
      "partyTypeId": 6,
      "institutionId": 41
    }
    ```

=== "Mühür"

    ```json
    {
      "signerType": "SEAL",
      "fullName": "Örnek Teknoloji A.Ş. e-Mühür",
      "email": "muhur@firma.com.tr",
      "identityNumber": "1234567890",
      "partyTypeId": 6
    }
    ```

!!! warning "Aynı kurumu tekrar oluşturmayın"
    `institutionId` olmadan `institutionTitle` gönderilen her istek **yeni bir kurum** kaydı oluşturur.
    İlk imzacıyı eklerken dönen yanıttaki `institutionId` değerini saklayın ve aynı kurumun sonraki
    imzacılarında onu gönderin.

!!! info "Mühür kuralları"
    `SEAL` türünde `identityNumber` zorunludur ve hane kısıtı yoktur (VKN 10, TCKN 11 hane). Kimlik
    kartına özgü alanlar (doğum tarihi, seri no, geçerlilik) kullanılmaz; mühür bir kuruma
    bağlanmaz.

---

## 📦 Örnek Request (Bulk Insert)

```json
[
  {
    "fullName": "Ali Veli",
    "email": "ali.veli@example.com",
    "phone": "+905551112233",
    "identityNumber": "12345678901",
    "partyTypeId": 6
  },
  {
    "fullName": "Ayşe Demir",
    "email": "ayse.demir@example.com",
    "identityNumber": "12345678901",
    "partyTypeId": 6
  }
]
```

### Örnek Response (Success)

```json
{
  "success": true,
  "message": "2 imzacı başarıyla eklendi",
  "insertedCount": 2
}
```

---

## 🔍 Signer Search (Pagination)

### Endpoint
```
GET /external/signers/search
```

### Required Scope
```
signer:read
```

### Query Parameters

| Parametre | Tip | Açıklama |
|---------|----|---------|
| `partyTypeNames` | `List<String>` | Taraf türleri |
| `search` | `String` | Genel arama |
| `fullName` | `String` | Ad Soyad |
| `phone` | `String` | Telefon |
| `email` | `String` | E-posta |
| `identityNumber` | `String` | Kimlik No |
| `page` | `int` | Sayfa |
| `size` | `int` | Boyut |

---

## ✏️ Update Signer

### Endpoint
```
PUT /external/signers/{id}
```

### Required Scope
```
signer:managment
```

### Request Body

| Alan | Tip | Zorunlu | Açıklama |
|----|----|----|----|  
| `fullName` | `String` | ✅ | İmzacının ad soyadı |
| `email` | `String` | ✅ | E-posta adresi |
| `phone` | `String` | ❌ | Telefon numarası |
| `identityNumber` | `String` | ✅ | TCKN / Kimlik No |
| `partyTypeId` | `Long` | ✅ | Taraf tipi ID |
| `signerType` | `String` | ❌ | `INDIVIDUAL`, `CORPORATE` ya da `SEAL`; değiştirilebilir. Kurumsal dışına geçince kurum bağlantısı kaldırılır |
| `institutionId` / `institutionTitle` | | Kurumsalda ⚠️ | Bkz. [İmzacı türleri](#imzac-turleri) |

### Örnek Request

```json
{
  "fullName": "Ali Veli Güncellenmiş",
  "email": "ali.yeni@example.com",
  "phone": "+905551112233",
  "identityNumber": "12345678901",
  "partyTypeId": 6
}
```

### Örnek Response

```json
{
  "id": 1,
  "fullName": "Ali Veli Güncellenmiş",
  "email": "ali.yeni@example.com",
  "phone": "+905551112233",
  "identityNumber": "12345678901",
  "partyTypeId": 6,
  "updatedAt": "2025-12-29T10:30:00Z"
}
```

---

## ❌ Deactivate Signer

### Endpoint
```
DELETE /external/signers/{id}
```

### Required Scope
```
signer:managment
```

### Örnek Response

```json
{
  "success": true,
  "message": "İmzacı başarıyla deaktive edildi",
  "id": 1
}
```

---

## ⚠️ Error Codes

| Code | Açıklama |
|------|---------|
| 400 | Bad Request - Geçersiz istek parametreleri |
| 401 | Unauthorized - Client ID/Secret geçersiz |
| 403 | Forbidden - Yeterli yetki yok |
| 404 | Not Found - Kaynak bulunamadı |
| 409 | Conflict - Duplicate email veya identityNumber |
| 422 | Unprocessable Entity - Validasyon hatası |
| 500 | Server Error - Sunucu hatası |

### Örnek Error Response

```json
{
  "statusCode": 422,
  "message": "Validasyon hatası",
  "errors": [
    {
      "field": "email",
      "message": "Bu email adresine sahip imzacı zaten var"
    }
  ]
}
```
