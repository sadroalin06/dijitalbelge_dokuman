# Abonelik Sözleşmesi İmzalama

Bu örnek, arayüzden yüklenen bir **Abonelik Sözleşmesi** taslağının API aracılığıyla imzalatılmasını adım adım açıklar.

Üç farklı senaryo ele alınmaktadır:

| Senaryo | Abone | İşletmeci |
|---------|-------|-----------|
| [**Senaryo A**](#senaryo-a-her-iki-taraf-e-imza-ile-imzalar) | E-İmza | E-İmza |
| [**Senaryo B**](#senaryo-b-abone-yapay-zeka-ile-kimlik-dogrulamayla-imzalar) | Yapay Zeka Kimlik Doğrulama (TCKK) | E-İmza |
| [**Senaryo C**](#senaryo-c-e-devlet-ile-kimlik-dogrulama-isletmeci-eimza) | e-Devlet kimlik doğrulama (dışarıda gerçekleşir) | PDF yükle + E-İmza |

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

```http
POST /api/external/process-instances
```

```json
{
  "name": "Abonelik Sözleşmesi - Ali Veli"
}
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

```http
POST /api/external/process-instances/147/document/document-type
```

```json
{
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
}
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

```http
PUT /api/external/process-instances/147/status/start
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

```http
POST /api/external/process-instances
```

```json
{
  "name": "Abonelik Sözleşmesi - Ali Veli (TCKK)"
}
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

```http
POST /api/external/process-instances/148/document/document-type
```

```json
{
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
}
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
  "id": 7355,
  "documentTypeId": 85,
  "documentTypeName": "Abonelik Sözleşmesi",
  "filePath": null,
  "fileName": "Abonelik Sözleşmesi",
  "description": "",
  "documentSigningType": null,
  "uploaded": null,
  "signed": null,
  "addpublicsigned": false,
  "approved": null,
  "mustsigned": true,
  "mustuploaded": true,
  "mustapproved": true,
  "signedAt": null,
  "uploadedAt": null,
  "approvedAt": null,
  "fileTypes": null,
  "documentFiles": [
    {
      "id": 1558,
      "fileType": "ORIGINAL",
      "isCurrentVersion": null,
      "linkedAt": null,
      "isOldsign": null,
      "storedFileId": 1412,
      "fileName": "Abonelik belgesi_xxxxxxxx.pdf",
      "filePath": "xxx/xxx/Abonelik belgesi_xxxxxxxx.pdf",
      "contentType": "application/pdf",
      "size": 2425408,
      "archivedDocumentId": null
    }
  ],
  "signers": [
    {
      "id": 1165,
      "documentInstanceId": 7355,
      "fullName": "Ali Veli",
      "signerId": 75,
      "email": "ali.veli@example.com",
      "phone": "5XXXXXXXXX",
      "mustUpload": false,
      "mustSign": true,
      "isauth": false,
      "stepOrder": 1,
      "uploadedAt": null,
      "signedAt": null,
      "issign": false,
      "partTypeId": null,
      "partTypeName": null,
      "signatureTypeId": 16,
      "signatureTypeName": "TCKK_ONBOARDING",
      "signatureTypeCode": "TCKK_ONBOARDING",
      "accessToken": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "visibleSignature": {
        "id": 7554,
        "data": "Ali Veli",
        "image": false,
        "originX": 384,
        "originY": 332,
        "width": 200,
        "height": 190,
        "pageNumber": 7,
        "fontSize": 14,
        "textColor": "#000000",
        "backgroundColor": "#ffffff",
        "alignment": "CENTER"
      },
      "signatureFileId": null,
      "promptText": null,
      "videoMaxDurationSeconds": null,
      "identityNumber": "1XXXXXXXXXX"
    },
    {
      "id": 1166,
      "documentInstanceId": 7355,
      "fullName": "İşletmeci Yetkili",
      "signerId": 108,
      "email": "isletmeci@example.com",
      "phone": "5XXXXXXXXX",
      "mustUpload": false,
      "mustSign": true,
      "isauth": false,
      "stepOrder": 2,
      "uploadedAt": null,
      "signedAt": null,
      "issign": false,
      "partTypeId": null,
      "partTypeName": null,
      "signatureTypeId": 1,
      "signatureTypeName": "Eimza",
      "signatureTypeCode": "EIMZA",
      "accessToken": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
      "visibleSignature": {
        "id": 7555,
        "data": "İşletmeci Yetkili",
        "image": false,
        "originX": 35,
        "originY": 416,
        "width": 200,
        "height": 75,
        "pageNumber": 7,
        "fontSize": 14,
        "textColor": "#000000",
        "backgroundColor": "#ffffff",
        "alignment": "CENTER"
      },
      "signatureFileId": null,
      "promptText": null,
      "videoMaxDurationSeconds": null,
      "identityNumber": "1XXXXXXXXXX"
    }
  ],
  "documentAdds": null,
  "signingControl": false,
  "fileTypesEnum": []
}
```

---

### Adım 3 – Süreci Başlat

```http
PUT /api/external/process-instances/148/status/start
```

**Yanıt:** `ok`

!!! success "Senaryo B Tamamlandı"
    Süreç başlatıldı. Abone, mobil uygulama üzerinden `accessToken` ile sürece girer; TC kimlik kartını okutarak ve BTK mevzuatına uygun metni yüksek sesle okuyarak video kaydı yapar. Doğrulama tamamlandıktan sonra İşletmeci e-imzasıyla imzalar.

---

## Senaryo C: e-Devlet ile Kimlik Doğrulama, İşletmeci E-İmza ile İmzalar

```
Süreç Oluştur → Tekil Döküman Ekle → İmzacı Ekle (İşletmeci) → Süreci Başlat
```

Bu senaryoda BTK mevzuatı gereği abonenin kimlik doğrulaması **e-Devlet** üzerinden gerçekleştirilir. Süreç tamamen işletmeci tarafından yönetilir:

- **Abone**: e-Devlet üzerinden kimliğini doğrular (bu adım DijitalBelge dışında gerçekleşir).
- **İşletmeci**: e-Devlet'ten aldığı abone bilgilerini içeren PDF'i sisteme yükler ve e-İmza ile imzalar.

---

### Adım 1 – Süreç Oluştur

```http
POST /api/external/process-instances
```

```json
{
  "name": "Abonelik Sözleşmesi - Ali Veli (e-Devlet)"
}
```

**Yanıt:**

```json
{
  "id": 149,
  "accountId": 153,
  "createdByUserId": null,
  "name": "Abonelik Sözleşmesi - Ali Veli (e-Devlet)",
  "statusCode": "NEW",
  "processType": "BELGE_IMZALAMA",
  "documents": [],
  "signers": [],
  "createdAt": "2026-06-29T16:38:59.134467",
  "updatedAt": "2026-06-29T16:38:59.134469",
  "responsibleBy": null,
  "accessToken": "nRRRkpc",
  "tokenExpiry": null,
  "referenceCode": null,
  "formFields": [],
  "formDesigns": []
}
```

---

### Adım 2 – e-Devlet PDF'ini Sürece Yükle

İşletmeci, e-Devlet'ten alınan abone kimlik doğrulama bilgilerini içeren PDF'i Base64 formatında sürece ekler.

```http
POST /api/external/process-instances/149/document/single
```

```json
{
  "name": "Abonelik Sözleşmesi",
  "base64": "JVBERi0xLjQK...",
  "fileName": "Abonelik belgesi.pdf"
}
```

**Yanıt:**

```json
{
  "id": 7356,
  "name": "Abonelik Sözleşmesi",
  "statusCode": "PENDING",
  "createdAt": "2026-06-29T20:00:00"
}
```

---

### Adım 3 – İşletmeciye İmzacı Olarak Ekle

e-Devlet kimlik doğrulaması dışarıda tamamlandığından yalnızca işletmeci imzacı olarak eklenir.

```http
POST /api/external/process-instances/149/document/7356/signers
```

```json
{
  "order": 1,
  "isRequired": true,
  "signer": {
    "id": 108
  }
}
```

**Yanıt:**

```json
{
  "id": 1167,
  "documentInstanceId": 7356,
  "fullName": "İşletmeci Yetkili",
  "signerId": 108,
  "email": "isletmeci@example.com",
  "stepOrder": 1,
  "statusCode": "PENDING",
  "signatureTypeCode": "EIMZA",
  "createdAt": "2026-06-29T20:00:00"
}
```

---

### Adım 4 – Süreci Başlat

```http
PUT /api/external/process-instances/149/status/start
```

**Yanıt:** `ok`

!!! success "Senaryo C Tamamlandı"
    Süreç başlatıldı. Abonenin kimlik doğrulaması e-Devlet üzerinden gerçekleştirilmiş olup PDF'e işlenmiştir. İşletmeci e-İmzasıyla belgeyi imzalayarak süreci tamamlar.

---

## İmza Sonrası – İmzalı Belgeyi İndir

Her üç senaryoda da süreç tamamlandıktan sonra imzalı belgenin son versiyonu Base64 formatında çekilebilir.

**Scope:** `document:read`

```http
GET /api/external/process-instances/{processId}/document/{documentId}/file
```

Senaryo A için örnek (`processId: 147`, `documentId: 7203`):

```http
GET /api/external/process-instances/147/document/7203/file
```

Senaryo B için örnek (`processId: 148`, `documentId: 7355`):

```http
GET /api/external/process-instances/148/document/7355/file
```

Senaryo C için örnek (`processId: 149`, `documentId: 7356`):

```http
GET /api/external/process-instances/149/document/7356/file
```

**Yanıt:**

```json
{
  "fileName": "Abonelik belgesi_xxxxxxxx.pdf",
  "mimeType": "application/pdf",
  "base64": "JVBERi0xLjQK...",
  "size": 2425408
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `fileName` | string | Dosya adı |
| `mimeType` | string | Dosya MIME türü |
| `base64` | string | İmzalı belgenin Base64 içeriği (en son versiyon) |
| `size` | number | Dosya boyutu (byte) |

> `documentId`, döküman eklenirken dönen yanıttaki `id` alanıdır (Senaryo A: `7203`, Senaryo B: `7355`).

---

## Senaryo Karşılaştırması

| | Senaryo A | Senaryo B | Senaryo C |
|--|-----------|-----------|-----------|
| **Abone kimlik doğrulama** | E-İmza | TCKK (Yapay Zeka) | e-Devlet (dışarıda) |
| **İşletmeci imza türü** | E-İmza | E-İmza | E-İmza |
| **İmzalama sırası** | Abone → İşletmeci | Abone → İşletmeci | Yalnızca İşletmeci |
| **Döküman kaynağı** | Taslak | Taslak | İşletmeci tarafından yüklenir |
| **Gerekli abone bilgileri** | fullName, email, phone, identityNumber | + birthDate, expiredDate, tcSerial | Gerekmez (e-Devlet PDF'inde) |
| **promptText / video** | Gerekmez | BTK yasal metni zorunlu | Gerekmez |
| **accessToken kullanımı** | Abone mobil uygulamaya girer | Abone mobil uygulamaya girer | Gerekmez |

---

## İlgili Kaynaklar

- [Süreç API](../progress.md)
- [Taslaktan Döküman Ekleme](../progress_doctype.md)
- [İmzacı API](../signers.md)
- [İmzalama Türleri](../signature-types.md)
