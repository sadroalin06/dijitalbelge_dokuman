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

### Endpoint

```
GET /external/signers/partytype
```

### Required Scope

```
signer:read
```

### Response Alanları

| Alan | Tip | Açıklama |
|----|----|----|
| `id` | `Long` | Ünvan ID |
| `name` | `String` | Ünvan adı |

### Örnek Response

```json
[
  {
    "id": 1,
    "name": "Müşteri"
  },
  {
    "id": 2,
    "name": "Çalışan"
  }
]
```

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


> ⚠️ `email`, `fullName`,`partyTypeId` veya `identityNumber` alanlarının **hepsi** dolu olmalıdır.

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

## 📥 Bulk Insert

### Endpoint
```
POST /external/signers/bulk-insert
```

### Required Scope
```
signer:managment
```

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
