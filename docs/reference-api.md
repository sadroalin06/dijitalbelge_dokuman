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

```json
[
  { "id": 1, "code": "E_SIGNATURE", "name": "Elektronik İmza" },
  { "id": 2, "code": "EMAIL_TIMESTAMP", "name": "Email üzerinden Dijital Onay" }
]
```
| Alan | Açıklama |
|----|---------|
| id | imza tipi ID |
| code | İmzalama türü kodu|
| name | İmza ismi |

