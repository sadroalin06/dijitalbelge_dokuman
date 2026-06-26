# Reference API (External)

Bu döküman **External API** için kullanılacak referans değerlerin listesini verir. Bu tüm apilerde ortak kullanılan alanları API ile çekebilirsiniz.
## Base Path

```
https://app.dijitalbelge.com/api/external/referance
```

## Authentication

Yetkilendirme için header da Client ID ve Client Secret kullanılır.

| Header | Description |
|------|-------------|
| X-Client-Id | Integration Client ID |
| X-Client-Secret | Integration Client Secret |

## Scopes

| Scope | Description |
|------|-------------|
| signer:read | Read party types |
| documenttype:read | Read document types |

## Party Types

### GET /partytype

Hesabınızdaki tanımlı ünvanlar listelenir

**Scope:** signer:read

```json
[
  { "id": 1, "name": "Signer" },
  { "id": 2, "name": "Witness" }
]
```

## Döküman Taslakları

### GET /documenttype

Hesapda tanımlı döküman taslakları listelenir

```json
[
  {
    "id": 1,
    "name": "Contract",
    "description": "Standard contract",
    "isSign": true,
    "isForm": false
  }
]
```

## İmzalama Türleri

### GET /signaturetype

Kullanılabilir imzalama türleri listelenir

**Scope:** documenttype:read

```json
[
  {
    "id": 1,
    "name": "Eimza",
    "code": "EIMZA",
    "description": "Elektronik İmza"
  },
  {
    "id": 5,
    "name": "E-Posta ile Dijital Onay",
    "code": "EMAIL_TIMESTAMP",
    "description": "E-Posta Islem Onayı"
  },
  {
    "id": 11,
    "name": "Kimlik(TCKK) ile Dijital Onay",
    "code": "TCKK_TIMESTAMP",
    "description": "Kimlik(TCKK) kartı Islem Onayı"
  },
  {
    "id": 13,
    "name": "SMSOTP ile Doğrulama",
    "code": "SMSOTP_TIMESTAMP",
    "description": "SMS OTP ile İmza"
  },
  {
    "id": 14,
    "name": "Mobil İmza",
    "code": "MOBILE_IMZA",
    "description": "Mobil İmza"
  },
  {
    "id": 15,
    "name": "TCKK ve Yüz tanıma Dijital İmza",
    "code": "TCKK_FACE_TIMESTAMP",
    "description": "Çipli Kimlik Kartı + yüz tanıma ile İmza"
  },
  {
    "id": 16,
    "name": "TCKK+Yüz Tanıma Videolu Dijital İmza",
    "code": "TCKK_ONBOARDING",
    "description": "Kimlik Kartı NFC + Fotoğraf + Video ile Kimlik Doğrulama"
  }
]
```

**Response Alanları:**

| Alan | Tip | Açıklama |
|------|-----|---------|
| `id` | number | İmza tipi ID |
| `code` | string | İmzalama türü kodu |
| `name` | string | İmza türü adı |
| `description` | string | İmza türü açıklaması |

