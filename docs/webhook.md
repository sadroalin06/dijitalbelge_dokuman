# Webhook

Sistem olayları gerçekleştiğinde, kayıtlı ve aktif webhook URL'lerine **HTTP POST** olarak bildirim gönderilir.

---

## Webhook Yapılandırması

> Webhook ayarları **yönetim paneli (UI)** üzerinden yapılır.

---

## Webhook Listele

```http
GET /api/external/webhooks
```

**Yanıt:**

```json
[
  {
    "id": 1,
    "url": "https://sizin-sistemiz.com/webhook",
    "active": true,
    "createdAt": "2026-06-29T10:00:00"
  }
]
```

---

## Webhook Oluştur

```http
POST /api/external/webhooks
```

**İstek Gövdesi:**

```json
{
  "url": "https://sizin-sistemiz.com/webhook",
  "secret": "gizli-anahtar-buraya"
}
```

> `secret` tanımlıysa her istekte `X-Webhook-Signature: sha256=<hmac>` header'ı eklenir.

**Yanıt:** `201 Created`

---

## Webhook Güncelle

```http
PUT /api/external/webhooks/{id}
```

**İstek Gövdesi:**

```json
{
  "url": "https://yeni-adres.com/webhook",
  "active": false
}
```

---

## Webhook Sil

```http
DELETE /api/external/webhooks/{id}
```

**Yanıt:** `204 No Content`

---

## Webhook Olayları

Başarısız teslimatlar otomatik yeniden denenir:

| Deneme | Bekleme |
|--------|---------|
| 1. hata | 2 dakika sonra |
| 2. hata | 10 dakika sonra |
| 3. hata | Kalıcı hata |

### Genel Payload Yapısı

```json
{
  "event": "DOCUMENT_SIGNED",
  "timestamp": "2026-06-29T14:30:00",
  "accountId": 5,
  "data": { }
}
```

### İstek Başlıkları

| Header | Açıklama |
|--------|----------|
| `Content-Type` | `application/json` |
| `X-Webhook-Event` | Olay tipi (ör. `DOCUMENT_SIGNED`) |
| `X-Webhook-Attempt` | Kaçıncı deneme (1, 2, 3) |
| `X-Webhook-Signature` | `sha256=<hmac>` — yalnızca secret tanımlıysa |

---

## Olay Tipleri

### `PROCESS_STATUS_CHANGED`

Süreç durumu değiştiğinde tetiklenir (başlatma, tamamlama, iptal).

```json
{
  "event": "PROCESS_STATUS_CHANGED",
  "data": {
    "processId": 123,
    "processName": "Sözleşme İmza Süreci",
    "newStatus": "COMPLETED",
    "referenceCode": "abc-123"
  }
}
```

---

### `DOCUMENT_ADDED`

Sürece yeni döküman eklendiğinde tetiklenir.

```json
{
  "event": "DOCUMENT_ADDED",
  "data": {
    "processId": 123,
    "documentId": 45,
    "documentName": "sozlesme.pdf",
    "documentType": "Sözleşme Formu"
  }
}
```

> `documentType` yalnızca taslaktan (`document-type`) eklenen dökümanlar için dolu gelir.

---

### `DOCUMENT_UPLOADED`

Bir dökümana dosya yüklendiğinde tetiklenir.

```json
{
  "event": "DOCUMENT_UPLOADED",
  "data": {
    "processId": 123,
    "documentId": 45,
    "documentName": "sozlesme.pdf"
  }
}
```

---

### `DOCUMENT_SIGNED`

Bir döküman imzalandığında tetiklenir.

```json
{
  "event": "DOCUMENT_SIGNED",
  "data": {
    "processId": 123,
    "documentId": 45,
    "documentName": "sozlesme.pdf",
    "allSigned": true
  }
}
```

> `allSigned: true` → dökümanın tüm imzacıları imzalamış demektir.

CAdES akışında ek olarak şu yapı döner:

```json
{
  "event": "DOCUMENT_SIGNED",
  "data": {
    "processId": 123,
    "taskCount": 3,
    "fileName": "manifest_process123.json.p7s",
    "signType": "CADES"
  }
}
```

---

### `DOCUMENT_APPROVED`

Döküman onay durumu değiştiğinde tetiklenir.

```json
{
  "event": "DOCUMENT_APPROVED",
  "data": {
    "processId": 123,
    "documentId": 45,
    "documentName": "sozlesme.pdf",
    "status": "APPROVED"
  }
}
```

| `status` | Anlam |
|----------|-------|
| `APPROVED` | Onaylandı |
| `REJECTED` | Reddedildi |
| `REVOKED` | Geri alındı |

---

## İmza Doğrulama (HMAC-SHA256)

Webhook'un sisteminizden geldiğini doğrulamak için `X-Webhook-Signature` başlığını kullanın:

=== "Python"

    ```python
    import hmac, hashlib

    def verify(secret: str, payload: str, signature: str) -> bool:
        expected = "sha256=" + hmac.new(
            secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    ```

=== "JavaScript"

    ```javascript
    const crypto = require('crypto');

    function verify(secret, payload, signature) {
      const expected = 'sha256=' + crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');
      return crypto.timingSafeEqual(
        Buffer.from(expected), Buffer.from(signature)
      );
    }
    ```
