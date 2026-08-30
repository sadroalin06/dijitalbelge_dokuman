---
description: Süreç Taslakları API — hazır süreç şablonlarını (ProcessDefinition) API ile listeleme ve bir taslaktan tek adımda süreç başlatma.
---

# Süreç Taslakları API

**Süreç taslağı (ProcessDefinition)**, panelde tanımlanan hazır bir imza akışıdır:
hangi belgelerin süreçte yer alacağı, her belgenin imza adımları (taraf tipi / ünvan
ya da sabit imzacı), imza türleri ve varsa dinamik form alanları taslakta tanımlıdır.

Bu API ile:

- Hesaptaki taslakları **listeleyebilir** ve detayını görebilirsiniz
- Bir taslaktan **tek adımda süreç başlatabilirsiniz** (belge ekleme + imzacı atama +
  başlatma tek istekte)

---

## Özet

| Özellik | Değer |
|---------|-------|
| Base URL | `https://app.dijitalbelge.com/api/external` |
| Base Path | `/process-definitions` |
| Kimlik Doğrulama | `X-Client-Id`, `X-Client-Secret` |

## Endpoint Özeti

| Method | Path | Scope | Açıklama |
|--------|------|-------|----------|
| `GET` | `/process-definitions` | `process:status` | Taslakları listele |
| `GET` | `/process-definitions/{definitionId}` | `process:status` | Taslak detayı |
| `POST` | `/process-definitions/{definitionId}/start` | `process:start` | Taslaktan süreç başlat |

---

## 1. Taslakları Listele

Hesaba ait, silinmemiş tüm süreç taslaklarını döndürür.

**Scope:** `process:status`

### İstek

```http
GET {baseURL}/process-definitions
```

### Başarılı Yanıt

**HTTP 200 OK**

```json
[
  {
    "id": 12,
    "name": "Görev Belgesi Süreci",
    "description": "",
    "processType": "BELGE_IMZALAMA",
    "allowedPartyIds": [3, 11],
    "documentRequirements": [
      {
        "id": 88,
        "documentTypeId": 45,
        "documentTypeName": "Görev Belgesi",
        "documentTypeisSign": true,
        "signatureTypeId": 1,
        "required": false,
        "mustBeSigned": true,
        "mustBeApproved": false,
        "signings": [
          {
            "id": 210,
            "stepOrder": 1,
            "partyType": { "id": 11, "name": "Personel" },
            "signatureType": { "id": 1, "name": "Eimza" },
            "signer": null
          }
        ]
      }
    ]
  }
]
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | number | Taslak ID (`definitionId`) |
| `name` / `description` | string | Taslak adı ve açıklaması |
| `processType` | string | Bu taslaktan oluşacak süreçlerin tipi (bkz. [Süreç Tipleri](progress.md#süreç-tipleri-processtype)) |
| `allowedPartyIds` | number[] | İzin verilen taraf tipi (ünvan) ID'leri |
| `documentRequirements[]` | array | Süreçte yer alacak belgeler |
| `documentRequirements[].documentTypeId` | number | Belge taslağı ID |
| `documentRequirements[].signings[]` | array | Belgenin imza adımları |
| `signings[].partyType` | object\|null | Adımın taraf tipi (ünvan). Başlatırken bu taraf tipine imzacı atanır |
| `signings[].signer` | object\|null | **Adıma sabit imzacı tanımlıysa** dolu gelir. Bu durumda o adım için başlatırken imzacı atamaya gerek yoktur |
| `signings[].signatureType` | object\|null | Adımın imza türü |

> Public başlatma linki alanları (`publicToken` vb.) bu yanıtta gösterilmez.

### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-definitions \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## 2. Taslak Detayı

**Scope:** `process:status`

### İstek

```http
GET {baseURL}/process-definitions/{definitionId}
```

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `definitionId` | number | Taslak ID |

Yanıt, listedeki tek bir eleman ile aynı yapıdadır. Bulunamazsa `404`.

---

## 3. Taslaktan Süreç Başlat

Belirtilen taslaktan **tek bir süreç** oluşturur: taslağın belge gereksinimleri
kopyalanır, imza görevleri aşağıdaki öncelikle atanır ve istenirse süreç başlatılır.

**İmzacı atama önceliği (her imza adımı için):**

1. `documentSignerOverrides[documentTypeId]` — istekteki override
2. `signings[].signer` — taslaktaki **sabit imzacı**
3. `signers[]` içinden adımın `partyType`'ına eşleşen imzacı (taraf tipi çözümü)

**Scope:** `process:start`

### İstek

```http
POST {baseURL}/process-definitions/{definitionId}/start
```

**Content-Type:** `application/json`

### Request Body

```json
{
  "name": "Görev Belgesi - Ali Veli",
  "autoStart": true,
  "responsibleId": null,
  "signers": [
    { "signerId": 138, "partyTypeId": 11 }
  ],
  "documentSignerOverrides": { "45": 99 },
  "formValues": {
    "ad_soyad": "Ali Veli",
    "gorevbas": "2026-09-01"
  },
  "formDesignIds": []
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `name` | string | Hayır | Sürecin adı. Boşsa taslak adı + imzacı adı kullanılır |
| `autoStart` | boolean | Hayır | `true` ise süreç oluşturulduktan hemen sonra `STARTED` durumuna alınır ve sıradaki imzacıya bildirim gider. `false`/boş ise süreç `NEW` durumunda kalır |
| `responsibleId` | number | Hayır | Süreçten sorumlu panel kullanıcısı ID'si |
| `signers[]` | array | Şarta bağlı | Taraf tipi (ünvan) bazında imzacılar. Taslaktaki her `partyType`'lı imza adımı için bir `{ signerId, partyTypeId }` gönderin. **Tüm imza adımlarında `signer` (sabit imzacı) tanımlıysa gönderilmesi gerekmez** |
| `signers[].signerId` | number | Evet | Hesabın imzacı rehberindeki `Signer` ID'si (bkz. [İmzacı API](signers.md)) |
| `signers[].partyTypeId` | number | Evet | Bu imzacının karşılık geldiği taraf tipi ID'si |
| `documentSignerOverrides` | object | Hayır | `{ "<documentTypeId>": <signerId> }` — o belgenin imza adım(lar)ındaki imzacıyı değiştirir (taslaktaki sabit imzacı dahil) |
| `formValues` | object | Hayır | Belgelerdeki `{{alan}}` yer tutucularına / form alanlarına işlenecek değerler. `autoStart` sırasında belgelere uygulanır |
| `formDesignIds` | number[] | Hayır | Sürece bağlanacak form tasarımı ID'leri |

### Başarılı Yanıt

**HTTP 201 Created** — oluşan sürecin detayı (`autoStart: true` ise imzacılarla birlikte):

```json
{
  "id": 148,
  "name": "Görev Belgesi - Ali Veli",
  "statusCode": "STARTED",
  "processType": "BELGE_IMZALAMA",
  "accessToken": "aB3xk9Q",
  "signers": [
    { "id": 401, "fullName": "Ali Veli", "email": "ali.veli@example.com", "signedAt": null }
  ],
  "documents": [
    { "id": 7310, "name": "Görev Belgesi", "uploaded": true, "signed": false }
  ]
}
```

### Hata Durumları

| HTTP Kodu | Açıklama |
|-----------|----------|
| 400 | İmzacı çözülemedi (ne `signers` ne sabit imzacı verildi), geçersiz `signerId`, iş kuralı hatası |
| 401 | Kimlik doğrulama bilgisi yok |
| 403 | `process:start` scope yok / paket yetersiz |
| 404 | Taslak bu hesaba ait değil / bulunamadı |

### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-definitions/12/start \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "autoStart": true,
    "signers": [ { "signerId": 138, "partyTypeId": 11 } ],
    "formValues": { "ad_soyad": "Ali Veli" }
  }'
```

---

## Tam Akış Örneği

```bash
BASE="https://app.dijitalbelge.com/api/external"
AUTH=(-H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx")

# 1. Taslakları listele, kullanılacak definitionId + partyTypeId'leri bul
curl -s "${AUTH[@]}" "$BASE/process-definitions"

# 2. Gerekli imzacıyı oluştur / bul (bkz. İmzacı API)
SIGNER_ID=$(curl -s "${AUTH[@]}" -H "Content-Type: application/json" \
  -X POST "$BASE/signers/bulk-insert" \
  -d '[{"fullName":"Ali Veli","email":"ali@x.com","identityNumber":"12345678901","partyTypeId":11}]' \
  | jq -r '.[0].id')

# 3. Taslaktan süreci başlat
curl -s "${AUTH[@]}" -H "Content-Type: application/json" \
  -X POST "$BASE/process-definitions/12/start" \
  -d "{\"autoStart\":true,\"signers\":[{\"signerId\":$SIGNER_ID,\"partyTypeId\":11}]}"
```

---

## İlgili Kaynaklar

- [Referans API](reference-api.md) — taraf tipleri, imza türleri, form tasarımları, belge taslakları
- [İmzacı API](signers.md) — imzacı oluşturma / arama
- [Süreç API](progress.md) — süreç durumu, QR, iptal/tamamla
- [Döküman API](documents.md) — belge dosyalarını indirme
