# Scopes & Paket Bazlı Yetkilendirme

Bu doküman, platformda kullanılan **yetkilerin (scopes)** hangi **paket (versiyon)** kapsamında kullanılabildiğini açıklar.  
Bazı yetkiler yalnızca belirli paketlerde aktiftir. İlgili scope’u kullanabilmek için hesabın uygun versiyona yükseltilmesi gerekir.

---

## Paketler

| Paket | Açıklama |
|------|---------|
| **Starter** | Temel kullanım. API ve entegrasyon yoktur. |
| **Plus** | Basit API entegrasyonları ve hazır süreçlerin kullanımı. |
| **Pro** | Gelişmiş süreç yönetimi, belge erişimi ve event tabanlı entegrasyonlar. |
| **Enterprise** | Uygulama içinden bağımsız imza akışı, Sumen entegrasyonu ve tam entegrasyon yetenekleri. |

---

## Scope Tanımları

### 📄 Document Scopes

| Scope | Açıklama | Minimum Paket |
|------|---------|---------------|
| `document:read` | İmzalı / imzasız belge içeriğini okuma | **Pro** |
| `document:upload` | Sürece belge yükleme | **Plus** |
| `document:sign` | Belge imzalama işlemi başlatma | **Plus** |

---

### 👤 Signer (İmzacı) Scopes

| Scope | Açıklama | Minimum Paket |
|------|---------|---------------|
| `signer:read` | Tanımlı imzacıları listeleme | **Plus** |
| `signer:management` | İmzacı oluşturma / güncelleme | **Plus** |

> ℹ️ Starter paket kullanıcıları imzacı yönetimi ve API erişimi yapamaz.

---

### 🔄 Process (Süreç) Scopes

| Scope | Açıklama | Minimum Paket |
|------|---------|---------------|
| `process:start` | Tanımlı süreç başlatma | **Plus** |
| `process:status` | Süreç durumunu görüntüleme | **Plus** |
| `process:create` | Yeni süreç oluşturma | **Pro** |
| `process:document:add` | Sürece taslaktan veya manuel belge ekleme | **Pro** |
| `process:event:subscribe` | Süreç durum değişiklikleri için event alma | **Pro** |

---

### 🔔 Event & Webhook Scopes

| Scope | Açıklama | Minimum Paket |
|------|---------|---------------|
| `event:read` | Süreç durum event’lerini alma | **Pro** |
| `webhook:manage` | Webhook tanımlama ve yönetme | **Pro** |

---

### ✍️ Embedded / Advanced Signing Scopes

| Scope | Açıklama | Minimum Paket |
|------|---------|---------------|
| `embedded:signing` | Uygulama içinde (iframe / custom UI) imzalama | **Enterprise** |
| `sumen:integration` | Sumen Desktop uygulaması ile entegre imzalama | **Enterprise** |
| `signing:full-control` | İmza akışını tamamen harici uygulama içinde yönetme | **Enterprise** |

---

## Paket Bazlı Özet Yetkinlikler

### Starter
- ❌ API erişimi yok
- ❌ Entegrasyon yok
- ❌ İmzacı ve süreç yönetimi yok

---

### Plus
- ✅ Basit API erişimi
- ✅ İmzacı yönetimi
- ✅ Tanımlı süreçlere belge yükleme
- ✅ Süreç başlatma
- ❌ Süreç oluşturma
- ❌ Event / webhook

---

### Pro
- ✅ Tüm Plus özellikleri
- ✅ Süreç oluşturma
- ✅ Taslaktan veya manuel belge ekleme
- ✅ İmzalı belge içeriğine erişim
- ✅ Süreç event’leri (status change)
- ✅ Webhook entegrasyonu

---

### Enterprise
- ✅ Tüm Pro özellikleri
- ✅ Uygulama içinden imzalama (embedded signing)
- ✅ Sumen uygulama entegrasyonu
- ✅ İmza akışını bağımsız uygulama içinde yönetme
- ✅ Gelişmiş entegrasyon senaryoları

---

## Versiyon Yükseltme Notu

Bir API anahtarı veya entegrasyon uygulaması, yalnızca hesabın paketine tanımlı scope’ları kullanabilir.  
Yetersiz paket ile yapılan çağrılar **403 – Insufficient Plan** hatası döner.
