# Ön Muhasebe Web Uygulaması

FastAPI ile geliştirilmiş, web tabanlı ön muhasebe uygulaması. Stok yönetimi, cari hesap yönetimi ve iş evrakı oluşturma özelliklerini içerir. Render.com üzerinde deploy edilebilir.

## Özellikler

- 📦 **Stok Yönetimi**: Ürün ekleme, düzenleme, silme ve listeleme
  - Ürün kodu ile stok takibi
  - Excel'den toplu ürün içe aktarma
  - Excel'e stok verisi dışa aktarma
  - Stok miktarı ve fiyat yönetimi
  - Stok miktarı azaltma (toplu işlem desteği)
- 👥 **Cari Hesap Yönetimi**: Müşteri ve tedarikçi kayıtları
  - TC Kimlik No ve VKN kontrolü ile otomatik cari oluşturma
  - Müşteri/Tedarikçi filtreleme
  - Bakiye takibi
  - Arama ve filtreleme
- 📄 **İş Evrakı Oluşturma**: Servis iş emri oluşturma ve PDF gönderme
  - Detaylı iş evrakı formu
  - Ürün ekleme ve stoktan otomatik düşme
  - PDF oluşturma (tek sayfa, profesyonel tasarım)
  - E-posta ile otomatik gönderme
  - Şirket bilgileri ve belge tarihi/saati otomatik ekleme
- 🌐 **Web Arayüzü**: Modern, responsive web arayüzü
  - Mobil ve masaüstü uyumlu
  - Kolay kullanım
- 🔍 **API Dokümantasyonu**: Swagger UI ve ReDoc desteği
- 💾 **SQLite Veritabanı**: Tüm veriler lokal SQLite veritabanında saklanır

## Gereksinimler

- Python 3.12 veya üzeri
- FastAPI ve bağımlılıkları (requirements.txt'de listelenmiştir)

## Kurulum

### Yerel Geliştirme

1. Projeyi klonlayın veya indirin:
   ```bash
   git clone <repository-url>
   cd on-muhasebe-web
   ```

2. Sanal ortam oluşturun (önerilir):
   ```bash
   python -m venv venv
   ```

3. Sanal ortamı aktifleştirin:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

5. Environment variable'ları ayarlayın:
   ```bash
   cp .env.example .env
   ```
   `.env` dosyasını düzenleyip gerekli değerleri girin (PDF API key, SMTP bilgileri, vb.)

6. Uygulamayı çalıştırın:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 10000
   ```

6. Tarayıcıda açın:
   ```
   http://localhost:10000
   ```

### Render.com Üzerinde Deploy

1. GitHub repository'nizi Render.com'a bağlayın
2. `render.yaml` dosyası otomatik olarak algılanacaktır
3. Deploy işlemi otomatik olarak başlayacaktır

**Not:** Render.com'da veritabanı dosyası (`on_muhasebe.db`) geçici olarak saklanır. Kalıcı veri için Render Disk veya harici bir veritabanı kullanmanız önerilir.

## Proje Yapısı

```
on-muhasebe-web/
├── main.py                 # FastAPI ana uygulama
├── models.py               # Pydantic modelleri
├── routes.py               # HTML route'ları
├── db_instance.py          # Paylaşılan veritabanı instance'ı
├── api/
│   ├── stok.py            # Stok API endpoint'leri
│   ├── cari.py            # Cari hesap API endpoint'leri
│   ├── is_evraki.py       # İş evrakı API endpoint'leri
│   ├── excel.py           # Excel import/export endpoint'leri
│   └── pdf_email.py       # PDF oluşturma ve e-posta fonksiyonları
├── app/
│   ├── database.py        # Veritabanı ana sınıfı
│   ├── db_connection.py   # Veritabanı bağlantı yönetimi
│   ├── db_stok.py         # Stok veritabanı işlemleri
│   ├── db_cari.py         # Cari hesap veritabanı işlemleri
│   └── db_is_evraki.py    # İş evrakı veritabanı işlemleri
├── static/
│   ├── index.html         # Stok yönetimi web arayüzü
│   ├── cari.html          # Cari hesap yönetimi web arayüzü
│   └── is-evraki.html     # İş evrakı web arayüzü
├── requirements.txt       # Python bağımlılıkları
├── render.yaml           # Render.com deployment konfigürasyonu
└── README.md             # Bu dosya
```

## API Endpoints

### Stok Yönetimi
- `GET /api/stok` - Stok listesi
- `GET /api/stok/{id}` - Stok detayı
- `POST /api/stok` - Yeni stok ekle
- `PUT /api/stok/{id}` - Stok güncelle
- `DELETE /api/stok/{id}` - Stok sil
- `GET /api/stok/ara/urun-adi` - Ürün adı ile ara
- `GET /api/stok/ara/urun-kodu` - Ürün kodu ile ara
- `POST /api/stok/miktar-azalt` - Stok miktarı azalt
- `POST /api/stok/miktar-azalt-batch` - Toplu stok miktarı azalt
- `GET /api/stok/excel-export` - Excel'e dışa aktar
- `POST /api/stok/excel-import` - Excel'den içe aktar

### Cari Hesap Yönetimi
- `GET /api/cari` - Cari hesap listesi
- `GET /api/cari/{id}` - Cari hesap detayı
- `POST /api/cari` - Yeni cari hesap ekle
- `PUT /api/cari/{id}` - Cari hesap güncelle
- `DELETE /api/cari/{id}` - Cari hesap sil
- `GET /api/cari/ara/tc` - TC kimlik no ile ara
- `GET /api/cari/ara/unvan` - Ünvan ile ara
- `GET /api/cari/sonraki-kod` - Sonraki cari kodu
- `POST /api/cari/ekle-tc-kontrolu-ile` - TC kontrolü ile cari ekle

### İş Evrakı
- `GET /api/is-evraki` - İş evrakı listesi
- `POST /api/is-evraki` - Yeni iş evrakı oluştur
- `POST /api/is-evraki/kaydet-ve-gonder` - İş evrakı kaydet, PDF oluştur ve e-posta gönder
- `GET /api/is-evraki/sonraki-no` - Sonraki iş emri numarası

### Web Arayüzü
- `GET /` - Ana sayfa
- `GET /stok` - Stok yönetimi sayfası
- `GET /cari` - Cari hesap yönetimi sayfası
- `GET /is-evraki` - İş evrakı sayfası
- `GET /docs` - Swagger UI (API dokümantasyonu)
- `GET /redoc` - ReDoc (API dokümantasyonu)

## Kullanım

### Web Arayüzü

1. Tarayıcıda uygulamayı açın
2. Ana sayfadan istediğiniz modüle tıklayın:
   - **Stok Yönetimi**: Ürün ekleme, düzenleme, silme ve Excel işlemleri
   - **Cari Hesaplar**: Müşteri ve tedarikçi yönetimi
   - **İş Evrakı**: İş emri oluşturma ve PDF gönderme

### API Kullanımı

API endpoint'lerini doğrudan kullanmak için:
- Swagger UI: `http://localhost:10000/docs`
- ReDoc: `http://localhost:10000/redoc`

## Excel İçe/Dışa Aktarma

### Excel İçe Aktarma

Excel dosyasından toplu stok verisi içe aktarabilirsiniz. Excel dosyasında şu sütunlar bulunmalıdır:

**Zorunlu Sütunlar:**
- Ürün Adı (urun, adi, adı, isim, name, product, vb.)
- Miktar (miktar, adet, quantity, stok, vb.)
- Fiyat (fiyat, price, birim_fiyat, birim fiyat, vb.)

**Opsiyonel Sütunlar:**
- Ürün Kodu (kod, code, urun_kodu, vb.)
- Marka (marka, brand)
- Birim (birim, unit)
- Açıklama (aciklama, açıklama, description, vb.)

### Excel Dışa Aktarma

Stok listesini Excel formatında dışa aktarabilirsiniz. Tüm stok verileri Excel dosyasına aktarılır.

## Veritabanı

Uygulama, çalıştığı dizinde `on_muhasebe.db` adında bir SQLite veritabanı dosyası oluşturur. Tüm veriler bu dosyada saklanır.

### Veritabanı Tabloları

- **stok**: Ürün bilgileri (urun_kodu, urun_adi, marka, birim, stok_miktari, birim_fiyat, aciklama)
- **cari**: Cari hesap bilgileri (cari_kodu, unvan, tip, telefon, email, adres, vergi_no, vergi_dairesi, bakiye, tc_kimlik_no, firma_tipi)
- **is_evraki**: İş evrakı kayıtları (is_emri_no, tarih, musteri_unvan, telefon, arac_plakasi, cekici_dorse, marka_model, talep_edilen_isler, musteri_sikayeti, yapilan_is, baslama_saati, bitis_saati, kullanilan_urunler, toplam_tutar, tc_kimlik_no)

### Veritabanı Yedekleme

Veritabanı dosyasını (`on_muhasebe.db`) kopyalayarak yedek alabilirsiniz. Yedekten geri yüklemek için dosyayı uygulamanın çalıştığı dizine kopyalayın.

## PDF ve E-posta Ayarları

PDF oluşturma için `html2pdf.app` API kullanılmaktadır. E-posta gönderme için **Gmail API** kullanılır (Render.com port kısıtlamaları nedeniyle).

**PDF Özellikleri:**
- Tek sayfa, profesyonel tasarım
- Şirket bilgileri otomatik eklenir
- Belge oluşturma tarihi ve saati otomatik eklenir
- Ürün tablosu ve toplam tutar gösterilir
- Notlar ve uyarılar bölümü
- İmza alanları

### Environment Variables (Gerekli)

Uygulama hassas bilgileri environment variable'lardan okur. Yerel geliştirme için:

1. `.env.example` dosyasını `.env` olarak kopyalayın:
   ```bash
   cp .env.example .env
   ```

2. `.env` dosyasını düzenleyin ve değerleri güncelleyin:
   ```env
   # PDF API Key
   PDF_API_KEY=your_pdf_api_key_here
   
   # SMTP Ayarları
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password_here
   
   # E-posta Adresleri
   EMAIL_FROM=your_email@gmail.com
   EMAIL_TO=recipient@example.com
   ```

**Gmail API Kurulumu:**

Gmail API kullanmak için OAuth 2.0 credentials gereklidir:

1. **Google Cloud Console'da Proje Oluşturun:**
   - https://console.cloud.google.com/ adresine gidin
   - Yeni proje oluşturun veya mevcut projeyi seçin

2. **Gmail API'yi Etkinleştirin:**
   - API Library'den "Gmail API" arayın ve etkinleştirin

3. **OAuth 2.0 Credentials Oluşturun:**
   - Credentials → Create Credentials → OAuth client ID
   - Application type: "Desktop app" seçin
   - Credentials JSON dosyasını indirin

4. **İlk Kurulum (Yerel Geliştirme):**
   ```python
   # credentials.json dosyasını proje klasörüne kopyalayın
   # Python script çalıştırın (tek seferlik):
   from google_auth_oauthlib.flow import InstalledAppFlow
   import json
   
   SCOPES = ['https://www.googleapis.com/auth/gmail.send']
   flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
   creds = flow.run_local_server(port=0)
   
   # Token'ı kaydedin
   token_data = {
       'token': creds.token,
       'refresh_token': creds.refresh_token,
       'token_uri': creds.token_uri,
       'client_id': creds.client_id,
       'client_secret': creds.client_secret,
       'scopes': creds.scopes
   }
   print(json.dumps(token_data))
   ```

5. **Environment Variables:**
   - `GMAIL_CREDENTIALS_JSON`: OAuth client credentials JSON (tek seferlik)
   - `GMAIL_TOKEN_JSON`: Refresh token JSON (production için - önerilen)
   - `EMAIL_FROM`: Gönderen e-posta adresi
   - `EMAIL_TO`: Alıcı e-posta adresi

**Render.com Deployment:**
Render.com'da environment variable'ları dashboard'dan ekleyin:
- `PDF_API_KEY`
- `GMAIL_TOKEN_JSON` (production için - refresh token içeren JSON)
- `EMAIL_FROM`
- `EMAIL_TO`

**Not:** Render.com'da interactive OAuth flow çalışmaz, bu yüzden `GMAIL_TOKEN_JSON` kullanmanız gerekir.

## Geliştirme

### Modüler Yapı

Uygulama modüler bir yapıda tasarlanmıştır:
- API endpoint'leri `api/` klasöründe organize edilmiştir
- Veritabanı işlemleri `app/db_*.py` modüllerinde
- Web arayüzü `static/` klasöründe
- Her modül tek bir sorumluluğa sahiptir
- Modüller arası bağımlılıklar minimize edilmiştir

### Yeni Özellik Ekleme

1. Veritabanı işlemleri için `app/db_*.py` modüllerine benzer yeni modül oluşturun
2. API endpoint'leri için `api/` klasöründe yeni router oluşturun
3. Web arayüzü için `static/` klasöründe yeni HTML sayfası oluşturun
4. `main.py` içinde yeni router'ı include edin

## Sorun Giderme

### "Database is locked" Hatası

Bu hata genellikle birden fazla veritabanı instance'ı kullanıldığında oluşur. Çözüm:
- Tüm modüller `db_instance.py`'den aynı instance'ı kullanmalıdır
- Veritabanı dosyasının yazılabilir olduğundan emin olun

### PDF Oluşturma Hatası

- İnternet bağlantınızı kontrol edin (html2pdf.app API gerektirir)
- API anahtarının geçerli olduğundan emin olun

### E-posta Gönderme Hatası

**"Network is unreachable" veya "errno 101" Hatası:**
- Render.com free tier'da SMTP portları (587, 465) kısıtlanmış olabilir
- **Çözüm 1:** Render.com dashboard'dan `SMTP_PORT=465` olarak ayarlayın (SSL kullanır)
- **Çözüm 2:** Render.com'da paid plan kullanın (SMTP portları açık)
- **Çözüm 3:** Harici email servisi kullanın (SendGrid, Mailgun, AWS SES)

**Diğer SMTP Hataları:**
- Gmail hesabınızda 2 Adımlı Doğrulama aktif mi kontrol edin
- Uygulama şifresinin doğru olduğundan emin olun
- SMTP ayarlarının doğru olduğundan emin olun
- Timeout değeri yeterli mi kontrol edin (30 saniye)

## Lisans

Bu proje eğitim ve kişisel kullanım amaçlıdır.

## Destek

Sorularınız veya önerileriniz için lütfen iletişime geçin.
