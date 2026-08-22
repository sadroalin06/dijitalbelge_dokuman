# Dosya İmzalama API (CAdES / ASiC-E)

Bu doküman, `DOSYA_IMZALAMA` süreç tipini kullanarak **herhangi bir dosya türünü** (PDF, DOCX, XML, resim, video vb.) CAdES ayrık imza (detached signature) ile imzalatmak için kullanılan API uç noktalarını açıklar.

!!! info "Bu akış PDF üzerine görünür imza basmaz"
    `DOSYA_IMZALAMA`, [Belge İmzalama](progress.md) (`BELGE_IMZALAMA`) akışından farklıdır: dosyanın içeriği **değiştirilmez**, imza dosyanın **dışında**, ayrık bir CAdES imzası olarak üretilir. Bu nedenle yalnızca PDF değil, **herhangi bir dosya türü** imzalanabilir; `visibleSignature` (imza konumu) alanı bu akışta **kullanılmaz**.

---

## Ne Zaman Kullanılır

| Senaryo | Süreç Tipi |
|---|---|
| Sözleşmeyi PDF üzerinde görünür imza/kaşe ile imzalatmak | [`BELGE_IMZALAMA`](progress.md) |
| PDF, DOCX, XML, görsel gibi **herhangi bir dosyayı** değiştirmeden, ayrık imzayla (`.p7s`/`.asice`) imzalatmak; birden fazla dosyayı **tek imzayla** imzalatmak | `DOSYA_IMZALAMA` |
| Belge üretmeden yalnızca kimlik doğrulamak | [`DIJITAL_KIMLIK_DOGRULAMA`](progress.md#süreç-tipleri-processtype) |

---

## Özet

| Özellik | Değer |
|---------|-------|
| Base URL | `https://app.dijitalbelge.com/api/external` |
| Kimlik Doğrulama | `X-Client-Id`, `X-Client-Secret` — bkz. [Kimlik Doğrulama](authentication.md) |
| İmza Formatı | CAdES detached, **ETSI TS 102 918 ASiC-E** container (`.asice`, `application/vnd.etsi.asic-e+zip`) |
| İzin verilen imza türleri | Yalnızca `EIMZA` (E-İmza) ve `MOBILE_IMZA` (Mobil İmza) — bkz. [İmzalama Türleri](signature-types.md) |

---

## Nasıl Çalışır

```
1. Süreç oluştur            → processType: "DOSYA_IMZALAMA"
2. Belge(ler) ekle           → POST .../document/single  (her dosya türü, base64)
3. İmzacı(lar)ı sürece bağla → POST .../signers/all-documents  (TEK çağrı → TÜM belgelere)
4. Süreci başlat             → PUT  .../status/start
5. (imzacı imzalar)          → imzalama ekranı üzerinden veya masaüstü/mobil istemciyle
6. Durumu/webhook'u izle     → GET  .../{processId}  veya DOCUMENT_SIGNED webhook'u
7. İmzalı container'ı indir  → GET  .../signers/{signerId}/signature/file  (.asice)
```

Sistem, sürece eklenen dosyaları temsil eden **tek bir gizli "imza belgesi" (signing control document)** oluşturur. Sürece kaç imzacı eklerseniz ekleyin, her imzacı bu **tek** belge üzerinden imza atar; imzaladığında sürecin **o anda yüklü olan tüm gerçek dosyaları** tek bir ASiC-E container içine konup imzalanır. Bu nedenle:

- Bir imzacıyı sürece bağlamak için döküman bazında değil, **tek bir çağrıyla tüm sürece** (`/signers/all-documents`) bağlanır.
- Bir imzacının görevini oluşturduktan **sonra** sürece yeni belge eklerseniz, o imzacı henüz imzalamadıysa yeni belge de imza kapsamına dahil olur (manifest, imzalama anında o anki belge listesi okunarak üretilir).

---

## Endpoint Özeti

| Method | Path | Scope | Açıklama |
|--------|------|-------|----------|
| `POST` | `/process-instances` | `process:start` | Süreç oluştur (`processType: "DOSYA_IMZALAMA"`) |
| `POST` | `/process-instances/{processId}/document/single` | `document:write` | Sürece dosya ekle |
| `POST` | `/process-instances/{processId}/signers/all-documents` | `document:sign` | İmzacıyı sürecin tüm belgelerine tek seferde bağla |
| `DELETE` | `/process-instances/{processId}/signer/{signerId}` | `document:sign` | İmzacıyı süreçten kaldır (tüm görevleri kapsar) |
| `PUT` | `/process-instances/{processId}/status/start` | `process:start` | Süreci başlat |
| `GET` | `/process-instances/{processId}` | `process:status` | Süreç ve imzacı durumunu getir |
| `GET` | `/process-instances/{processId}/signers/{signerId}/signature/file` | `document:read` | İmzacının tamamladığı `.asice` dosyasını indir |
| `GET` | `/process-instances/{processId}/signers/{signerId}/signature/verify` | `document:read` | İmzacının `.asice` dosyasını sunucu tarafında doğrula |
| `GET` | `/process-instances/{processId}/download-zip` | `document:read` | Sürecin tüm belgelerini + imza dosyalarını ZIP olarak indir |

> İmzacı kayıtlarını oluşturma/arama (`/external/signers/**`) için [İmzacı API](signers.md) sayfasına bakın — `identityNumber`/`fullName` ile önce bir imzacı kaydı oluşturup dönen `id`'yi burada kullanabilirsiniz.

---

## 1. Süreç Oluştur

**Scope:** `process:start`

```http
POST {baseURL}/process-instances
```

```json
{
  "name": "Toplu Belge İmzalama Süreci",
  "processType": "DOSYA_IMZALAMA"
}
```

!!! warning "`processType` zorunlu olarak gönderilmelidir"
    Gönderilmezse süreç varsayılan olarak `BELGE_IMZALAMA` tipinde oluşur ve bu sayfadaki uç noktalar (`signers/all-documents`) beklenen şekilde çalışmaz.

**Yanıt — 201 Created**

```json
{
  "id": 301,
  "accountId": 202,
  "name": "Toplu Belge İmzalama Süreci",
  "statusCode": "NEW",
  "processType": "DOSYA_IMZALAMA",
  "signers": [],
  "documents": [],
  "accessToken": "aB3xQ1z",
  "createdAt": "2026-08-22T10:00:00"
}
```

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"name": "Toplu Belge İmzalama Süreci", "processType": "DOSYA_IMZALAMA"}'
```

---

## 2. Belge(ler) Ekle

Her dosya türü desteklenir (PDF, DOCX, XML, JPG, MP4 vb.). Aynı sürece birden fazla belge eklenebilir — hepsi aynı imzacı(lar) tarafından **tek imzayla** imzalanır.

**Scope:** `document:write`

```http
POST {baseURL}/process-instances/{processId}/document/single
```

```json
{
  "fileName": "sozlesme.docx",
  "description": "Ana sözleşme",
  "base64": "UEsDBBQ...",
  "mustuploaded": true
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `fileName` | string | Evet | Dosya adı (uzantısıyla birlikte) |
| `base64` | string | Evet | Dosyanın Base64 içeriği |
| `description` | string | Hayır | Açıklama |
| `contentType` | string | Hayır | MIME türü. **Boş bırakılması önerilir** — belirtilmezse içerikten otomatik algılanır (Apache Tika) |
| `mustuploaded` | boolean | Hayır | Yükleme zorunluluğu |

!!! note "`mustsigned`, `addpublicsigned`, `signings`, `adds` bu akışta kullanılmaz"
    `DOSYA_IMZALAMA` sürecinde imza görevi, dosya bazında değil **süreç bazında** ([bkz. adım 3](#3-imzaciyi-surece-bagla-tum-belgeler)) tanımlanır; bu yüzden `mustsigned` sunucu tarafından otomatik olarak `false` yapılır. `signings`/`adds` ile PDF üzerine metin/QR/imza konumu tanımlamak (bkz. [Döküman API](documents.md#signings-tek-kullanımlık-imzacı-tanımı)) yalnızca `BELGE_IMZALAMA` sürecinde anlamlıdır.

**Yanıt — 201 Created**

```json
{
  "id": 5501,
  "fileName": "sozlesme.docx",
  "uploaded": true,
  "signed": false
}
```

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/301/document/single \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "fileName": "sozlesme.docx",
    "base64": "UEsDBBQ..."
  }'
```

Aynı çağrıyı sürece eklenecek her belge için tekrarlayın.

---

## 3. İmzacıyı Sürece Bağla (Tüm Belgeler)

İmzacıyı, sürece o ana kadar eklenmiş (ve ileride eklenecek) **tüm belgelere** tek seferde bağlar. İmzacı önceden [İmzacı API](signers.md) ile kayıtlı olmalıdır (`signerId`).

**Scope:** `document:sign`

```http
POST {baseURL}/process-instances/{processId}/signers/all-documents
```

```json
{
  "signerId": 138,
  "signatureTypeId": 3,
  "stepOrder": 1,
  "mustSign": true
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `signerId` | number | **Evet** | Hesaba kayıtlı imzacının ID'si |
| `signatureTypeId` | number | Hayır | İmza türü ID'si. Belirtilmezse varsayılan **EIMZA**. **Yalnızca `EIMZA` veya `MOBILE_IMZA` kabul edilir** |
| `stepOrder` | number | Hayır | İmzalama sırası (birden fazla imzacı varsa) |
| `mustSign` | boolean | Hayır | İmzanın zorunlu olup olmadığı |

!!! warning "İmza türü kısıtı"
    `DOSYA_IMZALAMA` sürecinde `signatureTypeId`, `EIMZA` veya `MOBILE_IMZA` dışında bir türe (ör. `SMSOTP_TIMESTAMP`, `TCKK_TIMESTAMP`) karşılık geliyorsa istek **400 Bad Request** ile reddedilir: *"DOSYA_IMZALAMA sürecinde yalnızca E-İmza veya Mobil İmza kullanılabilir."* İmza türü ID'lerini [Referans API](reference-api.md) üzerinden çekebilirsiniz.

**Yanıt — 200 OK**

```json
[ 771 ]
```

Yanıt, oluşturulan/güncellenen imza görevinin (`taskId`) tek elemanlı bir listesidir — bu ID, [imza dosyasını indirme](#6-imzali-container-asice-dosyasini-indirme) adımındaki `taskId` ile eşleşir.

#### Birden Fazla İmzacı — Sıralı İmza Zinciri

Aynı süreç için bu endpoint birden fazla kez farklı `signerId` ile çağrılabilir. Her imzacı, kendi sırası geldiğinde imzasını **bir önceki imzacının imzasını da içeren** aynı ASiC-E container'ının üzerine ekler; sonuçta tek bir `.asice` dosyasında tüm imzacıların imzaları birikmiş olur. Süreç, **tüm imzacıların** görevi tamamlanana kadar `IN_PROGRESS` durumunda kalır; son imzacı tamamladığında `COMPLETED` olur.

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/301/signers/all-documents \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"signerId": 138, "signatureTypeId": 3, "stepOrder": 1, "mustSign": true}'
```

---

### İmzacıyı Kaldır

**Scope:** `document:sign`

```http
DELETE {baseURL}/process-instances/{processId}/signer/{signerId}
```

İmzacının bu süreçteki (henüz imzalanmamış) tüm görevlerini pasife alır.

```bash
curl -X DELETE https://app.dijitalbelge.com/api/external/process-instances/301/signer/138 \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## 4. Süreci Başlat

**Scope:** `process:start`

```http
PUT {baseURL}/process-instances/{processId}/status/start
```

Süreç başlatılmadan imzacılar imzalama ekranına erişemez. Detaylar için [Süreç API](progress.md#3-süreci-başlat) sayfasına bakın.

---

## 5. Süreç / İmza Durumunu Takip Etme

```http
GET {baseURL}/process-instances/{processId}
```

Süreç durumları (`NEW`, `STARTED`, `IN_PROGRESS`, `COMPLETED`, `CANCELED`, `DELETED`) için bkz. [Süreç API — Süreç Durumları](progress.md#süreç-durumları).

Anlık polling yerine [Webhook](webhook.md) kullanmanız önerilir — bkz. [aşağıdaki bölüm](#webhook-olayları).

---

## 6. İmzalı Container (.asice) Dosyasını İndirme

Bir imzacı imzasını tamamladığında, o imzaya kadarki tüm imzaları içeren **tek `.asice` dosyasını** indirebilirsiniz.

**Scope:** `document:read`

```http
GET {baseURL}/process-instances/{processId}/signers/{signerId}/signature/file
```

**Yanıt — 200 OK**

```json
{
  "accountId": 202,
  "processId": 301,
  "fileName": "manifest_process301.asice",
  "content": "UEsDBBQ...",
  "contentType": "application/vnd.etsi.asic-e+zip"
}
```

`content` alanı, `.asice` dosyasının Base64 içeriğidir — çözüp diske yazdığınızda standart bir ZIP/ASiC-E container elde edersiniz.

!!! tip "Tüm süreci tek seferde indirmek isterseniz"
    `GET {baseURL}/process-instances/{processId}/download-zip` ile sürecin tüm orijinal belgelerini ve imza dosyalarını tek bir ZIP içinde indirebilirsiniz.

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/301/signers/138/signature/file \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## 7. İmza Doğrulama

`.asice` container'ının bütünlüğünü ve içindeki CAdES imza(lar)ını sunucu tarafında doğrulatabilirsiniz.

**Scope:** `document:read`

```http
GET {baseURL}/process-instances/{processId}/signers/{signerId}/signature/verify
```

**Yanıt — 200 OK**

```json
{
  "detectedType": "ASICE",
  "valid": true,
  "message": "Container ve tüm imzalar geçerli",
  "asice": {
    "containerValid": true,
    "mimeType": "application/vnd.etsi.asic-e+zip",
    "allFilesMatch": true,
    "valid": true,
    "signatures": [
      {
        "signerName": "Ali Veli",
        "signingTime": "2026-08-22T10:15:00",
        "integrityValid": true,
        "digestMatches": true,
        "certificateValidAtSignTime": true,
        "timestampValid": true,
        "cadesLevel": "CAdES-B-T"
      }
    ],
    "files": [
      { "name": "sozlesme.docx", "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "presentInContainer": true, "digestMatches": true }
    ]
  }
}
```

| Alan | Açıklama |
|---|---|
| `detectedType` | `ASICE` \| `PDF` \| `UNKNOWN` — dosya türü otomatik algılanır |
| `valid` | Container + tüm imzalar + tüm dosya hash'leri geçerliyse `true` |
| `asice.signatures[]` | Container içindeki her bir CAdES imzasının detayı (imzacı, sertifika, zaman damgası geçerliliği) |
| `asice.files[]` | Container'daki her veri dosyasının, manifestteki hash ile eşleşip eşleşmediği |

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/301/signers/138/signature/verify \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## Webhook Olayları

Bir imzacı imzasını tamamladığında `DOCUMENT_SIGNED` webhook'u tetiklenir:

```json
{
  "event": "DOCUMENT_SIGNED",
  "data": {
    "processId": 301,
    "taskCount": 1,
    "fileName": "manifest_process301.asice",
    "signType": "CADES"
  }
}
```

Tüm imzacılar tamamladığında ayrıca `PROCESS_STATUS_CHANGED` (`newStatus: "COMPLETED"`) webhook'u gönderilir. Webhook kurulumu, imza doğrulama (HMAC) ve diğer olay tipleri için [Webhook](webhook.md) sayfasına bakın.

!!! note
    `fileName` alanı artık `.json.p7s` değil **`.asice`** uzantısıyla gelir (ASiC-E container formatına geçiş sonrası).

---

## Hata Durumları

| HTTP Kodu | Durum | Açıklama |
|---|---|---|
| `400` | `"DOSYA_IMZALAMA sürecinde yalnızca E-İmza veya Mobil İmza kullanılabilir."` | `signers/all-documents` isteğinde izin verilmeyen bir `signatureTypeId` gönderildi |
| `400` | `"Bu imzacı zaten imzalamıştır."` | Zaten imzasını tamamlamış bir imzacı için tekrar görev güncellenmeye çalışıldı |
| `400` | `"Bu belge grubu şu anda başka bir imzacı tarafından imzalanıyor, lütfen kısa bir süre sonra tekrar deneyin"` | Aynı belge kümesi için eşzamanlı imzalama çakışması (1 dk içinde tekrar deneyin) |
| `404` | `"İmzacı bulunamadı"` / `"Process bulunamadı"` | Geçersiz `signerId` / `processId` |
| `404` | `"Bu imzacıya ait imza dosyası bulunamadı"` | `signature/file` — imzacı henüz imzalamadı |

Genel hata formatı için bkz. [Hata Kodları](errors.md).

---

## Tam Akış Örneği

```bash
BASE="https://app.dijitalbelge.com/api/external"
AUTH=(-H "X-Client-Id: app_xxxxx" -H "X-Client-Secret: secret_xxxxx")

# 1. Süreç oluştur
PROCESS_ID=$(curl -s -X POST "$BASE/process-instances" "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Toplu Belge İmzalama","processType":"DOSYA_IMZALAMA"}' | jq -r '.id')

# 2. Belge ekle
curl -s -X POST "$BASE/process-instances/$PROCESS_ID/document/single" "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d '{"fileName":"sozlesme.docx","base64":"UEsDBBQ..."}'

# 3. İmzacıyı sürece bağla (EIMZA)
curl -s -X POST "$BASE/process-instances/$PROCESS_ID/signers/all-documents" "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d '{"signerId": 138, "signatureTypeId": 3, "stepOrder": 1, "mustSign": true}'

# 4. Süreci başlat
curl -s -X PUT "$BASE/process-instances/$PROCESS_ID/status/start" "${AUTH[@]}"

# (imzacı süreç bağlantısından imzasını tamamlar — bkz. webhook: DOCUMENT_SIGNED)

# 5. İmzalı .asice dosyasını indir
curl -s "$BASE/process-instances/$PROCESS_ID/signers/138/signature/file" "${AUTH[@]}"
```

---

## İlgili Kaynaklar

- [Süreç API](progress.md)
- [İmzacı API](signers.md)
- [İmzalama Türleri](signature-types.md)
- [İmza Formatları ve Doğrulama](signature-verification.md)
- [Webhook](webhook.md)
- [Referans API](reference-api.md)
- [Hata Kodları](errors.md)
