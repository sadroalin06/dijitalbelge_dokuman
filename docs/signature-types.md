# İmzalama Türleri ve Kullanım Senaryoları

Bu sayfa, Dijital Belge platformunda kullanılabilen imzalama türlerini ve bu türlerin karşılıklı imzalama senaryolarında nasıl bir arada kullanıldığını açıklamaktadır.

---

## İmzalama Türleri

Her imzalama türü, kimlik doğrulama güvencesi ve kullanıcı deneyimi açısından farklı bir seviyeye karşılık gelir.

| Kod | Ad | Kimlik Doğrulama Yöntemi | Güvence Seviyesi |
|-----|----|--------------------------|-----------------|
| `EMAIL_TIMESTAMP` | E-Posta ile Dijital Onay | E-posta onayı + zaman damgası | Düşük |
| `SMSOTP_TIMESTAMP` | SMSOTP ile Doğrulama | SMS OTP + zaman damgası | Orta |
| `TCKK_TIMESTAMP` | Kimlik(TCKK) ile Dijital Onay | Kimlik Kartı NFC + SMS doğrulama + Konum + zaman damgası | Yüksek |
| `TCKK_FACE_TIMESTAMP` | TCKK ve Yüz Tanıma Dijital İmza | Kimlik Kartı NFC + Yüz tanıma + SMS doğrulama + Konum | Çok Yüksek |
| `TCKK_ONBOARDING` | TCKK+Yüz Tanıma Videolu Dijital İmza | Kimlik Kartı NFC + Kimlik Kartı + Fotoğraf + Video + SMS doğrulama + Konum | Çok Yüksek+ |
| `EIMZA` | Elektronik İmza | Nitelikli elektronik imza sertifikası | En Yüksek |
| `MOBILE_IMZA` | Mobil İmza | Mobil operatör nitelikli elektronik imza (Turkcell, Vodafone, Türk Telekom) | En Yüksek |

---

## Karşılıklı İmzalama Senaryoları

Bir belgede birden fazla imzacı olduğunda her imzacıya farklı bir imzalama türü atanabilir. Aşağıdaki senaryolar tipik kullanım akışlarını göstermektedir.

---

### Senaryo 1 — Dijital Abonelik Sözleşmesi

**Kullanım Alanı:** Müşteri ile servis sağlayıcı arasındaki abonelik veya üyelik sözleşmeleri.

Müşteri taraf en güçlü kimlik doğrulama yöntemi olan `TCKK_ONBOARDING` ile geçer — kimlik kartı NFC okuma, selfie fotoğraf ve kısa video kaydı içerir. Servis sağlayıcı kurumsal taraf olarak standart `EIMZA` ile imzalar.

```
Müşteri (1. İmzacı)                    Servis Sağlayıcı (2. İmzacı)
─────────────────────────────           ──────────────────────────────
TCKK_ONBOARDING                         EIMZA
  │                                       │
  ├─ Kimlik Kartı NFC okuma              ├─ Nitelikli elektronik imza sertifikası
  ├─ Kimlik Kartı (fiziksel tarama)      └─ Elektronik imza
  ├─ Selfie fotoğraf çekimi
  ├─ Kısa video kaydı
  ├─ SMS doğrulama
  └─ Konum + zaman damgası
```

**İmzacı Konfigürasyonu:**

```json
"signers": [
  {
    "order": 1,
    "name": "Müşteri Adı Soyadı",
    "email": "musteri@example.com",
    "signatureTypeCode": "TCKK_ONBOARDING"
  },
  {
    "order": 2,
    "name": "Servis Sağlayıcı Yetkilisi",
    "email": "yetkili@sirket.com",
    "signatureTypeCode": "EIMZA"
  }
]
```

!!! info "Akış Sırası"
    `order` alanı imza sırasını belirler. Müşteri (`order: 1`) önce imzalar; onboarding tamamlandıktan sonra servis sağlayıcı yetkilisine (`order: 2`) imza bildirimi iletilir.

---

### Senaryo 2 — Yüz Tanımalı Kimlik Doğrulama ile Sözleşme

**Kullanım Alanı:** Banka, sigorta veya finans sektöründe kimlik teyidi gerektiren sözleşmeler.

Müşteri taraf `TCKK_FACE_TIMESTAMP` ile doğrulanır — kimlik kartı NFC okumasına ek olarak anlık yüz tanıma biyometrik eşleşmesi yapılır. Kurumsal taraf `EIMZA` ile imzalar.

```
Müşteri (1. İmzacı)                    Kurum Yetkilisi (2. İmzacı)
─────────────────────────────           ──────────────────────────────
TCKK_FACE_TIMESTAMP                     EIMZA
  │                                       │
  ├─ Kimlik Kartı NFC okuma              ├─ Nitelikli elektronik imza sertifikası
  ├─ Gerçek zamanlı yüz tanıma          └─ Elektronik imza
  ├─ SMS doğrulama
  └─ Konum + zaman damgası
```

**İmzacı Konfigürasyonu:**

```json
"signers": [
  {
    "order": 1,
    "name": "Müşteri Adı Soyadı",
    "email": "musteri@example.com",
    "signatureTypeCode": "TCKK_FACE_TIMESTAMP"
  },
  {
    "order": 2,
    "name": "Kurum Yetkilisi",
    "email": "yetkili@kurum.com",
    "signatureTypeCode": "EIMZA"
  }
]
```

!!! tip "TCKK_ONBOARDING ile Farkı"
    `TCKK_FACE_TIMESTAMP` video kaydı içermez; anlık yüz biyometrisi ve NFC okuma ile kimlik doğrular.
    `TCKK_ONBOARDING` ise fotoğraf ve video kaydı ile daha kapsamlı uzaktan onboarding sürecini kapsar.

---

### Senaryo 3 — NFC Kimlik Doğrulama ile Sözleşme

**Kullanım Alanı:** Yüz tanımaya gerek duyulmayan ancak fiziksel kimlik kartı doğrulaması istenen akışlar.

Müşteri taraf yalnızca `TCKK_TIMESTAMP` ile kimlik kartını NFC okutarak doğrulama yapar ve zaman damgası oluşturur. Kurumsal taraf `EIMZA` ile imzalar.

```
Müşteri (1. İmzacı)                    Kurum Yetkilisi (2. İmzacı)
─────────────────────────────           ──────────────────────────────
TCKK_TIMESTAMP                          EIMZA
  │                                       │
  ├─ Kimlik Kartı NFC okuma              ├─ Nitelikli elektronik imza sertifikası
  ├─ SMS doğrulama                       └─ Elektronik imza
  └─ Konum + zaman damgası
```

**İmzacı Konfigürasyonu:**

```json
"signers": [
  {
    "order": 1,
    "name": "Müşteri Adı Soyadı",
    "email": "musteri@example.com",
    "signatureTypeCode": "TCKK_TIMESTAMP"
  },
  {
    "order": 2,
    "name": "Kurum Yetkilisi",
    "email": "yetkili@kurum.com",
    "signatureTypeCode": "EIMZA"
  }
]
```

---

## Senaryo Karşılaştırması

| Senaryo | Müşteri Tarafı | Kurumsal Taraf | Kimlik Güvencesi | Fotoğraf | Video |
|---------|---------------|---------------|-----------------|----------|-------|
| Dijital Abonelik | `TCKK_ONBOARDING` | `EIMZA` | Çok Yüksek | Evet | Evet |
| Yüz Tanımalı Sözleşme | `TCKK_FACE_TIMESTAMP` | `EIMZA` | Yüksek | Anlık Yüz | Hayır |
| NFC Kimlik Doğrulama | `TCKK_TIMESTAMP` | `EIMZA` | Yüksek | Hayır | Hayır |
