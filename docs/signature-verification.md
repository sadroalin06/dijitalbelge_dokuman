# İmza Formatları ve Doğrulama

Dosya imzalama sisteminde süreç tipine göre farklı imza formatları kullanılır. Bu bölüm
her formatın ne olduğunu, ne zaman üretildiğini ve nasıl doğrulanacağını açıklar.

---

!!! info "İmzalama Sistemi Hakkında"
    Üretilen çıktının ne olacağı (imzalı PDF, container, onay dosyası, yalnızca kimlik kanıtı vb.)
    iki şeye göre belirlenir: sürecin **süreç tipi** (`processType`) ve süreçteki imzacılara
    atanan **imzalama türü** (`signatureType`).

    | Süreç Tipi | Ne yapar | Kullanılabilen imzalama türleri | Sonuç |
    |---|---|---|---|
    | **BELGE_IMZALAMA** *(varsayılan)* | Tek bir PDF, imzacılar tarafından sırayla imzalanır | Tümü (`EIMZA`, `MOBILE_IMZA`, `TCKK_*`, `SMSOTP_TIMESTAMP`, `EMAIL_TIMESTAMP`) | aşağıya bakın |
    | **DIJITAL_ONAY** | Bir işlem/metin kullanıcıya onaylatılır — belge imzalanmaz, metin onaylanır | OTP/e-posta/TCKK tabanlı onay yöntemleri | Onay dosyası üretilir ve onaylanan metne bağlanır |
    | **DOSYA_IMZALAMA** | Birden fazla dosya **tek bir container** altında toplanıp tek imza ile imzalanır | Yalnızca `EIMZA`, `MOBILE_IMZA` (PKI tabanlı) | ETSI TS 102 918 uyumlu `.asice` container |
    | **DIJITAL_KIMLIK_DOGRULAMA** | Süreçte imzalama/onaylama yapılmaz — yalnızca imzacı bilgisi (TCKK NFC + yüz/video) doğrulanır | TCKK tabanlı kimlik doğrulama akışları (`TCKK_ONBOARDING` vb.) | Doğrulama kanıtı (evidence) üretilir; gerçek bir imza/onay dosyası oluşmaz |

    Detaylı `processType` alan açıklamaları için bkz. [Süreç API – Süreç Tipleri](progress.md#süreç-tipleri-processtype).

    **BELGE_IMZALAMA içinde**, imzacıya atanan `signatureType`'a göre PDF iki farklı şekilde işlenir:

    - **PKI tabanlı (`EIMZA`, `MOBILE_IMZA`):** PDF doğrudan **PAdES** formatında imzalanır — imza PDF'in içine gömülür, **zaman damgalı** ve **arşiv (LTV) özellikli**dir. Ayrı bir kanıt dosyası oluşmaz; PDF'in kendisi zaten imzalı halidir.
    - **Kimlik/OTP tabanlı (`TCKK_TIMESTAMP`, `TCKK_FACE_TIMESTAMP`, `TCKK_ONBOARDING`, `SMSOTP_TIMESTAMP`, `EMAIL_TIMESTAMP`):** Bu yöntemler nitelikli elektronik imza sertifikası kullanmaz. PDF yalnızca **zaman damgası** ile mühürlenir; kimlik doğrulama sürecinin kanıtı ise ayrı bir **JAdES** dosyası olarak (`EVIDENCE` tipinde) saklanır.

---

## Formatlar

| Format | Uzantı | Ne zaman üretilir | Açıklama |
|---|---|---|---|
| **PAdES** | `.pdf` | BELGE_IMZALAMA, tek PDF'in E-İmza/Mobil İmza ile imzalanması | İmza, PDF dosyasının içine gömülür (embedded). Dosyanın kendisi zaten imzalı halidir, ayrı bir imza dosyası yoktur. |
| **CAdES** | `.p7s` | PDF olmayan tek bir dosyanın (docx, xml vb.) imzalanması | Ayrık (detached) imza — orijinal dosya değişmez, imza `.p7s` olarak ayrı kaydedilir. Doğrulamak için hem orijinal dosya hem `.p7s` gerekir. |
| **ASiC-E** | `.asice` | **DOSYA_IMZALAMA** — bir imzacının süreçteki tüm dosyaları tek seferde imzalaması | ETSI TS 102 918 uyumlu ZIP container. İçinde: orijinal dosyalar + `process-metadata.json` + `ASiCManifest.xml` (her dosyanın SHA-256'sı) + `META-INF/signature001.p7s` (manifest'in CAdES imzası). Kendi kendine yeten kanıt paketi — dış bir doğrulayıcı (EU DSS, TÜBİTAK İmzager) sadece bu tek dosyayla hem dosya bütünlüğünü hem imzayı doğrulayabilir. |
| **JAdES** | `.jades` | OTP/SMS/Email doğrulama, TCKK NFC kanıtları | Gerçek bir belge imzası değil — kimlik doğrulama **kanıtını** (evidence) mühürler. Task'ın `signatureStoredFile`'ına değil, ayrı `EVIDENCE` tipinde kaydedilir. |

**Önemli:** DOSYA_IMZALAMA sürecinde her imzacı **kendi ayrı `.asice`'ını** üretir — 3 imzacı
varsa 3 ayrı `.asice` dosyası oluşur, aynı içerik (belgeler) her birine ayrı ayrı paketlenip
imzalanır. Tek bir container'da birden fazla imzacının imzası birleştirilmez.

**DOSYA_IMZALAMA yalnızca E-İmza ve Mobil İmza ile çalışır** — OTP/NFC gibi PKI tabanlı
olmayan yöntemler bu süreç tipinde reddedilir, çünkü ASiC-E manifest imzası gerçek bir
sertifika + ham imza gerektirir.

!!! info "ASiC-E = Container Bazlı İmzalama"
    DOSYA_IMZALAMA sürecinde tekil dosyalar ayrı ayrı değil, **tek bir container altında
    toplanıp** birlikte imzalanır. Üretilen `.asice` dosyası aslında bir **ZIP arşividir**
    — uzantısını `.zip` olarak değiştirdiğinizde içeriğini (orijinal dosyalar,
    `process-metadata.json`, `ASiCManifest.xml`, `META-INF/signature001.p7s`) doğrudan
    görüntüleyebilirsiniz. Bütünlüğünü ve imzasını doğrulamak için ise dosyayı değiştirmeden
    Dijital Belge'nin doğrulama uç noktalarını (bkz. [Doğrulama Endpoint'leri](#doğrulama-endpointleri))
    kullanmanız gerekir.

---

## Doğrulama Endpoint'leri

| Endpoint | Yetki | Kapsam |
|---|---|---|
| `POST /files/verify` | Yok (herkese açık) | Herhangi bir yüklenen dosyayı (PDF/`.asice`) tür otomatik algılayarak doğrular |
| `GET /external/process-instances/{processId}/document/{documentId}/tasks/{taskId}/signature/verify` | API-key, `document:read` | Task bazlı doğrulama |
| `GET /external/process-instances/{processId}/signers/{signerId}/signature/verify` | API-key, `document:read` | İmzacı bazlı doğrulama (documentId/taskId bilmeye gerek yok) |

Tüm doğrulama uç noktaları aynı yanıt şemasını (`DocumentVerificationResultDto`) kullanır —
`detectedType` (`PDF`/`ASICE`), `valid`, `message`, ve türe göre `pdfSignatures[]` ya da
`asice{ signatures[], files[], allFilesMatch }`.

| Alan | Tip | Açıklama |
|------|-----|----------|
| `detectedType` | string | Algılanan dosya türü: `PDF` veya `ASICE` |
| `valid` | boolean | İmza(lar) geçerli mi |
| `message` | string | Doğrulama sonucunu özetleyen mesaj |
| `pdfSignatures` | array | `detectedType: PDF` iken doldurulur — PDF içindeki imza(lar)ın listesi |
| `asice` | object | `detectedType: ASICE` iken doldurulur — `signatures[]`, `files[]`, `allFilesMatch` alanlarını içerir |

### Task Bazlı Doğrulama

Belirli bir imzalama görevinin (task) imza dosyasını doğrular. `taskId`, dökümana imzacı eklerken dönen `id` alanıyla aynıdır.

**Scope:** `document:read`

#### İstek

```http
GET {baseURL}/process-instances/{processId}/document/{documentId}/tasks/{taskId}/signature/verify
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `documentId` | number | Dökümanın ID'si |
| `taskId` | number | İmzalama görevinin (imzacının) ID'si |

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147/document/7203/tasks/5/signature/verify \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```

### İmzacı Bazlı Doğrulama

Task veya döküman ID'sini bilmeye gerek kalmadan, doğrudan imzacı ID'si üzerinden imza doğrulaması yapar.

**Scope:** `document:read`

#### İstek

```http
GET {baseURL}/process-instances/{processId}/signers/{signerId}/signature/verify
```

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `processId` | number | Sürecin ID'si |
| `signerId` | number | İmzacının ID'si |

#### Örnek cURL

```bash
curl -X GET https://app.dijitalbelge.com/api/external/process-instances/147/signers/138/signature/verify \
  -H "X-Client-Id: app_xxxxx" \
  -H "X-Client-Secret: secret_xxxxx"
```
