"""
HTML route handlers for web UI
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """Giriş sayfası (token gerekmez)"""
    try:
        with open("static/login.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Login sayfası bulunamadı</h1>", status_code=404)


@router.get("/", response_class=HTMLResponse)
async def root():
    """Ana sayfa - Web arayüzü"""
    html_content = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ön Muhasebe - Stok & Cari Yönetimi</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 16px;
            }
            .header-left { text-align: left; }
            .header h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            .btn-logout {
                display: inline-block;
                padding: 10px 20px;
                background: transparent;
                color: #666;
                border: 1px solid #ddd;
                border-radius: 8px;
                text-decoration: none;
                font-size: 14px;
                transition: background 0.2s, color 0.2s;
            }
            .btn-logout:hover {
                background: #f5f5f5;
                color: #333;
                border-color: #ccc;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s, box-shadow 0.3s;
                cursor: pointer;
                text-decoration: none;
                color: inherit;
                display: block;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            }
            .card-icon {
                font-size: 3em;
                margin-bottom: 15px;
            }
            .card h2 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 1.5em;
            }
            .card p {
                color: #666;
                line-height: 1.6;
            }
            .footer {
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
            }
            .footer a {
                color: #667eea;
                text-decoration: none;
                margin: 0 15px;
            }
            .footer a:hover {
                text-decoration: underline;
            }
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 2em;
                }
                .cards {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <script>
            (function(){
                var token = localStorage.getItem('token');
                if (!token) { window.location.href = '/login'; return; }
                var orig = window.fetch;
                window.fetch = function(url, opts) {
                    opts = opts || {};
                    if (token) {
                        opts.headers = opts.headers || {};
                        if (opts.headers instanceof Headers) opts.headers.append('Authorization', 'Bearer ' + token);
                        else opts.headers['Authorization'] = 'Bearer ' + token;
                    }
                    return orig.call(this, url, opts).then(function(res) {
                        if (res.status === 401) {
                            localStorage.removeItem('token'); localStorage.removeItem('user');
                            window.location.href = '/login';
                        }
                        return res;
                    });
                };
            })();
        </script>
        <div class="container">
            <div class="header">
                <div class="header-left">
                    <h1>📊 Ön Muhasebe</h1>
                    <p>Stok, Cari Hesap ve İş Evrakı Yönetimi</p>
                </div>
                <a href="#" class="btn-logout" id="logoutBtn" onclick="localStorage.removeItem('token'); localStorage.removeItem('user'); window.location.href='/login'; return false;">Çıkış</a>
            </div>
            
            <div class="cards">
                <a href="/stok" class="card">
                    <div class="card-icon">📦</div>
                    <h2>Stok Yönetimi</h2>
                    <p>Ürün ekleme, güncelleme, silme ve stok takibi yapabilirsiniz.</p>
                </a>
                
                <a href="/cari" class="card">
                    <div class="card-icon">👥</div>
                    <h2>Cari Hesaplar</h2>
                    <p>Müşteri ve tedarikçi bilgilerini yönetebilirsiniz.</p>
                </a>
                
                <a href="/is-evraki" class="card">
                    <div class="card-icon">📄</div>
                    <h2>İş Evrakı</h2>
                    <p>İş emirleri oluşturup yönetebilirsiniz.</p>
                </a>
                
                <a href="/is-prosesi" class="card">
                    <div class="card-icon">⚙️</div>
                    <h2>İş Prosesleri</h2>
                    <p>İş proseslerini tanımlayıp takip edebilirsiniz.</p>
                </a>
                
                <a href="/kullanicilar" class="card">
                    <div class="card-icon">👤</div>
                    <h2>Kullanıcı Yönetimi</h2>
                    <p>Yeni kullanıcı ekleyin (sadece admin).</p>
                </a>
            </div>
            
            <div class="footer" id="mainFooter">
                <span class="footer-docs admin-only-link">
                    <a href="/docs">API Dokümantasyonu</a>
                    <a href="/redoc">ReDoc</a>
                </span>
            </div>
        </div>
        <script>
            (function(){
                try {
                    var u = JSON.parse(localStorage.getItem('user') || 'null');
                    if (u && u.role !== 'admin') {
                        var el = document.querySelector('.admin-only-link');
                        if (el) el.style.display = 'none';
                    }
                } catch(e) {}
            })();
        </script>
    </body>
    </html>
    """
    return html_content


@router.get("/stok", response_class=HTMLResponse)
async def stok_ui():
    """Stok yönetimi web arayüzü"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Stok sayfası bulunamadı</h1>", status_code=404)


@router.get("/cari", response_class=HTMLResponse)
async def cari_ui():
    """Cari hesap yönetimi web arayüzü"""
    try:
        with open("static/cari.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Cari sayfası bulunamadı</h1>", status_code=404)


@router.get("/is-evraki", response_class=HTMLResponse)
async def is_evraki_ui():
    """İş evrakı web arayüzü"""
    try:
        with open("static/is-evraki.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>İş evrakı sayfası bulunamadı</h1>", status_code=404)


@router.get("/is-prosesi", response_class=HTMLResponse)
async def is_prosesi_ui():
    """İş prosesi web arayüzü"""
    try:
        with open("static/is-prosesi.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>İş prosesi sayfası bulunamadı</h1>", status_code=404)


@router.get("/kullanicilar", response_class=HTMLResponse)
async def kullanicilar_ui():
    """Kullanıcı yönetimi sayfası (sayfa içinde admin kontrolü yapılır)"""
    try:
        with open("static/kullanicilar.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Kullanıcı yönetimi sayfası bulunamadı</h1>", status_code=404)
