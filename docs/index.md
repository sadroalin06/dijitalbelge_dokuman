---
description: DijitalBelge API dokümantasyonu — e-imza, mobil imza ve elektronik belge imzalama süreçlerini REST API ile kendi yazılımınıza entegre edin.
hide:
  - navigation
  - toc
---

<div class="db-hero" markdown>

# DijitalBelge API Dokümantasyonu

Belge imzalama, dijital onay, kimlik doğrulama ve imza doğrulama süreçlerini REST API ile
kendi yazılımınıza entegre edin. E-imza, mobil imza ve kimlik kartı (TCKK) ile çalışır.

[Hangi akış bana uygun?](akislar/index.md){ .md-button .md-button--primary }
[API erişimi al](authentication.md){ .md-button }

</div>

## Entegrasyon akışları

<div class="grid cards" markdown>

-   :material-file-sign:{ .lg .middle } __Belge İmzalama__

    ---

    Sözleşme ve belgeleri ıslak imza yerine geçen nitelikli elektronik imzayla
    imzalatın: merkezi imza ekranından ya da kendi uygulamanızın içinden.

    [:octicons-arrow-right-24: Akışı incele](akislar/belge-imzalama.md)

-   :material-check-decagram-outline:{ .lg .middle } __Dijital Onay__

    ---

    Belgeleri e-posta, SMS, kimlik kartı, e-imza ya da mobil imzayla onaylatın;
    kanıtlar zaman damgasıyla mühürlensin.

    [:octicons-arrow-right-24: Akışı incele](akislar/dijital-onay.md)

-   :material-card-account-details-outline:{ .lg .middle } __Kimlik Doğrulama__

    ---

    Belge olmadan, üyelerinizin kimliğini TC kimlik kartı NFC, SMS ve konumla
    doğrulayın (KYC).

    [:octicons-arrow-right-24: Akışı incele](akislar/kimlik-dogrulama.md)

-   :material-login-variant:{ .lg .middle } __Login__

    ---

    Kullanıcılarınızı sitenize şifre yerine e-imza ya da mobil imzayla,
    doğrulanmış kimlikle giriş yaptırın.

    [:octicons-arrow-right-24: Akışı incele](akislar/login.md)

-   :material-shield-check-outline:{ .lg .middle } __Belge Doğrulama__

    ---

    PAdES, ASiC-E, JAdES, CAdES ve XAdES imzalarını QR kodla, doğrulama sayfasında
    ya da API ile doğrulayın.

    [:octicons-arrow-right-24: Doğrulama yolları](dogrulama/index.md)

-   :material-code-braces:{ .lg .middle } __API Referansı__

    ---

    Süreç, döküman, imzacı, webhook ve Sümen uçlarının tüm istek ve yanıtları.

    [:octicons-arrow-right-24: Süreç API](progress.md)

</div>

## Nasıl başlanır?

1. **Üyelik ve erişim bilgileri:** DijitalBelge platformunda üyelik oluşturun ve bir
   entegrasyon uygulaması tanımlayarak `ClientId` ve `ClientSecret` alın
   ([API Erişimi](authentication.md)).
2. **Yetkiler:** Uygulamanıza ihtiyacınız olan yetkileri (scope) verin ([Yetkiler](scopes.md)).
3. **Akışı seçin:** [Hangi akış?](akislar/index.md) sayfasından size uygun akışı seçin ve adımlarını izleyin.
4. **Deneyin:** [Postman koleksiyonu](postman.md) ile istekleri hızlıca deneyin.

!!! info "İmzaya giden tüm süreç"
    İmza öncesinde veya sırasında gereken ek belgelerin toplanması, doğrulanması ve sürece
    dahil edilmesi de DijitalBelge tarafından desteklenir. Böylece yalnızca imza anını değil,
    **imzaya giden tüm süreci** tek bir yapı üzerinden yönetirsiniz.
