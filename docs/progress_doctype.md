---
description: Döküman taslağından (doctype) süreç oluşturma API'si — hazır belge şablonlarını e-imza veya mobil imza ile hızlıca imzaya açın.
---

# Sürece döküman tasğalından belge ekleme

Bu endpoint, tanımlı bir **Döküman Taslağı** bilgisini kullanarak ilgili **süreç (process)** içerisine yeni bir belge eklemek için kullanılır. **Basit API** lisansı olan kullanıcılarda kullanılabilir. Hazırlanmış döküman taslağına tanımlı bir imzacı veya yeni imzacı bağlama işlemi yapabilirsiniz. Döküman imzalama ayarları döküman taslağında tanımlanır. Referans API üzerinden tanımlı döküman taslaklarına ulaşabilirsiniz

Belge;
- imzalanabilir
- onaylanabilir
- belgenin kullanıcı tarafından yüklenmesi veya yüklü belgeyi görüntülenmesi
bir yapı olarak tanımlanabilir.

---

## Yetkilendirme

Bu endpoint **scope bazlı yetkilendirme** kullanır.

Gerekli scope:

```
process:documenttype:write
```

---

## Endpoint

```
POST /api/external/process/{processId}/document/document-type
```

---

## Path Parametreleri

| Parametre | Tip | Açıklama |
|---------|----|---------|
| processId | Long | Belgenin ekleneceği süreç ID |

---

## Request Body – Döküman Taslağı

```json
{
    "id": 22,
    "name": "Ticari İletişim İzni (varsa)",
    "description": "",
    "isSign": true,
    "isForm": false,
    "isActive": true,
    "isApprove": true,
    "isUpload": false,
    "document": {
        "base64": "",
        "fileName": "deneme.pdf"
    },
    "signings": [
        {
            "id": 14,
           
            "signer": {
                "id": 138
                
            }
        }
    ]
}
```

---

## Alan Açıklamaları (DocumentTypeDto)

| Alan | Tip | Açıklama |
|----|----|---------|
| id | Long | Belge Taslağı ID |
| name | String | Belge adı |
| description | String | Belge açıklaması |
| isSign | Boolean | Belge imzalanabilir mi |
| isForm | Boolean | Form yapısı içeriyor mu |
| isActive | Boolean | Belge aktif mi |
| isApprove | Boolean | Onay süreci var mı |
| isUpload | Boolean | Dosya yükleme zorunlu mu |
| document | DocumentDto | Opsiyonel PDF şablonu (Base64) |
| signings | List | Belgeye ait imzacı tanımları |

---

## İmzacı Tanımı (signings)

`signings` alanı, belge üzerinde kimlerin hangi sırayla imza atacağını tanımlar. Bu alan döküman taslağındaki `signings` alanını referans verir ve ilgili taslakdaki imzalama sırasına göre tanımlanır. Taslaktaki ayarlara göre imzacı bilgisi bağlanması yapılır.

| Alan | Açıklama |
|----|---------|
| id | Taslaktadaki İmzacı sırası |
| stepOrder | İmzalama ekranındaki görünme sırası |
| visibleSignature | İmzanın PDF üzerindeki konumu (`pageNumber`, `originX`, `originY`, `width`, `height` vb.). Detaylı alan listesi için [Döküman API – `visibleSignature` Nesnesi](documents.md#visiblesignature-nesnesi-imza-alan-konumu) sayfasına bakın |
| signer | İmzacı bağlama |
| signer->id | Tanımlı İmzacı id |
| signer->fullName | Yeni İmzacı İsim ve soyismi |
| signer->email | Yeni İmzacı email |
| signer->phone | Yeni İmzacı telefon |
| signer->identityNumber | Yeni İmzacı TC kimlik numarası |

!!! warning "Önemli: `visibleSignature` (İmza Konumu)"
    `id` alanı taslaktaki önceden tasarlanmış bir imza sırasına (`signing`) referans verdiği için, o sıranın imza konumu **normalde taslakta zaten tanımlıdır** ve `visibleSignature` göndermeye gerek yoktur.

    Ancak taslakta **konumu tanımlanmamış bir sıra** kullanılıyorsa veya konum **taslaktakinden farklı** olacaksa, `visibleSignature` bu istekte açıkça gönderilerek taslaktaki konum **override edilebilir**. `visibleSignature` hem gönderilmez hem de taslakta tanımlı değilse istek **hata** verir.

!!! warning "Önemli: `stepOrder` (İmzalama Sırası)"
    `stepOrder` imzacıların imzalama ekranında hangi sırayla görüneceğini belirler. **Sırası gelmeyen imzacı imzalama ekranında görünmez.**

    - `stepOrder: 1` → İlk sırada; süreç başladığında imzalayacak kişiyi görür.
    - `stepOrder: 2` → 1. imzacı tamamlayana kadar imzalama ekranına **erişemez**.

    **Abonelik akışı örneği:**
    ```json
    "signings": [
      { "id": 75, "stepOrder": 1, "signer": { ... } },
      { "id": 77, "stepOrder": 2, "signer": { "id": 108 } }
    ]
    ```
    Abone (`stepOrder: 1`) mobil uygulamada süreci açtığında kendisini görür. İşletmeci (`stepOrder: 2`) abone imzaladıktan sonra sıraya girer.

    `stepOrder` girilmezse imzacı imzalama ekranında **hiç görünmez**.

```json
"signer": {
                 "fullName": "ali veli",
                 "email": "sadro@gmail.com",
                 "phone": "5333333333",
                 "identityNumber": "123456789011"
                
            }
```    
```json
"signer": {
                "id":24
                
            }
```            

**Taslakta konum tanımlı olmayan bir sıra için `visibleSignature` ile konum belirtme örneği:**

```json
{
  "id": 63,
  "stepOrder": 3,
  "visibleSignature": {
    "pageNumber": 1,
    "originX": 320,
    "originY": 100,
    "width": 200,
    "height": 75
  },
  "signer": {
    "id": 320
  }
}
```

---

## Response – 201 Created

```json
{
    "id": 7203,
    
}
```

---

## Hata Durumları

| HTTP Kodu | Açıklama |
|--------|---------|
| 400 | Geçersiz veri veya iş kuralı hatası |
| 401 | Yetkilendirme bilgisi yok |
| 403 | Gerekli scope yok |
| 404 | Süreç bulunamadı |

---

## Notlar

- `document` alanı opsiyoneldir.
- `signings` alanı boş bırakılırsa belge imzasız kabul edilir.
- Aynı belge türü bir süreçte birden fazla kez eklenebilir.

---

## Son Yüklü Belgeyi Getir (Base64)

Döküman eklendikten ve imzalandıktan sonra, imzalı belgenin en son halini Base64 formatında çekmek için aşağıdaki endpoint kullanılır.

**Scope:** `document:read`

```http
GET /api/external/process-instances/{processId}/document/{documentId}/file
```

**Path Parametreleri:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si (döküman eklenirken dönen `id`) |

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
| `base64` | string | Dosyanın Base64 içeriği (imzalı son versiyon) |
| `size` | number | Dosya boyutu (byte) |

> İmzalama tamamlanmadan önce çekilirse, mevcut en son dosya versiyonu döner.
