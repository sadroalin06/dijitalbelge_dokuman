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
- Taslak ID'si ve imzalama sırası (`signing` ID'leri) [Referans API](../reference-api.md) üzerinden öğrenilmiş olmalıdır.
- İşletmeci, sistemde tanımlı bir imzacı olmalıdır (`signerId`).

---

## Senaryo A: Her İki Taraf E-İmza ile İmzalar

```
Süreç Oluştur → Taslaktan Döküman Ekle → Süreci Başlat
```

İmzalama sırası: **Abone (1. sıra) → İşletmeci (2. sıra)**

Abone ve işletmeci bilgileri döküman taslağındaki signing ID'lerine bağlanır.

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
  "accountId": 153,
  "createdByUserId": null,
  "name": "Abonelik Sözleşmesi - Ali Veli",
  "statusCode": "NEW",
  "processType": "BELGE_IMZALAMA",
  "documents": [],
  "signers": [],
  "createdAt": "2026-06-29T16:38:59.134467",
  "updatedAt": "2026-06-29T16:38:59.134469",
  "hasQrCode": false,
  "responsibleBy": null,
  "accessToken": "kQQQioa",
  "tokenExpiry": null,
  "referenceCode": null,
  "formFields": [],
  "formDesigns": []
}
```

> **`accessToken`** — Kullanıcının **mobil uygulamaya** gireceği süreç token'ıdır. Bu değer, abonenin sürece mobil uygulama üzerinden erişmesini sağlar.

`id` değerini (`147`) sonraki adımlarda kullanın.

---

### Adım 2 – Taslaktan Döküman Ekle

Döküman taslağındaki `signings` sıralaması (Referans API'den öğrenilir):

- `id: 75` → Abone (1. imzacı)
- `id: 77` → İşletmeci (2. imzacı)

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/147/document/document-type \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "id": 85,
    "name": "Abonelik Sözleşmesi",
    "description": "",
    "isSign": true,
    "isForm": false,
    "isActive": true,
    "isApprove": true,
    "isUpload": true,
    "document": {
      "base64": "",
      "fileName": "Abonelik belgesi.pdf"
    },
    "signings": [
      {
        "id": 75,
        "signer": {
          "fullName": "Ali Veli",
          "email": "ali.veli@example.com",
          "phone": "5551112233",
          "identityNumber": "12345678901"
        }
      },
      {
        "id": 77,
        "signer": {
          "id": 108
        }
      }
    ]
  }'
```

> `signings[0].signer` → Abone bilgileri ile yeni imzacı oluşturulur.  
> `signings[1].signer.id` → Sistemde kayıtlı İşletmeci imzacısı (`id: 108`) bağlanır.

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
Süreç Oluştur → Taslaktan Döküman Ekle (TCKK bilgileriyle) → Süreci Başlat
```

Bu senaryoda:

- **Abone**: Yapay Zeka kimlik doğrulama (`TCKK_ONBOARDING`) ile imzalar. TC kimlik kartı bilgileri ve BTK mevzuatına uygun yasal metin, döküman eklenirken `signings` içinde belirtilir.
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
  "accountId": 153,
  "createdByUserId": null,
  "name": "Abonelik Sözleşmesi - Ali Veli (TCKK)",
  "statusCode": "NEW",
  "processType": "BELGE_IMZALAMA",
  "documents": [],
  "signers": [],
  "createdAt": "2026-06-29T16:38:59.134467",
  "updatedAt": "2026-06-29T16:38:59.134469",
  "hasQrCode": false,
  "responsibleBy": null,
  "accessToken": "mPPPjob",
  "tokenExpiry": null,
  "referenceCode": null,
  "formFields": [],
  "formDesigns": []
}
```

> **`accessToken`** — Kullanıcının **mobil uygulamaya** gireceği süreç token'ıdır. Bu değer, abonenin sürece mobil uygulama üzerinden erişmesini sağlar.

---

### Adım 2 – Taslaktan Döküman Ekle (TCKK Bilgileriyle)

#### BTK Mevzuatı – Zorunlu Yasal Metin

BTK mevzuatı gereği, görüntülü kimlik doğrulama sırasında abonenin yüksek sesle okuması gereken standart metin şu formattadır:

> *"Ben **\<Ad Soyad\>** olarak **\<Hizmet Numarası\>** numaralı hizmetin **\<İşlem Türü\>** işlemi için kimliğimin doğrulanmasını **\<GG.AA.YYYY\> \<SS.DD\>** itibarıyla onaylıyorum."*

**Örnek:**

> *"Ben Ali Veli olarak 0532 XXX XX XX numaralı hizmetin Abonelik Başvurusu işlemi için kimliğimin doğrulanmasını 29.06.2026 12:55 itibarıyla onaylıyorum."*

Bu metin `promptText` alanına dinamik olarak üretilerek gönderilmelidir.

---

Abone signing'i (`id: 75`) için `signatureType`, `promptText`, `videoMaxDurationSeconds` ve kimlik bilgileri doğrudan `signings` içinde verilir. İşletmeci (`id: 77`) ise kayıtlı imzacı ID'si ile bağlanır.

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/148/document/document-type \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "id": 85,
    "name": "Abonelik Sözleşmesi",
    "description": "",
    "isSign": true,
    "isForm": false,
    "isActive": true,
    "isApprove": true,
    "isUpload": true,
    "document": {
      "base64": "",
      "fileName": "Abonelik belgesi.pdf"
    },
    "signings": [
      {
        "id": 75,
        "signatureType": {
          "code": "TCKK_ONBOARDING"
        },
        "promptText": "Ben Ali Veli olarak 0532 XXX XX XX numaralı hizmetin Abonelik Başvurusu işlemi için kimliğimin doğrulanmasını 29.06.2026 12:55 itibarıyla onaylıyorum.",
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
      },
      {
        "id": 77,
        "signer": {
          "id": 108
        }
      }
    ]
  }'
```

| Alan | Açıklama |
|------|----------|
| `signings[0].id` | Taslaktaki Abone imzalama sırası ID'si |
| `signings[0].signatureType.code` | `TCKK_ONBOARDING` — Yapay Zeka kimlik doğrulama akışı |
| `signings[0].promptText` | BTK yasal metni — abone video sırasında yüksek sesle okur |
| `signings[0].videoMaxDurationSeconds` | Video kaydı için maksimum süre (saniye) |
| `signings[0].signer.birthDate` | Doğum tarihi (kimlik doğrulama için) |
| `signings[0].signer.expiredDate` | Kimlik kartı son geçerlilik tarihi |
| `signings[0].signer.tcSerial` | TC kimlik kartı seri numarası |
| `signings[1].signer.id` | Sistemde kayıtlı İşletmeci imzacısı (`id: 108`) |

**Yanıt:**

```json
{
  "id": 7204
}
```

---

### Adım 3 – Süreci Başlat

```bash
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/148/status/start \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

**Yanıt:** `ok`

!!! success "Senaryo B Tamamlandı"
    Süreç başlatıldı. Abone, mobil uygulama üzerinden `accessToken` ile sürece girer; TC kimlik kartını okutarak ve BTK mevzuatına uygun metni yüksek sesle okuyarak video kaydı yapar. Doğrulama tamamlandıktan sonra İşletmeci e-imzasıyla imzalar.

---

## Senaryo Karşılaştırması

| | Senaryo A | Senaryo B |
|--|-----------|-----------|
| **Abone imza türü** | E-İmza | TCKK Onboarding (Yapay Zeka) |
| **İşletmeci imza türü** | E-İmza | E-İmza |
| **İmzalama sırası** | Abone → İşletmeci | Abone → İşletmeci |
| **Gerekli abone bilgileri** | fullName, email, phone, identityNumber | + birthDate, expiredDate, tcSerial |
| **promptText / video** | Gerekmez | BTK yasal metni zorunlu |
| **Döküman ekleme adımı** | Taslaktan tek seferde | Taslak + ayrıca `signers` endpoint'i |
| **accessToken kullanımı** | Mobil uygulamaya girilir | Mobil uygulamaya girilir |

---

## İlgili Kaynaklar

- [Süreç API](../progress.md)
- [Taslaktan Döküman Ekleme](../progress_doctype.md)
- [İmzacı API](../signers.md)
- [İmzalama Türleri](../signature-types.md)
