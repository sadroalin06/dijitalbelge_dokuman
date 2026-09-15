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
(yalnızca Adım 3'teki `signatureTypeId` değişir).

---

## Ön Koşullar

- Panelde bir **webhook** tanımlı ve aktif olmalı (bkz. [Webhook](../webhook.md)) —
  doğrulama tamamlandığında sisteminize bildirim düşecek.
- Üyenin **TC kimlik numarası**, **cep telefonu** ve **e-posta** bilgisi, KVKK
  aydınlatma/onay süreciniz tamamlanmış şekilde elinizde olmalı.
- API kimlik bilgileriniz (`X-Client-Id` / `X-Client-Secret`) ve gerekli scope'lar:
  `process:start`, `signer:managment`, `document:sign`, `process:status`.

!!! warning "`document:write` gerekmez — hiç döküman yüklemeyeceksiniz"
    Önceki örneklerin aksine bu akışta **hiçbir aşamada dosya yüklenmez**. Aşağıda
    göreceğiniz gibi imzacıyı sürece bağladığınız tek çağrı, gizli "signing control"
    belgesini de kendisi oluşturur.

---

## Genel Akış

```
Üye "Kimliğimi Doğrula" der
        → Süreç Oluştur (processType: DIJITAL_KIMLIK_DOGRULAMA)
        → processId ↔ üyeId eşlemesini kendi veritabanınızda saklayın
        → İmzacıyı Oluştur / Bul
        → İmzacıyı Sürece Bağla (TCKK_TIMESTAMP) — döküman otomatik oluşur, ayrıca yüklenmez
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

## Adım 2 – İmzacıyı Oluştur / Bul

`DIJITAL_KIMLIK_DOGRULAMA` sürecinde imzacı, `/document/{documentId}/signers`
endpoint'indeki gibi bilgileriyle **inline** oluşturulamaz — önce hesabın imzacı
rehberinde bir `Signer` kaydı olması gerekir. Üye sisteminizde daha önce
doğrulanmamışsa `bulk-insert` ile oluşturun (kayıtlıysa bu adım atlanıp mevcut
`signerId` kullanılır):

```http
POST /api/external/signers/bulk-insert
```

```json
[
  {
    "fullName": "Ali Veli",
    "email": "ali.veli@example.com",
    "phone": "+905551112233",
    "identityNumber": "12345678901"
  }
]
```

**Yanıt:**

```json
[
  { "id": 138, "fullName": "Ali Veli" }
]
```

`id: 138` değerini bir sonraki adımda `signerId` olarak kullanın.

---

## Adım 3 – İmzacıyı `TCKK_TIMESTAMP` ile Sürece Bağla

Burada **döküman yüklenmez** — imzacıyı doğrudan sürece bağlayan tek bir çağrı
yeterlidir. `signatureTypeId: 11`, [Referans API — İmzalama
Türleri](../reference-api.md#imzalama-turleri)'nden `TCKK_TIMESTAMP` kodunun ID'sidir.

```http
POST /api/external/process-instances/512/signers/all-documents
```

```json
{
  "signerId": 138,
  "signatureTypeId": 11,
  "stepOrder": 1,
  "mustSign": true
}
```

| Alan | Açıklama |
|------|----------|
| `signerId` | Adım 2'de oluşturulan/bulunan `Signer` ID'si |
| `signatureTypeId: 11` | `TCKK_TIMESTAMP` — kimlik kartı NFC + SMS + konum + zaman damgası |
| `stepOrder` | Süreçte birden fazla kişi doğrulanacaksa sırayı belirler; tek kişilik akışta `1` |
| `mustSign` | `true` — doğrulama tamamlanmadan süreç kapanmaz |

!!! info "Belge burada, sizin göndermenize gerek kalmadan oluşur"
    Bu istek ilk kez çağrıldığında sistem, sürece ait **gizli bir "signing control"
    belgesi** (`isSigningControl: true`, dosya adı otomatik `imza_belgesi_
    DIJITAL_KIMLIK_DOGRULAMA_512` gibi üretilir) yoksa **kendisi oluşturur** ve
    imzacıyı ona bağlar — üyeye hiçbir zaman gösterilmez, indirilebilir gerçek bir
    dosya değildir (bkz. [Süreç Tipleri](../progress.md#surec-tipleri-processtype)).
    Aynı sürece birden fazla kişi ekleyecekseniz bu endpoint'i farklı `signerId` /
    `stepOrder` ile tekrar çağırmanız yeterli; hepsi aynı gizli belgeye bağlanır.

**Yanıt (HTTP 200) — oluşturulan görev ID'si:**

```json
[9]
```

`9`, bu imza/doğrulama görevinin (`DocumentSigningTask`) ID'sidir; ayrıca izlemeniz
gerekmiyorsa saklamanıza gerek yoktur — süreç durumunu her zaman `processId` (`512`)
ile sorgulayabilirsiniz.

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
    "documentName": "imza_belgesi_DIJITAL_KIMLIK_DOGRULAMA_512",
    "allSigned": true
  }
}
```

`documentId` (`8801`), Adım 3'te sizin göndermediğiniz, sistemin otomatik oluşturduğu
gizli signing-control belgesinin ID'sidir — Adım 6'daki kanıt indirme çağrısı için
webhook'tan öğrenirsiniz; ayrıca `documentName` her zaman `imza_belgesi_
<processType>_<processId>` kalıbında otomatik üretilir.

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
kanıtı) ayrı olarak saklanan JAdES kanıt dosyası indirilebilir. `documentId`'yi
webhook'tan almadıysanız (ör. henüz gelmediyse) süreç detayından da öğrenebilirsiniz:

```http
GET /api/external/process-instances/512
```

Yanıttaki `documents[0].id` alanı, aradığınız `documentId`'dir (`8801`).

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
- [Dosya İmzalama (CAdES/ASiC-E) — İmzacıyı Sürece Bağla](../dosya-imzalama.md#3-imzacy-surece-bagla-tum-belgeler) — `/signers/all-documents` endpoint'inin (DOSYA_IMZALAMA için yazılmış ama aynı yapıyı kullanan) tam alan referansı
- [İmzalama Türleri](../signature-types.md) — `TCKK_TIMESTAMP` / `TCKK_FACE_TIMESTAMP` / `TCKK_ONBOARDING` karşılaştırması
- [İmzacı API](../signers.md) — imzacı oluşturma / arama
- [Webhook](../webhook.md) — olay tipleri ve imza doğrulama (HMAC)
- [İmza Formatları ve Doğrulama](../signature-verification.md) — JAdES kanıt dosyası
