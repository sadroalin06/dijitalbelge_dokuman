---
description: DijitalBelge kimlik doğrulama akışı — belge imzalatmadan, üyelerinizin kimliğini TC kimlik kartı NFC, SMS ve konumla doğrulayın.
---

# Kimlik Doğrulama

Belge imzalatmadan, bir kişinin **gerçekten iddia ettiği kişi olduğunu** doğrularsınız.
Kişi TC kimlik kartını telefonuna okutur, SMS kodunu girer ve konum verir; sonuç
mühürlü bir kanıt dosyası olarak saklanır ve size webhook ile bildirilir.

**Kullanım örnekleri:** üyelik / hesap açılışında KYC, yüksek tutarlı işlem öncesi teyit,
satıcı hesabı başvurusu, araç ya da konut kiralama, yaş doğrulama.

![Kimlik doğrulama akışı](../assets/akislar/kimlik-dogrulama.svg)

!!! warning "Belge yüklenmez"
    Süreç tipi `DIJITAL_KIMLIK_DOGRULAMA` olduğunda hiçbir dosya yüklenmez. Kişiyi sürece
    bağladığınız çağrı (3. adım) gerekli iç belgeyi kendisi oluşturur.

## Doğrulama seviyeleri

| Kod | Kişinin yaptığı | Ne zaman |
|---|---|---|
| `TCKK_TIMESTAMP` | Kimlik kartı NFC + SMS + konum | Çoğu üyelik ve e-ticaret senaryosu |
| `TCKK_FACE_TIMESTAMP` | Yukarıdakiler + yüz eşleştirme | Kimlik kartının sahibinin kendisi olduğundan emin olunması gerektiğinde |
| `TCKK_ONBOARDING` | Yukarıdakiler + kimlik fotoğrafı ve video | Finans, kripto gibi en yüksek güvence gereken alanlar |

## Adımlar

| # | Ne yapılır | API | Ayrıntı |
|---|---|---|---|
| 1 | Süreç oluşturulur: `processType: DIJITAL_KIMLIK_DOGRULAMA` | `POST /process-instances` | [Süreç API](../progress.md) |
| 2 | Dönen `processId`, kendi sisteminizde üyeyle eşleştirilir | — | |
| 3 | Üye sürece bağlanır ve doğrulama seviyesi seçilir | `POST …/signers/all-documents` | [İmzacı API](../signers.md) |
| 4 | Süreç başlatılır | `PUT …/status/start` | [Süreç API](../progress.md) |
| 5 | DijitalBelge üyeye doğrulama bağlantısı gönderir (SMS / e-posta / QR) | — | |
| 6 | Üye mobil uygulamada kimlik kartını okutur, SMS kodunu girer, konum verir | — | |
| 7 | Webhook gelir | `DOCUMENT_SIGNED` | [Webhook](../webhook.md) |
| 8 | Üye hesabınızda "kimliği doğrulandı" olarak işaretlenir; isteğe bağlı olarak kanıt indirilir | `GET …/document/{documentId}/files` | [Döküman API](../documents.md) |

!!! tip "Kimlik kartı çipi nasıl doğrulanır?"
    Kartın çipi iki yolla doğrulanır: çipteki verinin devletçe imzalandığı (Passive
    Authentication) ve çipin kopya olmadığı (Active Authentication). İki doğrulamanın
    sonucu da kanıt dosyasına yazılır.

## Örnek

Uçtan uca istek ve yanıtlarıyla: [Üyelik Kimlik Doğrulama](../examples/uyelik-kimlik-dogrulama.md).
