# Sümen Masaüstü Uygulaması API

Dijital Belge'nin masaüstü yazılımı olan **Sümen**, yerel WebSocket API'si aracılığıyla imzalama işlemleri ve cihaz yönetimi için komutlar sunar.

## Genel Bakış

**Sümen** şu özellikler sağlar:

- **Lokal WebSocket Sunucusu** - Masaüstü uygulaması WebSocket aracılığıyla komutları dinler
- **Cihaz Yönetimi** - Bağlı imza sertifikalarını ve cihazlarını listeleyebilir
- **İmza İşlemleri** - Challenge'ı imzalayabilir
- **Versiyon Kontrolü** - Uygulamanın sürümünü ve durumunu bildirebilir

---

## Özet

| Özellik | Değer |
|---------|-------|
| Protokol | WebSocket |
| Host | `localhost` |
| Port | `5134` |
| Endpoint | `/ws` |
| Bağlantı URL | `ws://localhost:5134/ws` |
| İletişim Yöntemi | JSON Komut/Cevap |

---

## Bağlantı

### WebSocket Bağlantısı Oluşturma

```javascript
const ws = new WebSocket("ws://localhost:5134/ws");

ws.onopen = () => {
  console.log("Sümen'e bağlandı");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Cevap:", message);
};

ws.onerror = (error) => {
  console.error("Hata:", error);
};

ws.onclose = () => {
  console.log("Bağlantı kesildi");
};
```

---

## Komut Sistemi

Sümen API'si komut/cevap modeline dayanır. Her komut için:

1. **requestId** - Benzersiz istek kimliği (zorunlu)
2. **command** - Çalıştırılacak komut (zorunlu)
3. **params** - Komut parametreleri (opsiyonel)

Cevaplar aynı `requestId` ile döndürülür.

---

## Komutlar

### 1. Ping - Durum Kontrolü

Sümen uygulamasının çalışıp çalışmadığını ve versiyonunu kontrol eder.

#### İstek

```json
{
  "type": "ping"
}
```

#### Başarılı Yanıt

```json
{
  "type": "pong",
  "info": {
    "status": "ok",
    "version": "1.2.0",
    "lang": "tr"
  }
}
```

| Alan | Tip | Açıklama |
|------|-----|----------|
| `type` | string | Cevap türü (`pong`) |
| `info.status` | string | Uygulama durumu (`ok`, `error` vb.) |
| `info.version` | string | Sümen versiyonu |
| `info.lang` | string | Dil ayarı |

**Anlamı:** Status "ok" ise Sümen çalışıyor ve imzalama yapılabilir durumdadır. Version "1.2.0" ise o versiyonun aktif olduğunu gösterir.

#### Örnek cURL

```bash
# WebSocket için cURL doğrudan destek vermiyor, JavaScript örneğine bakınız
```

---

### 2. Devices - Cihaz Listesi

Bağlı imza cihazları ve sertifikaları listeler.

#### İstek

```json
{
  "requestId": "req_t3jeg5qm",
  "command": "devices"
}
```

#### Başarılı Yanıt

```json
{
  "type": "devices",
  "requestId": "req_t3jeg5qm",
  "data": {
    "data": [
      {
        "id": "eb6acc1ba47df01f932e23459e68a69a60cff93a0a2f1433eb2edab3736ca282",
        "name": "AKIS_08C9150800160012",
        "atr": null,
        "label": "AKIS_08C9150800160012",
        "serial": "08C9150800160012",
        "manufacturer": "TUBITAK UEKAE",
        "certs": [
          {
            "id": "x509-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "serial": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "issuer": "CN=TÜRKTRUST Nitelikli Elektronik Sertifika Hizmetleri H7,O=TÜRKTRUST Bilgi İletişim ve Bilişim Güvenliği Hizmetleri A.Ş.,OU=Dayanak: T.C. 5070 sayılı Elektronik İmza Kanunu,L=Ankara,C=TR",
            "subject": "CN=xxx xxxx,L=ANKARA,C=TR,2.5.4.5=xxxxxxxxx",
            "notAfter": "2026-02-11T10:40:06+00:00",
            "notBefore": "2025-02-11T10:40:06+00:00",
            "subjectSerial": "xxxxxxxxxx",
            "subjectCountry": "TR",
            "subjectEmail": null,
            "keyAlgorithm": "ecdsa-with-SHA384",
            "isExpired": false,
            "providerId": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
          }
        ]
      }
    ]
  }
}
```

**Cihaz Alanları:**

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | string | Cihazın benzersiz kimliği |
| `name` | string | Cihaz adı |
| `label` | string | Cihaz etiketi |
| `serial` | string | Cihaz seri numarası |
| `manufacturer` | string | Üretici adı |
| `atr` | string/null | ATR (Answer To Reset) değeri |
| `certs` | array | Cihazda yüklü sertifikalar |

**Sertifika Alanları:**

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | string | Sertifika kimliği |
| `serial` | string | Sertifika seri numarası |
| `issuer` | string | Sertifikayı veren kuruluş |
| `subject` | string | Sertifika sahibi bilgileri |
| `notBefore` | string | Sertifika geçerlilik başlangıcı (ISO 8601) |
| `notAfter` | string | Sertifika geçerlilik sonu (ISO 8601) |
| `subjectSerial` | string | Konu seri numarası (TC Kimlik No) |
| `subjectCountry` | string | Ülke kodu |
| `subjectEmail` | string/null | E-posta adresi |
| `keyAlgorithm` | string | Kullanılan şifreleme algoritması |
| `isExpired` | boolean | Sertifika süresi dolmuş mu |
| `providerId` | string | Sağlayıcı ID (cihaz ID'si ile aynı) |

---

### 3. Sign Login - E-İmza ile Login

E-İmza Login API'sinden alınan challenge'ı sertifika ile imzalar. İmzalama işlemi Sümen uygulamasında PIN girerek gerçekleştirilir.

#### İstek

```json
{
  "requestId": "req_t3jeg5qm",
  "command": "signLogin",
  "pin": "xxxx",
  "slot": 0,
  "istest": true,
  "loginTxId": "tx_5428cebb-80d6-4530-b4bb-2c03d5beedb1",
  "challenge": "pWRTBVigLq28b1QFdeF9ZyTdBvYqSydENWj27A0ln3A="
}
```

**İstek Alanları:**

| Alan | Tip | Açıklama | Örnek |
|------|-----|----------|--------|
| `requestId` | string | Benzersiz istek kimliği | `req_t3jeg5qm` |
| `command` | string | Komut adı | `signLogin` |
| `pin` | string | Sertifika PIN kodu | `xxxxxx` |
| `slot` | number | Cihaz slot numarası | `0` |
| `istest` | boolean | Test modu mu | `true` |
| `loginTxId` | string | E-İmza Login API'den alınan LoginTx ID'si | `tx_5428cebb-80d6-4530-b4bb-2c03d5beedb1` |
| `challenge` | string | E-İmza Login API'den alınan challenge (base64) | `pWRTBVigLq28b1QFdeF9ZyTdBvYqSydENWj27A0ln3A=` |

#### Başarılı Yanıt

```json
{
  "type": "signLoginResult",
  "data": {
    "success": true,
    "status_code": 200,
    "data": {
      "loginTxId": "tx_f980f9bd-14c4-4789-a470-e65839d50d5c",
      "status": "SUCCESS"
    }
  },
  "requestId": "req_t3jeg5qm"
}
```

**Cevap Alanları:**

| Alan | Tip | Açıklama |
|------|-----|----------|
| `type` | string | Cevap türü (`signLoginResult`) |
| `data.success` | boolean | İmzalama başarılı mı |
| `data.status_code` | number | HTTP durum kodu |
| `data.data.loginTxId` | string | Login işlemi ID'si |
| `data.data.status` | string | İşlem durumu (`SUCCESS`, `FAILED` vb.) |
| `requestId` | string | İstek kimliği |

#### Başarısız Yanıtlar

**LoginTx Bulunamadı:**
```json
{
  "type": "signLoginResult",
  "requestId": "req_t3jeg5qm",
  "data": {
    "success": false,
    "status_code": 404,
    "error": "loginTx not found"
  }
}
```

**Hatalı PIN:**
```json
{
  "type": "signLoginResult",
  "requestId": "req_t3jeg5qm",
  "data": {
    "success": false,
    "status_code": 401,
    "error": "Invalid PIN"
  }
}
```

**Sertifika Bulunamadı:**
```json
{
  "type": "signLoginResult",
  "requestId": "req_t3jeg5qm",
  "data": {
    "success": false,
    "status_code": 404,
    "error": "Certificate not found"
  }
}
```

**Geçersiz Slot:**
```json
{
  "type": "signLoginResult",
  "requestId": "req_t3jeg5qm",
  "data": {
    "success": false,
    "status_code": 400,
    "error": "Invalid slot number"
  }
}
```

**Sertifika Süresi Dolmuş:**
```json
{
  "type": "signLoginResult",
  "requestId": "req_t3jeg5qm",
  "data": {
    "success": false,
    "status_code": 403,
    "error": "Certificate expired"
  }
}
```

#### İş Akışı

1. İlk olarak [E-İmza Login API](esign.md) ile `POST /external/auth/tx` endpoint'ine istek göndererek `loginTxId` ve `challenge` alınır
2. Sümen'de `signLogin` komutu gönderilerek PIN ile imzalama gerçekleştirilir
3. İmza başarılı ise `signature` alanı doldurulur
4. İmza başarısızsa hata alanı doldurulur (hatalı PIN, sertifika bulunamadı vb.)
5. Başarılı imzadan sonra [E-İmza Login API](esign.md) ile `GET /external/auth/tx/{loginToken}` endpoint'ine `signature` parametresi gönderilerek kullanıcı kimliği doğrulanır



---

## İstek/Yanıt Yapısı

### Genel İstek Formatı

```json
{
  "requestId": "unique-request-id",
  "command": "command-name",
  "params": {
    "key": "value"
  }
}
```

### Genel Cevap Formatı

```json
{
  "type": "response-type",
  "requestId": "unique-request-id",
  "data": {
    "key": "value"
  },
  "error": null
}
```

### Hata Cevabı

```json
{
  "type": "error",
  "requestId": "unique-request-id",
  "error": {
    "code": "ERROR_CODE",
    "message": "Hata açıklaması"
  }
}
```

---

## JavaScript Örneği

### Ping Komutu

```javascript
function sendPing(ws) {
  const message = {
    type: "ping"
  };
  ws.send(JSON.stringify(message));
}

function handlePingResponse(data) {
  console.log("Sümen Versiyonu:", data.info.version);
  console.log("Durum:", data.info.status);
  if (data.info.status === "ok") {
    console.log("Sümen çalışıyor ve imzalama yapılabilir");
  }
}
```

### Devices Komutu

```javascript
function requestDevices(ws) {
  const requestId = "req_" + Math.random().toString(36).substr(2, 9);
  const message = {
    requestId: requestId,
    command: "devices"
  };
  ws.send(JSON.stringify(message));
  return requestId;
}

function handleDevicesResponse(data) {
  const devices = data.data.data;
  console.log(`${devices.length} cihaz bulundu`);
  
  devices.forEach(device => {
    console.log(`Cihaz: ${device.name}`);
    console.log(`Üretici: ${device.manufacturer}`);
    console.log(`Sertifikalar:`);
    
    device.certs.forEach(cert => {
      console.log(`  - ${cert.subject}`);
      console.log(`    Süresi: ${cert.notBefore} - ${cert.notAfter}`);
      console.log(`    Süresi Dolmuş: ${cert.isExpired}`);
    });
  });
}

// WebSocket bağlantısı ve mesaj işleme
const ws = new WebSocket("ws://localhost:5134/ws");

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === "pong") {
    handlePingResponse(message);
  } else if (message.type === "devices") {
    handleDevicesResponse(message);
  } else if (message.type === "error") {
    console.error("Hata:", message.error.message);
  }
};

ws.onopen = () => {
  console.log("Bağlandı");
  sendPing(ws);
  requestDevices(ws);
};
```

---

## Hata Durumları

### Bağlantı Hatası

Sümen çalışmıyorsa veya WebSocket erişilemez:

```javascript
ws.onerror = (error) => {
  console.error("WebSocket Hatası:", error);
  console.log("Lütfen Sümen uygulamasının çalışıyor olduğundan emin olunuz");
};
```

### Timeout

İstek uzun süre cevap vermiyor:

```javascript
function sendCommandWithTimeout(ws, message, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      reject(new Error("İstek zaman aşımına uğradı"));
    }, timeout);
    
    ws.send(JSON.stringify(message));
  });
}
```

---

## Entegrasyon Kontrol Listesi

- [ ] Sümen uygulaması masaüstünde kurulu ve çalışıyor
- [ ] WebSocket bağlantısı `ws://localhost:5134/ws` erişilebilir
- [ ] Ping komutu başarılı şekilde cevap alıyor
- [ ] Devices komutu sertifikaları listeliyor
- [ ] requestId her istek için benzersiz
- [ ] Hata yönetimi implement edilmiş
- [ ] Timeout mekanizması tanımlanmış
- [ ] Bağlantı kesintisi durumunda yeniden bağlanma mekanizması var

---

## İlgili Kaynaklar

- [E-İmza ile Login API](esign.md)
- [Süreç Yönetimi API](progress.md)
- [Signer API](signers.md)
