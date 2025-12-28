# Signer API (External)

Bu doküman, **Signer (İmzacı)** yönetimi için kullanılan **External Signer API** uç noktalarını açıklar.  
API, entegrasyon uygulamaları tarafından kullanılmak üzere tasarlanmıştır.

---

## Base Path

```
/external/signers
```

---

## 🔐 Authentication & Authorization

Bu API **OAuth2 kullanmaz**.  
Kimlik doğrulama **Client ID / Client Secret** başlıkları ile yapılır.

### Zorunlu HTTP Header’lar

| Header | Açıklama |
|------|---------|
| `X-Client-Id` | Entegrasyon Client ID |
| `X-Client-Secret` | Entegrasyon Client Secret |

### Scope Bazlı Yetkilendirme

| Scope | Açıklama |
|------|---------|
| `signer:read` | İmzacı okuma |
| `signer:managment` | İmzacı ekleme / güncelleme / silme |
### Gerekli HTTP Header’lar

| Header | Açıklama |
|------|---------|
| `X-Client-Id` | Entegrasyon Client ID |
| `X-Client-Secret` | Entegrasyon Client Secret |
| `Content-Type` | `application/json` |

---

## 📥 Request Body (SignerDto List)

İstek gövdesi **SignerDto** nesnelerinden oluşan bir JSON dizisidir.

### Alanlar

| Alan | Tip | Zorunlu | Açıklama |
|----|----|----|----|
| `fullName` | `String` | ✅ | İmzacının ad soyadı |
| `email` | `String` | ❌ | E-posta adresi |
| `phone` | `String` | ❌ | Telefon numarası |
| `identityNumber` | `String` | ❌ | TCKN / Kimlik No |
| `partyTypeId` | `Long` | ❌ | Taraf tipi ID |
| `partyTypeName` | `String` | ❌ | Taraf tipi adı |
| `active` | `Boolean` | ❌ | Varsayılan `true` |

> ⚠️ `email`, `phone` veya `identityNumber` alanlarından **en az biri** dolu olmalıdır.

---

## 📦 Örnek Request

```json
[
  {
    "fullName": "Ali Veli",
    "email": "ali.veli@example.com",
    "phone": "+905551112233",
    "identityNumber": "12345678901",
    "partyTypeName": "CUSTOMER"
  },
  {
    "fullName": "Ayşe Demir",
    "email": "ayse.demir@example.com",
    "partyTypeName": "EMPLOYEE"
  }
]

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

---

## ❌ Deactivate Signer

### Endpoint
```
DELETE /external/signers/{id}
```

---

## ⚠️ Error Codes

| Code | Açıklama |
|------|---------|
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |
