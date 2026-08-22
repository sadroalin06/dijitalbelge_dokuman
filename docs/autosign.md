---
description: Bulut İmzalama (Autosign) API'si ile TC kimlik numarasına bağlı imzacılar için otomatik e-imza işlemlerini süreçlerinizde etkinleştirin.
---

# Bulut İmzalama (Autosign)

**Bulut İmzalama**, DijitalBelge platformunun lisanslı bir hizmetidir. Hesabınıza kayıtlı ve yetkilendirilmiş bir cihazın ilgili bilgisayarda aktif olması koşuluyla, bir sürece TC kimlik numarası ile imzacı olarak eklenen kişinin belgesi **otomatik olarak imzalanır**.

Süreç üzerinde bulut imzalamayı etkinleştirmek veya devre dışı bırakmak için `/autosign` endpoint'leri kullanılır.

---

## Nasıl Çalışır?

```
  1. Hesabınıza bir cihaz kaydedilir ve yetkilendirilir
         │
         ▼
  2. Cihazın kurulu olduğu bilgisayar aktif durumdadır
         │
         ▼
  3. Sürece TC kimlik numarasıyla tanımlı imzacı eklenir
         │
         ▼
  4. /autosign endpoint'i ile süreç için bulut imzalama etkinleştirilir
         │
         ▼
  5. Sistem, kayıtlı cihazda bu TC'ye ait sertifikayı tespit eder
     ve belgeyi otomatik imzalar
         │
         ▼
  6. İmza durumu webhook veya döküman durumu sorgusuyla takip edilir
```

---

## Gereksinimler

| Gereksinim | Açıklama |
|------------|----------|
| **Lisans** | Bulut İmzalama lisansı aktif olmalıdır |
| **Kayıtlı Cihaz** | Hesabınıza en az bir cihaz kaydedilmiş ve yetkilendirilmiş olmalıdır |
| **Aktif Bağlantı** | İmzalama sırasında cihazın kurulu olduğu bilgisayar çevrimiçi ve aktif olmalıdır |
| **TC Kimlik Numarası** | İmzacının TC kimlik numarası sertifika kaydıyla eşleşmelidir |
| **IP Whitelist** | `/autosign` endpoint'leri yalnızca hesaba tanımlı IP adreslerinden çağrılabilir |

---

## Genel Bakış

| Özellik | Değer |
|---------|-------|
| Base URL | `https://app.dijitalbelge.com/api/external` |
| Kimlik Doğrulama | `X-Client-Id` / `X-Client-Secret` |
| Gerekli Scope | `autosign:write` |
| Minimum Paket | **Enterprise** |

!!! warning "IP Whitelist Zorunluluğu"
    Bu endpoint'lere yalnızca hesabınıza tanımlı IP adresleri üzerinden erişilebilir.  
    Yetkisiz IP'den gelen istekler `403 Forbidden` döner.

---

## Endpoints

### 1. Bulut İmzalamayı Etkinleştir

Belirtilen süreç için bulut imzalamayı etkinleştirir.

**Scope:** `autosign:write`

#### İstek

```http
POST {baseURL}/process-instances/{processId}/autosign
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |

#### Request Body

```json
{
  "signerId": 140,
  "expiresHours": 72
}
```

| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| `signerId` | number | **Evet** | Bulut imzalamanın uygulanacağı imzacının ID'si. Sürece daha önce eklenmiş olmalıdır. |
| `expiresHours` | number | Hayır | Geçerlilik süresi (saat). Varsayılan: **72** |

#### Doğrulama Kuralları

İstek işlenmeden önce aşağıdaki kontroller sırayla yapılır:

| Kontrol | Hata |
|---------|------|
| `signerId` alanı gönderilmemiş | `400 Bad Request` — signerId zorunludur |
| İmzacı bu süreçte kayıtlı değil | `409 Conflict` — Bu imzacı bu süreçte bulunamadı |
| İmzacının TC'sine ait hesapta aktif kayıtlı cihaz yok | `409 Conflict` — Hesapta kayıtlı aktif cihazı bulunmuyor |

Tüm kontroller geçerse yalnızca o imzacı için AutoSignProcess oluşturulur veya güncellenir.

#### Başarılı Yanıt

**HTTP 200 OK**

```json
{
  "processId": 147,
  "enabled": true,
  "expiresAt": "2026-01-08T20:00:00",
  "autoSignToken": "as_xxxxxx"
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `enabled` | boolean | Bulut imzalamanın aktif olup olmadığı |
| `expiresAt` | string | Geçerlilik bitiş tarihi (ISO 8601) |
| `autoSignToken` | string | Otomatik imzalama token'ı |

#### Örnek cURL

```bash
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/147/autosign \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{
    "signerId": 140,
    "expiresHours": 72
  }'
```

---

### 2. Bulut İmzalamayı Devre Dışı Bırak

Belirtilen süreç için etkin olan bulut imzalamayı iptal eder.

**Scope:** `autosign:write`

#### İstek

```http
DELETE {baseURL}/process-instances/{processId}/autosign
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |

#### Başarılı Yanıt

**HTTP 200 OK**

```
ok
```

#### Örnek cURL

```bash
curl -X DELETE https://app.dijitalbelge.com/api/external/process-instances/147/autosign \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## Otomatik İmzalamada Sıralama (stepOrder)

Otomatik imzalama, imzacıların `stepOrder` değerini dikkate alarak çalışır. Her döngüde yalnızca **sırası gelen** imzacılar kuyruğa alınır.

### Davranış Kuralları

| `stepOrder` değeri | Davranış |
|--------------------|----------|
| `null` veya `0` | Sıralama kontrolü yapılmaz, her zaman kuyruğa eklenir |
| `N` (N > 0) | Aynı belgedeki imzalanmamış görevlerin en düşük `stepOrder`'ı N ise kuyruğa eklenir; değilse atlanır |

### Örnek

| Adım | İmzacı | Durum | Sonuç |
|------|--------|-------|-------|
| 1 | A | İmzalamadı | Kuyruğa eklenir |
| 1 | B | İmzalamadı | Kuyruğa eklenir |
| 2 | C (oto-imza aktif) | İmzalamadı | **Atlanır** — adım 1 henüz bitmedi |

Adım 1'deki tüm imzacılar (A ve B) imzasını tamamladığında, bir sonraki döngüde C kuyruğa alınır ve otomatik imzalama gerçekleşir.

!!! warning "Önemli"
    Otomatik imzalama etkinleştirilmiş bir imzacının `stepOrder`'ı önceki adımdaki tüm imzacılar tamamlanmadan işlem **yapılmaz**. Bu davranış kasıtlıdır; sıra bekleyen imzacılar için sistemi tekrar tetiklemenize gerek yoktur, adım tamamlandığında otomatik olarak devreye girer.

---

## Tam Entegrasyon Akışı

```bash
# 1. Süreç oluştur
PROCESS_ID=$(curl -s -X POST https://app.dijitalbelge.com/api/external/process-instances \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"name": "Bulut İmza Süreci"}' | jq -r '.id')

# 2. Döküman ekle
DOC_ID=$(curl -s -X POST https://app.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/document/single \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"name":"Sözleşme.pdf","base64":"JVBERi0...","fileName":"sozlesme.pdf"}' | jq -r '.id')

# 3. TC kimlik numarasıyla tanımlı imzacıyı ekle
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/document/$DOC_ID/signers \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"signerId": 138}'

# 4. Bulut imzalamayı etkinleştir (signerId zorunlu)
curl -X POST https://app.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/autosign \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx" \
  -d '{"signerId": 138, "expiresHours": 72}'

# 5. Süreci başlat
curl -X PUT https://app.dijitalbelge.com/api/external/process-instances/$PROCESS_ID/status/start \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

---

## İmza Durumu Takibi

İmzalama tamamlanınca durum güncellenir. İki yöntemle takip edebilirsiniz:

=== "Döküman Durumu Sorgulama"

    ```bash
    curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147/document/7203 \
      -H "X-Client-Id: app_xxxxx" \
      -H "X-Client-Secret: secret_xxxxx"
    ```

    Yanıttaki `statusCode` alanını izleyin:

    | Durum | Açıklama |
    |-------|----------|
    | `PENDING` | İmza bekleniyor |
    | `SIGNED` | İmzalandı |
    | `FAILED` | İmzalama başarısız |
    | `EXPIRED` | İmzalama süresi doldu |

=== "Webhook ile Anlık Bildirim"

    Webhook tanımlıysa sistem, imzalama tamamlandığında belirlediğiniz URL'ye **POST** isteği gönderir.

    ```json
    {
      "event": "DOCUMENT_SIGNED",
      "processId": 147,
      "documentId": 7203,
      "signerId": 138,
      "signedAt": "2026-01-06T10:00:00"
    }
    ```

---

## Hata Yanıtları

| HTTP Kodu | Açıklama |
|-----------|----------|
| `400` | `signerId` gönderilmemiş |
| `401` | Kimlik doğrulama başarısız |
| `403` | IP adresi whitelist'te tanımlı değil veya scope yetersiz |
| `404` | Süreç bulunamadı |
| `409` | İmzacı bu süreçte bulunamadı veya hesapta aktif kayıtlı cihaz yok |
| `500` | Sunucu hatası |

---

## Sık Sorulan Sorular

**Cihaz çevrimdışıysa ne olur?**  
İmzalama tetiklenir ancak cihaz bağlantı kurulana kadar bekleme durumunda kalır. Belirli bir süre sonra `FAILED` durumuna düşer.

**Birden fazla kayıtlı cihaz olabilir mi?**  
Evet. Hesabınıza birden fazla cihaz kaydedebilirsiniz. Sistem, imzacının TC numarasıyla eşleşen aktif cihazı seçer.

**TC numarası yanlış girilirse ne olur?**  
Eşleşen sertifika bulunamaz, imzalama tetiklenmez ve döküman `PENDING` durumunda kalır.

---

## İlgili Sayfalar

- [Süreç API](progress.md)
- [İmzacı API](signers.md)
- [Yetkiler (Scopes)](scopes.md)
