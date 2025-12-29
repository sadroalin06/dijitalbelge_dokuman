# 🔐 Kimlik Doğrulama (Authentication)

DijitalBelge External API’ye yapılan tüm istekler **entegrasyon bazlı kimlik doğrulama**
ile korunmaktadır. Bu doğrulama, uygulamanıza özel olarak üretilen
`ClientId` ve `ClientSecret` bilgileri üzerinden gerçekleştirilir.

---

## 🧩 Entegrasyon Uygulaması Oluşturma

API’yi kullanabilmek için öncelikle DijitalBelge platformu üzerinde
bir **entegrasyon uygulaması** oluşturmanız gerekmektedir.

### Uygulama oluşturma adımları:

1. DijitalBelge uygulamasına giriş yapın
2. **Ayarlar** menüsüne gidin
3. **API Entegrasyonu** bölümünü açın
4. **Yeni Uygulama Oluştur** seçeneği ile entegrasyon uygulamanızı kaydedin

Uygulama oluşturulduktan sonra sistem tarafından size özel olarak:

- **ClientId**
- **ClientSecret**

değerleri üretilir.

!!! warning
    ClientSecret bilgisi **yalnızca bir kez görüntülenir** ve gizli tutulmalıdır.
    Bu bilgi paylaşılmamalı ve herkese açık ortamlarda saklanmamalıdır.

---

## 🔑 ClientId ve ClientSecret Kullanımı

Oluşturulan `ClientId` ve `ClientSecret` bilgileri,
DijitalBelge External API’ye yapılan **tüm HTTP isteklerinde**
header olarak gönderilmelidir.

### Zorunlu HTTP Header’lar

```http
X-Client-Id: your-client-id
X-Client-Secret: your-client-secret

```
## 📦 Örnek API İstekleri

=== "cURL"

    ```    
    curl -X GET "https://api.dijitalbelge.com/api/external/signers/search" \
      -H "X-Client-Id: app_xxxxx" \
      -H "X-Client-Secret: secret_xxxxx"
    ```

=== "Java"

    ``` 
    HttpHeaders headers = new HttpHeaders();
    headers.set("X-Client-Id", "app_xxxxx");
    headers.set("X-Client-Secret", "secret_xxxxx");
    ```

=== "JavaScript"

    ``` 
    fetch("https://api.dijitalbelge.com/api/external/signers/search", {
      headers: {
        "X-Client-Id": "app_xxxxx",
        "X-Client-Secret": "secret_xxxxx"
      }
    });
    ```

=== "Python"

    ``` 
    import requests

    headers = {
        "X-Client-Id": "app_xxxxx",
        "X-Client-Secret": "secret_xxxxx"
    }

    requests.get(
        "https://api.dijitalbelge.com/api/external/signers/search",
        headers=headers
    )
    ```
