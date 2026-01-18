# Gmail API Hızlı Kurulum (OAuth 2.0)

Render.com'da SMTP portları bloke olduğu için Gmail API kullanıyoruz.

## Adım 1: OAuth 2.0 Credentials Oluşturma

1. Google Cloud Console'da projenize gidin: https://console.cloud.google.com/
2. Sol menüden **"APIs & Services"** → **"Credentials"** seçin
3. **"Create Credentials"** → **"OAuth client ID"** seçin

4. **Eğer "Configure consent screen" ekranı çıkarsa:**
   - **User Type:** "External" seçin → "Create"
   - **App name:** "Ön Muhasebe" yazın
   - **User support email:** Kendi email'inizi seçin
   - **Developer contact:** Kendi email'inizi girin
   - **"Save and Continue"** tıklayın
   - **Scopes:** "Add or Remove Scopes" → **"https://www.googleapis.com/auth/gmail.send"** ekleyin → "Update" → "Save and Continue"
   - **Test users:** Kendi Gmail adresinizi ekleyin → "Save and Continue"
   - **"Back to Dashboard"** tıklayın
   - Tekrar **"Create Credentials"** → **"OAuth client ID"** seçin

5. **Application type seçme ekranı:**
   - **Application type:** **"Desktop app"** seçin
   - **Name:** "Ön Muhasebe Desktop" yazın (veya istediğiniz bir isim)
   - **"Create"** tıklayın

6. **OAuth client oluşturuldu ekranı:**
   - **"Download JSON"** butonuna tıklayın
   - İndirilen dosyayı `credentials.json` olarak proje klasörüne kaydedin

## Adım 2: Token Oluşturma (Yerel Bilgisayarınızda)

1. İndirdiğiniz `credentials.json` dosyasını proje klasörüne kopyalayın

2. `setup_gmail_token.py` dosyası oluşturun:
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   import json
   
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
   
   print("\n" + "="*60)
   print("AŞAĞIDAKI JSON'U KOPYALAYIN VE RENDER.COM'A EKLEYIN:")
   print("="*60)
   print(json.dumps(token_data))
   print("="*60)
   ```

3. Script'i çalıştırın:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   python setup_gmail_token.py
   ```

4. Tarayıcı açılacak, Gmail hesabınızla giriş yapın ve **"Allow"** tıklayın

5. Terminal'de çıkan JSON'u kopyalayın

## Adım 3: Render.com'a Environment Variable Ekleme

1. Render.com dashboard'a gidin
2. Servisinizin **"Environment"** sekmesine gidin
3. **"Add Environment Variable"** tıklayın
4. Şu değişkenleri ekleyin:

   - **Key:** `GMAIL_TOKEN_JSON`
   - **Value:** Adım 2'de kopyaladığınız JSON'u yapıştırın (tek satır olmalı)

   - **Key:** `EMAIL_FROM`
   - **Value:** Gönderen Gmail adresiniz (örn: your_email@gmail.com)

   - **Key:** `EMAIL_TO`
   - **Value:** Alıcı e-posta adresi (örn: recipient@example.com)

5. **"Save Changes"** tıklayın

6. Servis otomatik olarak yeniden deploy edilecek

## Test

Render.com'da servis deploy edildikten sonra, iş evrakı oluşturup "Kaydet ve Gönder" butonuna tıklayın. Email başarıyla gönderilmelidir.

## Sorun Giderme

**"Error 403: access_denied" veya "Access blocked" hatası:**

Bu hata OAuth consent screen'in test modunda olması ve test kullanıcı listesine email'inizin eklenmemesinden kaynaklanır.

**Çözüm:**

1. Google Cloud Console'a gidin: https://console.cloud.google.com/
2. Sol menüden **"APIs & Services"** → **"OAuth consent screen"** seçin
3. **"Test users"** sekmesine gidin (veya aşağı kaydırın)
4. **"+ ADD USERS"** butonuna tıklayın
5. **Kendi Gmail adresinizi** ekleyin (token oluştururken kullanacağınız email)
6. **"ADD"** tıklayın
7. Tekrar `python setup_gmail_token.py` çalıştırın

**Not:** Eğer hala çalışmazsa:
- Consent screen'de **"Scopes"** sekmesine gidin
- `https://www.googleapis.com/auth/gmail.send` scope'unun eklendiğinden emin olun
- Eğer yoksa, "Add or Remove Scopes" → "gmail.send" ekleyin → "Update" → "Save and Continue"

**"Invalid credentials" hatası:**
- `GMAIL_TOKEN_JSON` formatını kontrol edin (JSON string olmalı, tek satır)
- Tırnak işaretlerini escape etmeyi unutmayın

**Token expire oldu:**
- Refresh token varsa otomatik yenilenir
- Yenilenmezse, Adım 2'yi tekrarlayın
