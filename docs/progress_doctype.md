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
| id | İmza sırası |
| signer | İmzacı  bağlama|
| signer->id | Tanımlı İmzacı id |
| signer->fullName | Yeni İmzacı İsim ve soyismi |
| signer->email | Yeni İmzacı email |
| signer->phone | Yeni İmzacı telefon |
| signer->identityNumber | Yeni İmzacı TC kimlik numarası |

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
