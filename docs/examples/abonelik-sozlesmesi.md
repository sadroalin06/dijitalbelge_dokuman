# Abonelik Sözleşmesi İmzalama

Bu örnek, arayüzden yüklenen bir **Abonelik Sözleşmesi** taslağının API aracılığıyla imzalatılmasını adım adım açıklar.

İki farklı senaryo ele alınmaktadır:

| Senaryo | Abone İmza Yöntemi | İşletmeci |
|---------|-------------------|-----------|
| [**Senaryo A**](#senaryo-a-her-iki-taraf-e-imza-ile-imzalar) | E-İmza | E-İmza |
| [**Senaryo B**](#senaryo-b-abone-yapay-zeka-ile-kimlik-dogrulamayla-imzalar) | Yapay Zeka Kimlik Doğrulama (TCKK) | E-İmza |

---

## Ön Koşullar

- Abonelik Sözleşmesi döküman taslağı arayüzden sisteme yüklenmiş olmalıdır.
- Taslak ID'si ve imzalama sırası (signing ID'leri) [Referans API](../reference-api.md) üzerinden öğrenilmiş olmalıdır.
- İşletmeci, sistemde tanımlı bir imzacı olmalıdır (`signerId`).

---

## Senaryo A: Her İki Taraf E-İmza ile İmzalar

```
Süreç Oluştur → Taslaktan Döküman Ekle → Süreci Başlat
```

İmzalama sırası: **Abone (1. sıra) → İşletmeci (2. sıra)**

Abone ve işletmeci bilgileri döküman taslağında tanımlı signing ID'lerine bağlanır.

---

### Adım 1 – Süreç Oluştur

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "name": "Abonelik Sözleşmesi - Ali Veli"
  }'
```

**Yanıt:**

```json
{
  "id": 147,
  "statusCode": "NEW",
  "accessToken": "kQQQioa"
}
```

`id` değerini (`147`) sonraki adımlarda kullanın.

---

### Adım 2 – Taslaktan Döküman Ekle

Döküman taslağındaki `signings` sıralaması:
- `id: 1` → Abone (1. imzacı)
- `id: 2` → İşletmeci (2. imzacı)

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/147/document/document-type \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "id": 22,
    "name": "Abonelik Sözleşmesi",
    "isSign": true,
    "isApprove": false,
    "isUpload": false,
    "signings": [
      {
        "id": 1,
        "signer": {
          "fullName": "Ali Veli",
          "email": "ali.veli@example.com",
          "phone": "5551112233",
          "identityNumber": "12345678901"
        }
      },
      {
        "id": 2,
        "signer": {
          "id": 138
        }
      }
    ]
  }'
```

> `signings[0].signer` → Abone bilgileri ile yeni imzacı oluşturulur.  
> `signings[1].signer.id` → Sistemde kayıtlı İşletmeci imzacısı bağlanır.

**Yanıt:**

```json
{
  "id": 7203
}
```

---

### Adım 3 – Süreci Başlat

```bash
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/147/status/start \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

**Yanıt:** `ok`

!!! success "Senaryo A Tamamlandı"
    Süreç başlatıldı. Abone e-posta/SMS ile bildirim alır ve e-imzasıyla imzalar. Ardından İşletmeci sırasına geçilir.

---

## Senaryo B: Abone Yapay Zeka ile Kimlik Doğrulamayla İmzalar

```
Süreç Oluştur → Taslaktan Döküman Ekle → Dökümana İmzacı Ekle (TCKK) → Süreci Başlat
```

Bu senaryoda:

- **Abone**: Yapay Zeka kimlik doğrulama (`TCKK_ONBOARDING`) ile imzalar. TC kimlik kartı bilgileri ve video yönergesi girilir.
- **İşletmeci**: E-İmza ile imzalar (2. sıra).

---

### Adım 1 – Süreç Oluştur

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "name": "Abonelik Sözleşmesi - Ali Veli (TCKK)"
  }'
```

**Yanıt:**

```json
{
  "id": 148,
  "statusCode": "NEW",
  "accessToken": "mPPPjob"
}
```

---

### Adım 2 – Taslaktan Döküman Ekle

Döküman taslağında yalnızca **İşletmeci** (2. sıra) tanımlı imzacı olarak bağlanır. Abone imzacısı bir sonraki adımda ayrıca eklenir.

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/148/document/document-type \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "id": 22,
    "name": "Abonelik Sözleşmesi",
    "isSign": true,
    "isApprove": false,
    "isUpload": false,
    "signings": [
      {
        "id": 2,
        "signer": {
          "id": 138
        }
      }
    ]
  }'
```

**Yanıt:**

```json
{
  "id": 7204
}
```

---

### Adım 3 – Aboneyi TCKK İmzacısı Olarak Ekle

Abone, TCKK Onboarding akışı ile doğrulanacaktır. TC kimlik kartı bilgileri, okunacak metin (`promptText`) ve video süresi bu adımda belirtilir.

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/148/document/7204/signers \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
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
  }'
```

| Alan | Değer | Açıklama |
|------|-------|----------|
| `order` | `1` | Abone ilk imzalar |
| `signatureType.code` | `TCKK_ONBOARDING` | Yapay Zeka kimlik doğrulama akışı |
| `promptText` | `"Lütfen adınızı ve soyadınızı okuyun"` | Aboneye video sırasında gösterilecek metin |
| `videoMaxDurationSeconds` | `60` | Video kaydı için maksimum süre |
| `signer.birthDate` | `"1990-05-15"` | Doğum tarihi (kimlik doğrulama için) |
| `signer.expiredDate` | `"2030-01-01"` | Kimlik kartı son geçerlilik tarihi |
| `signer.tcSerial` | `"A1B2C3D4"` | TC kimlik kartı seri numarası |

**Yanıt:**

```json
{
  "id": 5,
  "documentInstanceId": 7204,
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

---

### Adım 4 – Süreci Başlat

```bash
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/148/status/start \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

**Yanıt:** `ok`

!!! success "Senaryo B Tamamlandı"
    Süreç başlatıldı. Abone, yapay zeka kimlik doğrulama akışı ile TC kimlik kartını okutarak ve video kaydı yaparak sözleşmeyi imzalar. Ardından İşletmeci e-imzasıyla imzalar.

---

## Senaryo Karşılaştırması

| | Senaryo A | Senaryo B |
|--|-----------|-----------|
| **Abone imza türü** | E-İmza | TCKK Onboarding (Yapay Zeka) |
| **İşletmeci imza türü** | E-İmza | E-İmza |
| **İmzalama sırası** | Abone → İşletmeci | Abone → İşletmeci |
| **Gerekli abone bilgileri** | fullName, email, phone, identityNumber | + birthDate, expiredDate, tcSerial |
| **promptText / video** | Gerekmez | Gerekir |
| **Döküman ekleme adımı** | Taslaktan tek seferde | Taslak + ayrıca `signers` endpoint'i |

---

## İlgili Kaynaklar

- [Süreç API](../progress.md)
- [Taslaktan Döküman Ekleme](../progress_doctype.md)
- [İmzacı API](../signers.md)
- [İmzalama Türleri](../signature-types.md)
