# Karşılıklı Elektronik Sözleşme İmzalama

Bu örnek, **iki tarafın da elektronik imza (E-İmza) ile imzaladığı** karşılıklı bir sözleşme sürecinin API aracılığıyla nasıl kurulacağını adım adım açıklar. Tipik kullanım alanı; iki şirket veya bir şirket ile bir gerçek/tüzel kişi arasında imzalanan **karşılıklı sözleşmelerdir** (ör. hizmet sözleşmesi, iş birliği sözleşmesi, tedarik sözleşmesi).

| Taraf | Rol | İmza Türü |
|-------|-----|-----------|
| **Taraf A** | Sözleşmeyi başlatan taraf (1. sıra) | E-İmza |
| **Taraf B** | Karşı taraf (2. sıra) | E-İmza |

!!! tip "Ek Evrak / Destekleyici Belgeler (Kurumsal Sözleşmelerde)"
    Özellikle **kurumsal sözleşmelerde**, taraflardan birinin imza yetkisini kanıtlayan **imza sirküleri** gibi destekleyici belgelerin de süreçle birlikte talep edilmesi gerekebilir. Bu belgeler ayrı bir **"yüklemeli" döküman taslağı** olarak sürece eklenir ve ilgili tarafın imzalama sırasına bağlanır. Bu sayede karşı taraf, kendi sırası geldiğinde hem sözleşmeyi imzalar hem de talep edilen ek belgeyi (ör. imza sirküleri) sisteme yükler. Detaylar için [Ek Evrak Yükleme](#ek-evrak-yukleme-imza-sirkuleri-ornegi) bölümüne bakın.

!!! tip "Sözleşmeye Sonradan İmzacı Ekleme (ör. Tanık, Kefil)"
    Süreç başladıktan sonra, taslakta önceden tanımlanmamış üçüncü bir taraf (ör. tanık, kefil) sözleşmeye imzacı olarak eklenmek istenebilir. Bu durumda taslağın `signings` sırası kullanılamaz; imzanın PDF üzerinde nereye basılacağı **taslaktan otomatik gelmez** ve isteğe `visibleSignature` ile açıkça belirtilmesi gerekir. Detaylar için [Sonradan İmzacı Ekleme](#sonradan-imzaci-ekleme-imza-konumu-belirterek) bölümüne bakın.

---

## Ön Koşullar

- Karşılıklı Sözleşme döküman taslağı arayüzden sisteme yüklenmiş olmalıdır.
- Taslak ID'si ve imzalama sırası (`signing` ID'leri) [Referans API](../reference-api.md) üzerinden öğrenilmiş olmalıdır.
- Taraf A ve Taraf B, sistemde tanımlı imzacılar olmalıdır (`signerId`). Karşı taraf sistemde tanımlı değilse, döküman eklenirken yeni imzacı bilgileriyle (`fullName`, `email`, `phone`, `identityNumber`) tanımlanabilir.
- Ek belge talep edilecekse (ör. imza sirküleri), bu belge için hesapta ayrı bir **yüklemeli döküman taslağı** (`isUpload: true`) tanımlı olmalıdır.

---

## Genel Akış

```
Süreç Oluştur → Taslaktan Döküman Ekle (Sözleşme) → (opsiyonel) Ek Belge Taslağı Ekle (İmza Sirküleri) → (opsiyonel) Sonradan İmzacı Ekle (İmza Konumu ile) → Süreci Başlat
```

İmzalama sırası: **Taraf A (1. sıra) → Taraf B (2. sıra)**

---

## Adım 1 – Süreç Oluştur

```http
POST /api/external/process-instances
```

```json
{
  "name": "Karşılıklı Sözleşme - ABC Ltd. Şti. x XYZ A.Ş."
}
```

**Yanıt:**

```json
{
  "id": 150,
  "accountId": 153,
  "createdByUserId": null,
  "name": "Karşılıklı Sözleşme - ABC Ltd. Şti. x XYZ A.Ş.",
  "statusCode": "NEW",
  "processType": "BELGE_IMZALAMA",
  "documents": [],
  "signers": [],
  "createdAt": "2026-07-25T10:00:00.000000",
  "updatedAt": "2026-07-25T10:00:00.000000",
  "responsibleBy": null,
  "accessToken": "pTTTlqd",
  "tokenExpiry": null,
  "referenceCode": null,
  "formFields": [],
  "formDesigns": []
}
```

`id` değerini (`150`) sonraki adımlarda kullanın.

---

## Adım 2 – Taslaktan Sözleşme Dökümanını Ekle

Döküman taslağındaki `signings` sıralaması (Referans API'den öğrenilir):

- `id: 60` → Taraf A (1. imzacı)
- `id: 61` → Taraf B / karşı taraf (2. imzacı)

```http
POST /api/external/process-instances/150/document/document-type
```

```json
{
  "id": 90,
  "name": "Karşılıklı Sözleşme",
  "description": "",
  "isSign": true,
  "isForm": false,
  "isActive": true,
  "isApprove": true,
  "isUpload": false,
  "document": {
    "base64": "",
    "fileName": "Sozlesme.pdf"
  },
  "signings": [
    {
      "id": 60,
      "stepOrder": 1,
      "signer": {
        "id": 108
      }
    },
    {
      "id": 61,
      "stepOrder": 2,
      "signer": {
        "id": 215
      }
    }
  ]
}
```

> `signings[0].signer.id` → Taraf A için sistemde kayıtlı imzacı (`id: 108`).  
> `signings[1].signer.id` → Taraf B / karşı taraf için sistemde kayıtlı imzacı (`id: 215`).
>
> Karşı taraf henüz sistemde kayıtlı değilse, `signer` alanı yerine `fullName`, `email`, `phone`, `identityNumber` bilgileriyle yeni bir imzacı satır içinde tanımlanabilir (bkz. [Abonelik Sözleşmesi örneği](abonelik-sozlesmesi.md)).

**Yanıt:**

```json
{
  "id": 7401
}
```

`documentId` değerini (`7401`) not edin; ek belge ve indirme adımlarında kullanılacaktır.

---

## Ek Evrak Yükleme (İmza Sirküleri Örneği)

Kurumsal sözleşmelerde karşı tarafın imza yetkisini gösteren **imza sirküleri** gibi belgeler, sözleşmeyle birlikte ayrı bir döküman olarak sürece eklenir. Bu döküman `isSign: false` ve `isUpload: true` olarak tanımlanır; yani karşı taraf bu belgeyi **imzalamaz, yalnızca yükler**. Aynı `stepOrder` değeri kullanılarak karşı tarafın imzalama sırasına bağlanır — böylece karşı taraf sürece girdiğinde hem sözleşmeyi imzalar hem de imza sirkülerini yükler.

```http
POST /api/external/process-instances/150/document/document-type
```

```json
{
  "id": 91,
  "name": "İmza Sirküleri",
  "description": "Karşı tarafın imza yetkisini gösteren belge",
  "isSign": false,
  "isForm": false,
  "isActive": true,
  "isApprove": false,
  "isUpload": true,
  "document": {
    "base64": "",
    "fileName": "imza_sirkuleri.pdf"
  },
  "signings": [
    {
      "id": 63,
      "stepOrder": 2,
      "signer": {
        "id": 215
      }
    }
  ]
}
```

| Alan | Açıklama |
|------|----------|
| `isSign: false` | Belge imzalanmaz |
| `isUpload: true` | Belge, atanan imzacı tarafından yüklenmesi zorunlu belge olarak işaretlenir |
| `signings[0].stepOrder` | Taraf B'nin sözleşme imzalama sırasıyla **aynı** (`2`) verilir, böylece aynı adımda görünür |
| `signings[0].signer.id` | Taraf B ile aynı imzacı (`215`) |

**Yanıt:**

```json
{
  "id": 7402
}
```

!!! note "Birden fazla ek belge"
    Aynı mantıkla, farklı `id` değerlerine sahip başka yüklemeli döküman taslakları da (ör. ticaret sicil gazetesi, vekaletname) sürece eklenerek karşı taraftan talep edilebilir. Her biri ayrı bir `document-type` çağrısıyla eklenir.

---

## Sonradan İmzacı Ekleme (İmza Konumu Belirterek)

Adım 2'de sözleşmeye eklenen imzacılar (Taraf A ve Taraf B), döküman taslağındaki `signings` sırasını (`id: 60`, `id: 61`) referans alır — bu sıraların PDF üzerindeki imza konumu **taslakta önceden tasarlanmıştır**. Ancak taslakta yer almayan üçüncü bir tarafın (ör. **tanık**, **kefil**) sözleşmeye sonradan imzacı olarak eklenmesi gerekebilir. Bu durumda taslağın `signings` yapısı kullanılamaz; bunun yerine [Dökümana İmzacı Ekle](../documents.md#8-dokumana-imzaci-ekle) uç noktası ile doğrudan dökümana imzacı eklenir.

!!! warning "Bu durumda imza konumu (`visibleSignature`) zorunludur"
    Bu yolla eklenen imzacı, taslaktaki önceden tasarlanmış bir imza konumuna bağlı değildir. `visibleSignature` alanı **belirtilmezse imza PDF üzerinde görünür bir konuma yerleştirilmez.** Bu nedenle yeni imzacı eklenirken sözleşme PDF'i üzerinde imzanın basılacağı sayfa ve koordinatlar (`pageNumber`, `originX`, `originY`, `width`, `height`) mutlaka gönderilmelidir.

```http
POST /api/external/process-instances/150/document/7401/signers
```

```json
{
  "signerId": 320,
  "signerName": "Mehmet Tanık",
  "order": 3,
  "isRequired": true,
  "visibleSignature": {
    "pageNumber": 1,
    "originX": 320,
    "originY": 100,
    "width": 200,
    "height": 75,
    "data": "Mehmet Tanık",
    "fontSize": 14,
    "textColor": "#000000",
    "backgroundColor": "#ffffff",
    "alignment": "CENTER"
  }
}
```

| Alan | Açıklama |
|------|----------|
| `signerId` | Sistemde kayıtlı imzacının ID'si (tanık/kefil önceden [İmzacı API](../signers.md) ile tanımlanmış olmalıdır) |
| `order` | İmzalama sırası — Taraf A (1) ve Taraf B (2) tamamlandıktan sonra imza alması için `3` verilir |
| `visibleSignature.pageNumber` | İmzanın basılacağı PDF sayfası |
| `visibleSignature.originX` / `originY` | İmzanın sayfa üzerindeki konumu (koordinat) |
| `visibleSignature.width` / `height` | İmza alanının boyutu |
| `visibleSignature.data` | İmza alanında görünecek metin (ör. imzacının adı) |
| `visibleSignature.fontSize`, `textColor`, `backgroundColor` | Metin/alan görünüm ayarları |
| `visibleSignature.alignment` | Metin hizalaması: `LEFTTOP`, `CENTER`, `RIGHTBOTTOM` |

> Tüm `visibleSignature` alanlarının tam listesi için [Döküman API – `visibleSignature` Nesnesi](../documents.md#visiblesignature-nesnesi-imza-alan-konumu) sayfasına bakın.

**Yanıt:**

```json
{
  "id": 8,
  "documentInstanceId": 7401,
  "signerId": 320,
  "signerName": "Mehmet Tanık",
  "order": 3,
  "statusCode": "PENDING",
  "visibleSignature": {
    "id": 7601,
    "pageNumber": 1,
    "originX": 320,
    "originY": 100,
    "width": 200,
    "height": 75
  },
  "createdAt": "2026-07-25T10:05:00"
}
```

> `documentId` (`7401`), Adım 2'de sözleşme eklenirken dönen `id` değeridir.

---

## Adım 3 – Süreci Başlat

```http
PUT /api/external/process-instances/150/status/start
```

**Yanıt:** `ok`

!!! success "Süreç Başlatıldı"
    Taraf A e-posta/SMS ile bildirim alır ve sözleşmeyi e-imzasıyla imzalar. Taraf A imzaladıktan sonra sıra Taraf B'ye geçer; Taraf B sürece girdiğinde hem sözleşmeyi e-imzasıyla imzalar hem de imza sirkülerini yükler. Her iki görev de tamamlanmadan süreç `COMPLETED` durumuna geçmez.

---

## İmza Sonrası – Belgeleri İndir

Süreç tamamlandıktan sonra imzalı sözleşme ve yüklenen ek belge ayrı ayrı Base64 formatında çekilebilir.

**Scope:** `document:read`

**Sözleşme:**

```http
GET /api/external/process-instances/150/document/7401/file
```

**İmza Sirküleri (yüklenen ek belge):**

```http
GET /api/external/process-instances/150/document/7402/file
```

**Yanıt:**

```json
{
  "fileName": "Sozlesme_xxxxxxxx.pdf",
  "mimeType": "application/pdf",
  "base64": "JVBERi0xLjQK...",
  "size": 1875200
}
```

> Süreç tamamlanana kadar bu uç nokta, mevcut en son yüklü/imzalı versiyonu döner.

---

## İlgili Kaynaklar

- [Süreç API](../progress.md)
- [Taslaktan Döküman Ekleme](../progress_doctype.md)
- [Döküman API (İmzacı Ekleme / İmza Konumu)](../documents.md)
- [İmzacı API](../signers.md)
- [İmzalama Türleri](../signature-types.md)
- [Abonelik Sözleşmesi İmzalama (örnek)](abonelik-sozlesmesi.md)
