---
description: E-ticaret üyesinin TCKK_TIMESTAMP ile kimlik doğrulaması örneği — kimlik kartı NFC, SMS ve konum doğrulaması, webhook ile üye hesabının otomatik doğrulanmış olarak işaretlenmesi.
---

# E-Ticaret Üyesi Kimlik Doğrulama (`TCKK_TIMESTAMP`)

Bu örnek, bir e-ticaret sitesinin üyelerinden birine **kimlik doğrulama** yaptırmasını
ve doğrulama tamamlandığında **webhook** ile üyenin hesabını otomatik olarak
"kimliği doğrulandı" durumuna almasını gösterir.

Önceki örneklerden farkı: burada bir **sözleşme imzalatılmıyor** — amaç yalnızca
kişinin gerçekten iddia ettiği kişi olduğunu (TC kimlik kartı + telefon + konum ile)
teyit etmek. Bu yüzden süreç tipi olarak [`DIJITAL_KIMLIK_DOGRULAMA`](../progress.md#surec-tipleri-processtype)
kullanılır: **belge imzalanmaz, gerçek bir dosya üretilmez**, yalnızca kimlik
doğrulama kanıtı oluşturulur.

**Senaryo:** E-ticaret sitesi, belirli bir işlem limitinin üzerine çıkan (ör. yüksek
tutarlı sipariş, taksitli ödeme, satıcı hesabı başvurusu vb.) üyelerinden kimlik
doğrulaması istiyor. Üye "Kimliğimi Doğrula" butonuna bastığında sistem
**TCKK_TIMESTAMP** yöntemiyle bir doğrulama süreci başlatır: üye telefonunun NFC
anteniyle TC kimlik kartını okutur, kayıtlı cep telefonuna gelen SMS kodunu girer ve
cihazın konumu okunur; tüm bunlar bir zaman damgasıyla mühürlenir. Doğrulama
tamamlanınca e-ticaret sistemine webhook düşer ve üyenin hesabı otomatik olarak
doğrulanmış işaretlenir.

---

## Neden `TCKK_TIMESTAMP`?

[İmzalama Türleri](../signature-types.md) sayfasındaki karşılaştırmaya göre, yüz
tanıma veya video kaydına gerek duymayan, yalnızca **fiziksel kimlik kartı + SMS +
konum** doğrulaması yeterli olan akışlar için önerilen yöntem budur:

| Yöntem | Kimlik Kartı NFC | SMS (Telefon) | Konum | Yüz/Video |
|---|---|---|---|---|
| `TCKK_TIMESTAMP` | ✅ | ✅ | ✅ | ❌ |
| `TCKK_FACE_TIMESTAMP` | ✅ | ✅ | ✅ | Anlık yüz |
| `TCKK_ONBOARDING` | ✅ | ✅ | ✅ | Fotoğraf + video |

E-ticaret üyelik doğrulamasında genelde ek biyometri gerekmediğinden en hafif seçenek
olan `TCKK_TIMESTAMP` yeterlidir; daha yüksek güvence gerekiyorsa aynı akış
`TCKK_FACE_TIMESTAMP` veya `TCKK_ONBOARDING` ile birebir aynı şekilde kurulabilir
(yalnızca `signatureType.code` değişir).

---

## Ön Koşullar

- Panelde bir **webhook** tanımlı ve aktif olmalı (bkz. [Webhook](../webhook.md)) —
  doğrulama tamamlandığında sisteminize bildirim düşecek.
- Üyenin **TC kimlik numarası**, **cep telefonu** ve **e-posta** bilgisi, KVKK
  aydınlatma/onay süreciniz tamamlanmış şekilde elinizde olmalı.
- API kimlik bilgileriniz (`X-Client-Id` / `X-Client-Secret`) ve gerekli scope'lar:
  `process:start`, `document:write`, `document:sign`, `process:status`.

---

## Genel Akış

```
Üye "Kimliğimi Doğrula" der
        → Süreç Oluştur (processType: DIJITAL_KIMLIK_DOGRULAMA)
        → processId ↔ üyeId eşlemesini kendi veritabanınızda saklayın
        → Doğrulama Görevini Ekle (döküman + TCKK_TIMESTAMP imzacı)
        → Süreci Başlat  →  üyeye link/QR gider
        → Üye: Kimlik Kartı NFC + SMS Kodu + Konum İzni
        → Webhook (DOCUMENT_SIGNED)  →  üye hesabı "Kimliği Doğrulandı" işaretlenir
```

---

## Adım 1 – Süreci Oluştur

```http
POST /api/external/process-instances
```

```json
{
  "name": "Üye Kimlik Doğrulama - Ali Veli (#4521)",
  "processType": "DIJITAL_KIMLIK_DOGRULAMA"
}
```

**Yanıt (HTTP 201):**

```json
{
  "id": 512,
  "name": "Üye Kimlik Doğrulama - Ali Veli (#4521)",
  "statusCode": "NEW",
  "processType": "DIJITAL_KIMLIK_DOGRULAMA",
  "signers": [],
  "documents": [],
  "accessToken": "xY7pQ2m",
  "createdAt": "2026-09-15T10:00:00"
}
```

!!! warning "`processId` ↔ üye eşlemesini kendiniz saklayın"
    Bu API'de sürece özel bir "referans kodu" alanı yoktur; webhook geldiğinde sizi
    hangi üyeyle ilgili olduğunu bulmanız için dönen `id` (`processId`, burada `512`)
    değerini kendi veritabanınızda üyenin kaydına (`#4521`) yazmanız gerekir — Stripe
    vb. servislerdeki `external_reference` mantığının burada uygulama tarafında
    yapılması gerekir.

---

## Adım 2 – Doğrulama Görevi İçin Belge Ekle

`DIJITAL_KIMLIK_DOGRULAMA` sürecinde **gerçek bir belge imzalanmaz**, ama imza/kimlik
doğrulama görevi teknik olarak yine bir dökümana bağlanır — sistem bunu üyeye asla
göstermeyeceği, imzalatmayacağı **gizli bir "signing control" belgesi** olarak
kullanır (bkz. [Süreç Tipleri](../progress.md#surec-tipleri-processtype)). Bu yüzden
küçük, içeriği önemsiz bir belge eklemeniz yeterlidir:

```http
POST /api/external/process-instances/512/document/single
```

```json
{
  "name": "Kimlik Doğrulama Kaydı",
  "fileName": "kimlik-dogrulama.pdf",
  "base64": "JVBERi0xLjQK..."
}
```

**Yanıt (HTTP 201):**

```json
{
  "id": 8801,
  "fileName": "kimlik-dogrulama.pdf",
  "uploaded": true,
  "signed": false
}
```

`id: 8801` değerini bir sonraki adımda `documentId` olarak kullanın.

---

## Adım 3 – İmzacıyı `TCKK_TIMESTAMP` ile Ekle

```http
POST /api/external/process-instances/512/document/8801/signers
```

```json
{
  "signerName": "Ali Veli",
  "order": 1,
  "isRequired": true,
  "signatureType": { "code": "TCKK_TIMESTAMP" },
  "visibleSignature": {
    "pageNumber": 1,
    "originX": 0,
    "originY": 0,
    "width": 1,
    "height": 1
  },
  "signer": {
    "fullName": "Ali Veli",
    "identityNumber": "12345678901",
    "phone": "+905551112233",
    "email": "ali.veli@example.com"
  }
}
```

| Alan | Açıklama |
|------|----------|
| `signatureType.code: "TCKK_TIMESTAMP"` | Kimlik doğrulama yöntemi: kimlik kartı NFC + SMS + konum + zaman damgası |
| `signer.identityNumber` | Doğrulanacak T.C. Kimlik Numarası — üyenin NFC ile okuttuğu kimlik kartıyla eşleşmesi gerekir |
| `signer.phone` | SMS doğrulama kodunun gönderileceği, üyenin kayıtlı cep telefonu numarası |
| `visibleSignature` | Bu süreç tipinde belge görünür şekilde işlenmediği için değerlerin bir önemi yoktur, ancak alan **zorunlu** olduğundan minimal bir değer gönderilir |

!!! info "`order: 1` şart"
    [Döküman API](../documents.md#8-dokumana-imzac-ekle) sayfasındaki kurala göre
    `order` gönderilmezse imzacı doğrulama ekranında hiç görünmez.

**Yanıt (HTTP 201):**

```json
{
  "id": 9,
  "documentInstanceId": 8801,
  "signerName": "Ali Veli",
  "order": 1,
  "statusCode": "PENDING",
  "signatureType": { "code": "TCKK_TIMESTAMP" },
  "signer": {
    "fullName": "Ali Veli",
    "identityNumber": "12345678901",
    "phone": "+905551112233",
    "email": "ali.veli@example.com"
  },
  "createdAt": "2026-09-15T10:00:05"
}
```

---

## Adım 4 – Süreci Başlat

```http
PUT /api/external/process-instances/512/status/start
```

**Yanıt:** `ok`

Süreç başlatıldığında Ali Veli'ye e-posta/SMS ile `accessToken` içeren doğrulama
bağlantısı (veya QR kod) gönderilir.

---

## Üye Tarafında Ne Olur?

Ali Veli bağlantıyı açtığında sırasıyla:

```
1. Kimlik Kartı NFC Okuma   → telefonun NFC anteniyle T.C. kimlik kartı okutulur,
                               kart üzerindeki bilgiler signer.identityNumber ile
                               karşılaştırılır
2. SMS Doğrulama            → signer.phone'a (+905551112233) gönderilen tek kullanımlık
                               kod, ekrana girilir
3. Konum İzni               → tarayıcı/uygulama cihazdan GPS konumunu okur
4. Zaman Damgası            → yukarıdaki adımların tamamlandığı an, değiştirilemez
                               şekilde mühürlenir
```

Bu dört unsur (kimlik + telefon + konum + zaman), `TCKK_TIMESTAMP` yönteminin ürettiği
**kimlik doğrulama kanıtının** temelini oluşturur (bkz. [İmza Formatları ve
Doğrulama — JAdES](../signature-verification.md#formatlar)).

---

## Adım 5 – Webhook: Doğrulama Sonucu

Üye adımları tamamladığında sisteminize `DOCUMENT_SIGNED` olayı düşer:

```json
{
  "event": "DOCUMENT_SIGNED",
  "timestamp": "2026-09-15T10:04:32",
  "accountId": 5,
  "data": {
    "processId": 512,
    "documentId": 8801,
    "documentName": "Kimlik Doğrulama Kaydı",
    "allSigned": true
  }
}
```

Webhook handler'ınızda yapmanız gereken:

1. `X-Webhook-Signature` başlığını doğrulayın (bkz. [Webhook — İmza Doğrulama](../webhook.md#imza-dogrulama-hmac-sha256)).
2. `data.processId` (`512`) değerini Adım 1'de sakladığınız eşlemeden kendi üye
   kaydınıza (`#4521`) çevirin.
3. `allSigned: true` ise üyenin hesabını `identityVerified = true` /
   `identityVerifiedAt = timestamp` olarak güncelleyin ve kısıtlı işlemi (yüksek
   limitli ödeme, satıcı paneli vb.) açın.

!!! success "Tamamlandı"
    Ali Veli, telefonuyla kimlik kartını okutup SMS kodunu girdikten ve konum izni
    verdikten sonra sürecin tek imzacısı olduğu için süreç `COMPLETED` durumuna
    geçti; e-ticaret sistemi webhook'u alarak üyeyi "kimliği doğrulandı" olarak
    işaretledi — hiçbir belge imzalanmadı, yalnızca kimlik doğrulama kanıtı üretildi.

---

## Adım 6 (Opsiyonel) – Doğrulama Kanıtını Sakla

Denetim veya uyuşmazlık durumunda ("üye şu tarihte şu konumda kimliğini doğruladı"
kanıtı) ayrı olarak saklanan JAdES kanıt dosyası indirilebilir:

```http
GET /api/external/process-instances/512/document/8801/files
```

```json
[
  {
    "id": 601,
    "fileType": "EVIDENCE",
    "storedFileId": 9101,
    "fileName": "kimlik_dogrulama_kaniti.jades",
    "size": 4096,
    "linkedAt": "2026-09-15T10:04:32"
  }
]
```

```http
GET /api/external/process-instances/512/document/8801/file/9101
```

Bu dosya, SMS/konum/NFC doğrulama adımlarının kanıtını ve zaman damgasını mühürler —
gerçek bir imzalı belge değildir (bkz. [İmza Formatları ve Doğrulama —
JAdES](../signature-verification.md#formatlar)).

---

## İlgili Kaynaklar

- [Süreç Yönetimi API — Süreç Tipleri](../progress.md#surec-tipleri-processtype) — `DIJITAL_KIMLIK_DOGRULAMA` detayı
- [İmzalama Türleri](../signature-types.md) — `TCKK_TIMESTAMP` / `TCKK_FACE_TIMESTAMP` / `TCKK_ONBOARDING` karşılaştırması
- [Döküman API — Dökümana İmzacı Ekle](../documents.md#8-dokumana-imzac-ekle) — `signer` nesnesi alan referansı
- [Webhook](../webhook.md) — olay tipleri ve imza doğrulama (HMAC)
- [İmza Formatları ve Doğrulama](../signature-verification.md) — JAdES kanıt dosyası
