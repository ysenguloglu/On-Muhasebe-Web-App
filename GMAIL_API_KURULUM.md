# Gmail API Kurulum Rehberi

Render.com'da SMTP portları (25, 465, 587) bloke olduğu için Gmail API kullanıyoruz. Gmail API HTTP/HTTPS üzerinden çalışır ve port kısıtlamalarından etkilenmez.

## Adım 1: Google Cloud Console'da Proje Oluşturma

1. https://console.cloud.google.com/ adresine gidin
2. Yeni proje oluşturun veya mevcut projeyi seçin
3. Proje adı: "Ön Muhasebe" (veya istediğiniz bir isim)

## Adım 2: Gmail API'yi Etkinleştirme

1. Sol menüden "APIs & Services" → "Library" seçin
2. "Gmail API" arayın
3. "Gmail API" seçin ve "Enable" butonuna tıklayın

## Adım 3: OAuth 2.0 Credentials Oluşturma

1. Sol menüden "APIs & Services" → "Credentials" seçin
2. "Create Credentials" → "OAuth client ID" seçin
3. İlk kez ise "Configure consent screen" yapın:
   - User Type: "External" seçin
   - App name: "Ön Muhasebe" (veya istediğiniz isim)
   - User support email: Kendi email'inizi seçin
   - Developer contact: Kendi email'inizi girin
   - "Save and Continue" tıklayın
   - Scopes: "Add or Remove Scopes" → "https://www.googleapis.com/auth/gmail.send" ekleyin
   - "Save and Continue" tıklayın
   - Test users: Kendi Gmail adresinizi ekleyin
   - "Save and Continue" tıklayın

4. OAuth client ID oluşturun:
   - Application type: "Desktop app" seçin
   - Name: "Ön Muhasebe Desktop" (veya istediğiniz isim)
   - "Create" tıklayın

5. İndirilen JSON dosyasını açın ve içeriğini kopyalayın

## Adım 4: İlk Kurulum (Yerel Geliştirme)

Yerel bilgisayarınızda token oluşturmak için:

1. İndirdiğiniz JSON dosyasını `credentials.json` olarak proje klasörüne kaydedin

2. Python script oluşturun (`setup_gmail_token.py`):
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   import json
   import os
   
   SCOPES = ['https://www.googleapis.com/auth/gmail.send']
   
   # credentials.json dosyasını oku
   flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
   creds = flow.run_local_server(port=0)
   
   # Token'ı JSON formatına çevir
   token_data = {
       'token': creds.token,
       'refresh_token': creds.refresh_token,
       'token_uri': creds.token_uri,
       'client_id': creds.client_id,
       'client_secret': creds.client_secret,
       'scopes': creds.scopes
   }
   
   print("\n" + "="*50)
   print("GMAIL_TOKEN_JSON için aşağıdaki değeri kopyalayın:")
   print("="*50)
   print(json.dumps(token_data))
   print("="*50)
   ```

3. Script'i çalıştırın:
   ```bash
   python setup_gmail_token.py
   ```

4. Tarayıcı açılacak, Gmail hesabınızla giriş yapın ve izin verin

5. Terminal'de çıkan JSON'u kopyalayın

## Adım 5: Environment Variables Ayarlama

### Yerel Geliştirme (.env dosyası):

```env
# Gmail API Token (Adım 4'te oluşturduğunuz JSON)
GMAIL_TOKEN_JSON={"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"...","scopes":["https://www.googleapis.com/auth/gmail.send"]}

# E-posta Adresleri
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
```

### Render.com Deployment:

Render.com dashboard'dan environment variable'ları ekleyin:

1. **GMAIL_TOKEN_JSON**: Adım 4'te oluşturduğunuz JSON'u ekleyin
2. **EMAIL_FROM**: Gönderen e-posta adresi
3. **EMAIL_TO**: Alıcı e-posta adresi

## Önemli Notlar

- **Refresh Token**: Token süresi dolduğunda otomatik olarak yenilenir
- **Güvenlik**: `GMAIL_TOKEN_JSON` içinde `refresh_token` bulunur, bu token'ı güvenli tutun
- **Test Users**: Gmail API test modunda sadece test users listesindeki email'lerden gönderim yapılabilir
- **Production**: Production'a geçmek için OAuth consent screen'i "Publish" etmeniz gerekir

## Sorun Giderme

**"Access blocked" hatası:**
- OAuth consent screen'i "Publish" etmeniz gerekebilir
- Test users listesine email'inizi eklediğinizden emin olun

**"Invalid credentials" hatası:**
- `GMAIL_TOKEN_JSON` formatını kontrol edin (JSON string olmalı)
- Token'ın expire olmadığından emin olun (refresh token varsa otomatik yenilenir)

**"Insufficient permissions" hatası:**
- Gmail API scope'unun (`gmail.send`) doğru olduğundan emin olun
