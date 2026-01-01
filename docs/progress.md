# Sürece Belge Türü Ekleme (Document Type)

Bu endpoint, tanımlı bir **Belge Türü (Document Type)** bilgisini kullanarak ilgili **süreç (process)** içerisine yeni bir belge eklemek için kullanılır.

Belge;
- imzalanabilir
- onaylanabilir
- yalnızca yükleme gerektiren
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

## Request Body – DocumentTypeDto

```json
{
  "id": 1,
  "name": "Sözleşme Formu",
  "description": "Yeni abonelik sözleşmesi için standart form",
  "isSign": true,
  "isForm": false,
  "isActive": true,
  "isApprove": false,
  "isUpload": true,
  "document": {
    "content": "<base64-pdf-content>"
  },
  "signings": [
    {
      "stepOrder": 1,
      "signatureTypeId": 2,
      "mustSign": true
    }
  ]
}
```

---

## Alan Açıklamaları (DocumentTypeDto)

| Alan | Tip | Açıklama |
|----|----|---------|
| id | Long | Belge türü ID |
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

`signings` alanı, belge üzerinde kimlerin hangi sırayla imza atacağını tanımlar.

| Alan | Açıklama |
|----|---------|
| stepOrder | İmza sırası |
| signatureTypeId | İmza tipi |
| mustSign | İmza zorunlu mu |

---

## Response – 201 Created

```json
{
  "id": 45,
  "processInstanceId": 12,
  "documentTypeId": 1,
  "status": "CREATED"
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
