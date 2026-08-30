---
description: DijitalBelge External API için hazır Postman koleksiyonu — tüm uçları içeren, değişkenleri otomatik dolduran indirilebilir dosya.
---

# Postman Koleksiyonu

DijitalBelge External API'nin **tüm uçlarını** içeren hazır Postman koleksiyonu.

## İndir

- [**Koleksiyon** — `DijitalBelge-External-API.postman_collection.json`](assets/postman/DijitalBelge-External-API.postman_collection.json){ download }
- [**Ortam** — `DijitalBelge-External-API.postman_environment.json`](assets/postman/DijitalBelge-External-API.postman_environment.json){ download }

## Kurulum

1. Postman → **Import** → iki dosyayı da yükle.
2. Sağ üstten **DijitalBelge External - TEST** ortamını seç.
3. Ortam değişkenlerini doldur (**Current Value** alanı — yalnızca Initial değil):
   - `clientId` / `clientSecret` — Panel > Ayarlar > API Entegrasyonu > Yeni Uygulama
   - `baseUrl` — TEST: `https://testapp.dijitalbelge.com:8443/api/external` · PROD: `https://app.dijitalbelge.com/api/external`

> `{{clientId}}` / `{{clientSecret}}` **Current Value** boşsa istekler **401** döner.

## İçerik

| Klasör | Uçlar |
|--------|-------|
| **Reference** | `partytype`, `documenttype`, `signaturetype`, `form` |
| **Signers** | `search`, `bulk-insert`, `update`, `deactivate` |
| **Process Definitions** | taslakları listele, detay, `POST /{id}/start` (taslaktan süreç başlat) |
| **Process Instances** | oluştur, detay, `qr` (PNG), `status/start · cancel · complete`, sil, `download-zip` |
| **Documents** | `document/single`, `document/document-type`, belge/dosya getir, dosya listesi, dosya (storedFileId), sil |
| **Signing Tasks** | belgeye imzacı ekle, `signers/all-documents` (DOSYA_IMZALAMA), imzacı çıkar, imza dosyası + doğrulama (task & signer bazlı) |
| **AutoSign** | etkinleştir / devre dışı |
| **E-İmza Login (Sümen)** | `auth/tx`, `auth/tx/{id}`, `auth/tx/{id}/audit` |
| **Mobil İmza Login** | `auth/operators`, `{operator}/mobiltx`, `{operator}/mobil/{id}` |

## Otomatik değişkenler

Her istekte `X-Client-Id` + `X-Client-Secret` header'ları açıkça tanımlıdır.
Test scriptleri yanıttan şu değişkenleri doldurur; böylece uçtan uca akış tek tıkla ilerler:

`definitionId`, `processId`, `documentId`, `signerId`, `taskId`, `storedFileId`, `loginTxId`

## Önerilen akış

### Taslaktan süreç (kısa yol)

1. **Process Definitions** → `GET /` → `definitionId` set edilir
2. **Signers** → `POST bulk-insert` → `signerId` set edilir
3. **Process Definitions** → `POST /{definitionId}/start`
   (`signers`, gerekirse `documentSignerOverrides` / `formValues`, `autoStart: true`)

### Elle süreç kurma

1. **Process Instances** → `POST /` → `processId`
2. **Documents** → `POST document/single` (veya `document-type`) → `documentId`
3. **Signing Tasks** → `POST document/{documentId}/signers` → `taskId`
4. **Process Instances** → `PUT status/start`
5. İmza sonrası → **Signing Tasks** → `GET signers/{signerId}/signature/file` / `.../verify`

## Notlar

- **Webhook yönetimi** (`/webhooks`) bu koleksiyonda yoktur — o uç `/api/external`
  altında değildir, panel oturumu (JWT) ile korunur. Webhook olayları için
  [Webhook](webhook.md) sayfasına bakın.
- `base64` alanlarına gerçek PDF içeriğini koyun.
- `autosign` uçları **IP whitelist** zorunlu kılar (Enterprise).
