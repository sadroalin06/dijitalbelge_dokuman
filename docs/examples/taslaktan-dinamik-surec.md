---
description: Hazır süreç taslaklarından (ProcessDefinition) tek istekte dinamik süreç başlatma örneği — belge içeriğindeki {{alan}} yer tutucularının form verisiyle otomatik doldurulması.
---

# Taslaktan Dinamik Süreç Başlatma

Bu örnek, panelde önceden hazırlanmış bir **süreç taslağının** (ProcessDefinition) API ile
**tek istekte** başlatılmasını ve belge içeriğindeki dinamik alanların (`{{alan}}` yer
tutucuları) her seferinde farklı verilerle otomatik doldurulmasını gösterir.

Önceki örneklerdeki (bkz. [Abonelik Sözleşmesi](abonelik-sozlesmesi.md),
[Karşılıklı Sözleşme](karsilikli-sozlesme-imzalama.md)) çok adımlı akıştan
(`Süreç Oluştur` → `Taslaktan Döküman Ekle` → `Süreci Başlat`) farkı: burada üç adım
[`/process-definitions/{definitionId}/start`](../process-definitions.md) ile **tek
API çağrısında** yapılır. Bu, aynı taslaktan sık sık (ör. her yeni personel için,
her yeni sipariş için) tekrar tekrar süreç başlatan entegrasyonlar için önerilen yöntemdir.

**Senaryo:** İK departmanı, her yeni personel görevlendirmesinde aynı **"Görev Belgesi"**
şablonunu kullanıyor. Belgede personelin adı, soyadı ve görev başlangıç tarihi değişiyor;
geri kalan metin sabit. Bu üç alan panelde **Form Tasarımı** olarak tanımlanmış ve
belgeye `{{ad_soyad}}` / `{{gorevbas}}` yer tutucularıyla yerleştirilmiş.

---

## Ön Koşullar

- **Görev Belgesi Süreci** adında bir süreç taslağı panelde tanımlanmış olmalıdır: belge
  içinde `{{ad_soyad}}`, `{{gorevbas}}` yer tutucuları ve bu alanları tanımlayan bir
  **Form Tasarımı** (bkz. [Reference API — Form Tasarımları](../reference-api.md#form-tasarmlar))
  bağlı olmalıdır.
- Taslağın `definitionId`'si ve imza adımının `partyTypeId`'si (taraf tipi) biliniyor
  olmalıdır — bkz. [Süreç Taslakları API](../process-definitions.md#1-taslaklar-listele).
- Personel, sistemde tanımlı bir imzacı olmalıdır (`signerId`) ya da istekle birlikte
  oluşturulabilir.

---

## Genel Akış

```
(İlk kurulumda bir kez) Taslağı ve Form Alanlarını Öğren
        → İmzacıyı Oluştur / Bul
        → Taslaktan Süreci Başlat (formValues ile)
        → İmzalı Belgeyi İndir
```

---

## Adım 1 – Taslağı ve Form Alanlarını Öğren

Bu adım genelde entegrasyonun **ilk kurulumunda bir kez** yapılır; `definitionId`,
`partyTypeId` ve form alan anahtarları (`key`) sabit kaldığı sürece tekrarlanmasına
gerek yoktur.

```http
GET /api/external/process-definitions/12
```

**Yanıt (özet):**

```json
{
  "id": 12,
  "name": "Görev Belgesi Süreci",
  "processType": "BELGE_IMZALAMA",
  "documentRequirements": [
    {
      "documentTypeId": 45,
      "documentTypeName": "Görev Belgesi",
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
```

`signings[0].signer: null` olduğundan bu adıma başlatırken bir imzacı atanmalı —
`partyTypeId: 11` (Personel) için.

Belgedeki dinamik alanların anahtarlarını (`key`) form tasarımından öğrenin:

```http
GET /api/external/referance/form
```

```json
[
  {
    "id": 3,
    "name": "Görev Formu",
    "jsonSchema": {
      "fields": [
        { "key": "ad_soyad", "type": "text", "label": "Adı Soyadı" },
        { "key": "gorevbas", "type": "date", "label": "Görev Başlangıç Tarihi" }
      ]
    }
  }
]
```

`formValues` isteğinde göndereceğiniz anahtarlar (`ad_soyad`, `gorevbas`), belgedeki
`{{ad_soyad}}` ve `{{gorevbas}}` yer tutucularıyla **birebir aynı** olmalıdır.

---

## Adım 2 – İmzacıyı Oluştur / Bul

Yeni personel sisteme henüz kayıtlı değilse `bulk-insert` ile oluşturulur (kayıtlıysa
bu adım atlanıp mevcut `signerId` kullanılır):

```http
POST /api/external/signers/bulk-insert
```

```json
[
  {
    "fullName": "Ali Veli",
    "email": "ali.veli@example.com",
    "phone": "+905551112233",
    "identityNumber": "12345678901",
    "partyTypeId": 11
  }
]
```

**Yanıt:**

```json
[
  { "id": 138, "fullName": "Ali Veli", "partyTypeId": 11 }
]
```

`id: 138` değerini bir sonraki adımda `signerId` olarak kullanın.

---

## Adım 3 – Taslaktan Süreci Başlat (`formValues` ile)

Taslak, imzacı ve belgeye işlenecek dinamik değerler **tek istekte** gönderilir:

```http
POST /api/external/process-definitions/12/start
```

```json
{
  "name": "Görev Belgesi - Ali Veli",
  "autoStart": true,
  "signers": [
    { "signerId": 138, "partyTypeId": 11 }
  ],
  "formValues": {
    "ad_soyad": "Ali Veli",
    "gorevbas": "2026-09-01"
  }
}
```

| Alan | Açıklama |
|------|----------|
| `signers[0].partyTypeId: 11` | Adım 1'de öğrenilen "Personel" taraf tipi |
| `formValues.ad_soyad` | Belgedeki `{{ad_soyad}}` yer tutucusunun yerine geçer |
| `formValues.gorevbas` | Belgedeki `{{gorevbas}}` yer tutucusunun yerine geçer |
| `autoStart: true` | Süreç oluşturulur oluşturulmaz `STARTED` durumuna alınır, Ali Veli'ye bildirim gider |

**Yanıt (HTTP 201):**

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

!!! success "Tamamlandı"
    Tek istekte: taslaktan yeni bir süreç oluşturuldu, belge kopyalandı,
    `{{ad_soyad}}` → "Ali Veli" ve `{{gorevbas}}` → "2026-09-01" olarak belgeye işlendi,
    Personel taraf tipine Ali Veli imzacı olarak atandı ve süreç başlatıldı (Ali Veli
    e-posta/SMS bildirimi aldı). Aynı isteği farklı `signers`/`formValues` ile
    çağırarak her yeni personel için aynı akışı tekrarlayabilirsiniz.

`document.id` (`7310`) değerini imzalı belgeyi indirirken kullanın (bkz.
[Adım 4](#adm-4-opsiyonel-imzal-belgeyi-indir)).

---

## Ek Senaryo: Dinamik Video Yönergesi (`TCKK_ONBOARDING`)

Personel taraf tipi, taslakta e-imza yerine **`TCKK_ONBOARDING`** (kimlik kartı NFC +
yüz tanıma + video) ile tanımlıysa, video kaydı sırasında okunacak yönerge metni de
`{{alan}}` yer tutucusu içerebilir ve **aynı `formValues` ile** doldurulur — bkz.
[Süreç Taslakları API — `promptText` notu](../process-definitions.md#3-taslaktan-surec-baslat).

Taslaktaki imza adımının `promptText`'i (panelde tanımlanır):

```
Merhaba {{ad_soyad}}, {{gorevbas}} tarihli görevlendirmenizi onaylamak için
lütfen kimliğinizi kameraya gösterin.
```

Adım 3'teki **aynı istek** gönderildiğinde (`formValues: {"ad_soyad": "Ali Veli", "gorevbas": "2026-09-01"}`),
Ali Veli'nin video kayıt ekranında göreceği yönerge metni otomatik olarak:

```
Merhaba Ali Veli, 2026-09-01 tarihli görevlendirmenizi onaylamak için
lütfen kimliğinizi kameraya gösterin.
```

olur. Yönerge metnini `formValues`'a göre elle üretip ayrıca göndermenize gerek yoktur.

---

## Adım 4 (Opsiyonel) – İmzalı Belgeyi İndir

Süreç tamamlandıktan sonra, doldurulmuş ve imzalanmış belgenin son hali:

```http
GET /api/external/process-instances/148/document/7310/file
```

**Yanıt:**

```json
{
  "fileName": "Görev Belgesi_xxxxxxxx.pdf",
  "mimeType": "application/pdf",
  "base64": "JVBERi0xLjQK...",
  "size": 245120
}
```

---

## İlgili Kaynaklar

- [Süreç Taslakları API](../process-definitions.md) — `formValues` / `formDesignIds` alan referansı
- [Reference API — Form Tasarımları](../reference-api.md#form-tasarmlar)
- [İmzacı API](../signers.md) — imzacı oluşturma / arama
- [İmzalama Türleri](../signature-types.md) — `TCKK_ONBOARDING` dahil tüm imza türleri
- [Abonelik Sözleşmesi İmzalama](abonelik-sozlesmesi.md) — çok adımlı (taslak taslağı elle kurarak) alternatif akış
