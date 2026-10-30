---
description: DijitalBelge entegrasyon akışları — belge imzalama, dijital onay, kimlik doğrulama ve login. Hangi akışın size uygun olduğunu seçin.
---

# Hangi akış size uygun?

DijitalBelge'yi dört farklı amaçla entegre edebilirsiniz. Her akışın kendi sayfası var:
önce aşağıdaki şemadan size uyanı seçin, sonra o sayfadaki adımları izleyin.

![Hangi entegrasyon akışı?](../assets/akislar/hangi-akis.svg)

| Akış | Ne zaman kullanılır | Sonuç | Sayfa |
|---|---|---|---|
| **Belge İmzalama** | Sözleşme, dilekçe gibi belgelerin **ıslak imza yerine geçen** nitelikli elektronik imzayla imzalanması | İmzalı PDF (PAdES) ya da ayrık imzalı dosya (ASiC-E) | [Belge İmzalama](belge-imzalama.md) |
| **Dijital Onay** | Belgenin imzalanması değil **onaylanması** gerektiğinde; onaylayan e-posta, SMS, kimlik kartı, e-imza ya da mobil imzayla onaylar | Onaylı PDF; e-imza / mobil imza dışındaki yöntemlerde zaman damgalı kanıt dosyası (JAdES) | [Dijital Onay](dijital-onay.md) |
| **Kimlik Doğrulama** | Belge olmadan, bir kişinin **gerçekten iddia ettiği kişi olduğunun** teyidi (üyelik, KYC) | Mühürlü kimlik doğrulama kanıtı | [Kimlik Doğrulama](kimlik-dogrulama.md) |
| **Login** | Kullanıcılarınızın sitenize **e-imza ya da mobil imza ile giriş** yapması | Doğrulanmış kimlikle oturum + audit log | [Login](login.md) |

İmzalanan ya da onaylanan belgelerin sonradan doğrulanması (QR kod, dosya yükleme, API) ayrı bir
bölümde anlatılır: [Belge Doğrulama](../dogrulama/index.md).

!!! tip "Hepsi için ortak ön koşul"
    Tüm akışlarda istekler `X-Client-Id` ve `X-Client-Secret` başlıklarıyla yapılır.
    Bu bilgileri almak için [API Erişimi](../authentication.md) sayfasına bakın.
    Belge imzalama, dijital onay ve kimlik doğrulama akışlarında sonucu anında öğrenmek
    için bir [Webhook](../webhook.md) tanımlamanız önerilir.

## Akışları okuma rehberi

Akış şemalarında üç taraf vardır:

- **Sizin sisteminiz** (lacivert): DijitalBelge API'sini çağıran uygulamanız.
- **DijitalBelge** (sarı): süreci yöneten, bildirimleri gönderen, imzaları doğrulayan platform.
- **İmzacı / kullanıcı** (yeşil): belgeyi imzalayan, onaylayan ya da kimliğini doğrulayan kişi.

Düz oklar sizin yaptığınız API çağrılarıdır; kesikli oklar DijitalBelge'nin gönderdiği
bildirimleri (e-posta, SMS, webhook) gösterir. Her şemadaki numaralar, sayfadaki adım
tablosuyla birebir eşleşir.

## API dışındaki bağlantılar

Sizin sisteminizin DijitalBelge'ye yaptığı **tüm çağrılar** `/api/external` altındadır ve
`X-Client-Id` / `X-Client-Secret` ile yapılır. Aşağıdakiler ise API çağrısı değildir ya da
sizin değil, başka bir bileşenin yaptığı bağlantılardır:

| Bağlantı | Kim kullanır | Ne için |
|---|---|---|
| `ws://localhost:5134/ws` | Uygulamanız (tarayıcıdan) → imzacının bilgisayarındaki Sümen | E-imza: uygulama içi imza (`signDocument`) ve e-imza ile login (`signLogin`). Yerel masaüstü uygulamasıdır, internete açık değildir. |
| `/api/files/document/{token}/hash` · `…/sign/{uid}` | Sümen → DijitalBelge | Sümen'in imzalama sırasında özeti alıp imzayı göndermesi. Sizin çağırmanız gerekmez. |
| `https://app.dijitalbelge.com/sign/{accessToken}` | İmzacı (tarayıcı) | Merkezi imza ekranı (A modeli) ve belgedeki QR'ın açtığı süreç sayfası. Web sayfasıdır. |
| `https://app.dijitalbelge.com/sign/dogrula` · `/api/files/verify` · `/api/public/sign/captcha` | Belgeyi alan herkes (tarayıcı) | Herkese açık doğrulama sayfası; resimli doğrulama kodu ister. API karşılığı [`/external/verify`](../dogrulama/api.md). |
| DijitalBelge mobil uygulaması | İmzacı / onaylayan (telefon) | Kimlik kartı (TCKK) gerektiren dijital onay ve kimlik doğrulama adımları. |
| Webhook | DijitalBelge → sizin sunucunuz | Süreç ve belge olaylarının bildirimi ([Webhook](../webhook.md)). |
