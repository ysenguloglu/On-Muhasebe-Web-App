# Ön Muhasebe Web Uygulaması

FastAPI ile geliştirilmiş, web tabanlı ön muhasebe uygulaması. Stok yönetimi, cari hesap yönetimi ve iş evrakı oluşturma özelliklerini içerir.

## 🚀 Özellikler

- **📦 Stok Yönetimi**: Ürün ekleme, düzenleme, silme, Excel'den içe/dışa aktarma
- **👥 Cari Hesap Yönetimi**: Müşteri ve tedarikçi kayıtları, TC/VKN kontrolü
- **📄 İş Evrakı**: İş emri oluşturma, PDF oluşturma ve e-posta gönderme
- **📊 Aylık Rapor**: Müşteri sayısı, ciro ve ürün kullanım özeti — PDF olarak EMAIL_TO adresine aylık gönderim
- **🌐 Web Arayüzü**: Modern, mobil uyumlu arayüz
- **💾 Veritabanı**: MySQL

## 📋 Gereksinimler

- Python 3.9 veya üzeri
- MySQL (DATABASE_URL zorunlu)

## 🔧 Kurulum

### 1. Projeyi İndirin

```bash
git clone <repository-url>
cd on-muhasebe-web
```

### 2. Sanal Ortam Oluşturun ve Aktifleştirin

```bash
# Sanal ortam oluştur
python -m venv venv

# Aktifleştir (Windows)
venv\Scripts\activate

# Aktifleştir (macOS/Linux)
source venv/bin/activate
```

### 3. Paketleri Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Ayarlayın

`.env.example` dosyasını `.env` olarak kopyalayın ve düzenleyin:

```bash
cp .env.example .env
```

`.env` dosyasında şu değişkenleri ayarlayın:

```env
# PDF API Key (html2pdf.app)
PDF_API_KEY=your_api_key_here

# Gmail API (E-posta gönderme için)
GMAIL_CREDENTIALS_JSON={"type":"service_account",...}
GMAIL_TOKEN_JSON={"token":"...","refresh_token":"..."}

# E-posta Ayarları
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com

# Veritabanı (Zorunlu - MySQL)
DATABASE_URL=mysql://user:password@host:port/database
```

### 5. Uygulamayı Çalıştırın

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

Tarayıcıda açın: `http://localhost:10000`

## 🌐 Deployment (Railway/Render)

### Railway.com

1. Railway.com'da yeni proje oluşturun
2. GitHub repository'nizi bağlayın
3. MySQL servisi ekleyin
4. Environment variables ekleyin (DATABASE_URL zorunlu):
   - `DATABASE_URL` → MySQL servisinden (veya kendi MySQL adresiniz)
   - `PDF_API_KEY`
   - `GMAIL_TOKEN_JSON`
   - `EMAIL_FROM`
   - `EMAIL_TO`

### Render.com

1. Render.com'da yeni Web Service oluşturun
2. GitHub repository'nizi bağlayın
3. Environment variables'ı ekleyin
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 📧 Gmail API Kurulumu

E-posta göndermek için Gmail API kurulumu gereklidir:

1. **Google Cloud Console**'da proje oluşturun
2. **Gmail API**'yi etkinleştirin
3. **OAuth 2.0 Credentials** oluşturun (Desktop app)
4. `credentials.json` dosyasını indirin
5. İlk kurulum için `setup_gmail_token.py` scriptini çalıştırın
6. Oluşan token'ı `GMAIL_TOKEN_JSON` environment variable'ına ekleyin

Detaylı kurulum için: `GMAIL_API_KURULUM.md`

## 📁 Proje Yapısı

```
on-muhasebe-web/
├── main.py              # FastAPI ana uygulama
├── models.py            # Veri modelleri
├── api/                 # API endpoint'leri
│   ├── stok.py
│   ├── cari.py
│   ├── is_evraki.py
│   └── pdf_email.py
├── app/                 # Veritabanı işlemleri
│   ├── database.py
│   ├── db_connection.py
│   ├── db_stok.py
│   ├── db_cari.py
│   └── db_is_evraki.py
└── static/              # Web arayüzü
    ├── index.html
    ├── cari.html
    └── is-evraki.html
```

## 🎯 Kullanım

### Web Arayüzü

- **Ana Sayfa**: `http://localhost:10000`
- **Stok Yönetimi**: `/stok`
- **Cari Hesaplar**: `/cari`
- **İş Evrakı**: `/is-evraki`

### Aylık İş Evrakları Raporu (PDF)

İş evraklarından müşteri sayısı, ciro ve ürün kullanım özetini PDF olarak **EMAIL_TO** adresine gönderir.

**Otomatik gönderim (uygulama içi):**  
`.env` içinde `AYLIK_RAPOR_OTOMATIK=1` (veya `true` / `yes`) tanımlayın. Uygulama her **ayın 1’i 09:00 (İstanbul)** bir önceki ayın raporunu otomatik oluşturup e‑posta ile gönderir. Ek cron / dış servis gerekmez.

**Manuel veya dış cron:**
- **Endpoint**: `POST /api/aylik-rapor/gonder`
- **Parametreler** (opsiyonel): `?ay=1&yil=2025` — verilmezse önceki ay kullanılır.
- **Dış cron güvenliği**: `CRON_SECRET` tanımlıysa `?secret=CRON_SECRET` veya `X-Cron-Secret` header’ı gerekir.

Örnek (dış cron):
```bash
curl -X POST "https://your-app.onrender.com/api/aylik-rapor/gonder?secret=YOUR_CRON_SECRET"
```

### API Dokümantasyonu

- **Swagger UI**: `http://localhost:10000/docs`
- **ReDoc**: `http://localhost:10000/redoc`

## 💾 Veritabanı

Yalnızca MySQL kullanılır. `DATABASE_URL` ortam değişkeni zorunludur:

```env
DATABASE_URL=mysql://user:password@host:port/database
```

Örnek: `mysql://user:password@localhost:3306/onmuhasebe` veya `mysql+pymysql://...`

## 🔍 Sorun Giderme

### Veritabanı Bağlantı Hatası

- MySQL için `cryptography` paketinin yüklü olduğundan emin olun
- `DATABASE_URL` formatının doğru olduğunu kontrol edin

### E-posta Gönderme Hatası

- Gmail API token'ının geçerli olduğundan emin olun
- `GMAIL_TOKEN_JSON` environment variable'ının doğru formatta olduğunu kontrol edin

### PDF Oluşturma Hatası

- İnternet bağlantınızı kontrol edin
- `PDF_API_KEY`'in geçerli olduğundan emin olun

## 📝 Lisans

Bu proje eğitim ve kişisel kullanım amaçlıdır.
