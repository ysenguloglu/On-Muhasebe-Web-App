"""
PDF oluşturma ve e-posta gönderme fonksiyonları
"""
import os
import smtplib
import tempfile
from datetime import datetime
from typing import List, Dict, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from models import IsEvrakiCreateWithEmail

# Environment variable'ları yükle
from dotenv import load_dotenv
load_dotenv()


async def pdf_olustur_api(evrak: IsEvrakiCreateWithEmail, urunler: List[Dict]) -> Optional[str]:
    """HTML'den PDF oluştur - html2pdf.app API kullanarak"""
    try:
        import requests
        
        is_emri_no = str(evrak.is_emri_no)
        plaka = (evrak.arac_plakasi or "").strip().replace(" ", "_")
        musteri_unvan = evrak.musteri_unvan.strip()
        
        tr_chars = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
        musteri_unvan_temiz = musteri_unvan.translate(tr_chars).replace(" ", "_")
        plaka_temiz = plaka.translate(tr_chars) if plaka else "plaka_yok"
        
        dosya_adi = f"Is_Emri_No_{is_emri_no}_{plaka_temiz}_{musteri_unvan_temiz}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Geçici dosya oluştur
        temp_dir = tempfile.gettempdir()
        dosya_yolu = os.path.join(temp_dir, dosya_adi)
        
        # PDF API key'i environment variable'dan al
        api_key = os.getenv("PDF_API_KEY", "")
        if not api_key:
            raise Exception("PDF_API_KEY environment variable tanımlı değil")
        
        telefon_temiz = (evrak.telefon or "").strip().replace(" ", "")
        isler_str = evrak.talep_edilen_isler or ""
        sikayet = evrak.musteri_sikayeti or ""
        yapilan = evrak.yapilan_is or ""
        baslama = evrak.baslama_saati or "-"
        bitis = evrak.bitis_saati or "-"
        
        # Ürünler tablosu HTML'i
        urun_tablo_html = ""
        toplam_tutar = 0
        if urunler:
            urun_tablo_html = '<h2 style="color: #1f538d; margin-top: 12px; margin-bottom: 8px; font-size: 13px;">Kullanılan Ürünler</h2><table style="width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 9px;"><thead><tr style="background-color: #1f538d; color: white;"><th style="padding: 4px; border: 1px solid #ddd; text-align: left; font-size: 8px;">Ürün Kodu</th><th style="padding: 4px; border: 1px solid #ddd; text-align: left; font-size: 8px;">Ürün Adı</th><th style="padding: 4px; border: 1px solid #ddd; text-align: center; font-size: 8px;">Adet</th><th style="padding: 4px; border: 1px solid #ddd; text-align: right; font-size: 8px;">Birim Fiyat</th><th style="padding: 4px; border: 1px solid #ddd; text-align: right; font-size: 8px;">Toplam</th></tr></thead><tbody>'
            
            for urun in urunler:
                urun_kodu = urun.get("urun_kodu", "") or "-"
                urun_tablo_html += f'<tr><td style="padding: 3px; border: 1px solid #ddd; font-size: 8px;">{urun_kodu}</td><td style="padding: 3px; border: 1px solid #ddd; font-size: 8px;">{urun["urun_adi"]}</td><td style="padding: 3px; border: 1px solid #ddd; text-align: center; font-size: 8px;">{urun["adet"]}</td><td style="padding: 3px; border: 1px solid #ddd; text-align: right; font-size: 8px;">{urun["birim_fiyat"]:.2f} ₺</td><td style="padding: 3px; border: 1px solid #ddd; text-align: right; font-size: 8px;">{urun["toplam"]:.2f} ₺</td></tr>'
                toplam_tutar += urun["toplam"]
            
            urun_tablo_html += f'<tr style="background-color: #e8f0f8; font-weight: bold;"><td colspan="4" style="padding: 4px; border: 1px solid #ddd; text-align: right; font-size: 8px;">TOPLAM:</td><td style="padding: 4px; border: 1px solid #ddd; text-align: right; font-size: 8px;">{toplam_tutar:.2f} ₺</td></tr></tbody></table>'
        
        # Belge oluşturma tarihi ve saati
        olusturma_tarihi = datetime.now().strftime('%d.%m.%Y')
        olusturma_saati = datetime.now().strftime('%H:%M')
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@page {{
    margin: 15mm;
    size: A4;
}}
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    color: #333;
    font-size: 10px;
    line-height: 1.3;
}}
h1 {{
    color: #1f538d;
    text-align: center;
    font-size: 18px;
    margin-bottom: 8px;
    margin-top: 0;
    padding-bottom: 5px;
}}
.company-info {{
    text-align: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #1f538d;
}}
.company-name {{
    font-size: 12px;
    font-weight: bold;
    color: #1f538d;
    margin-bottom: 4px;
}}
.company-details {{
    font-size: 9px;
    color: #555;
    line-height: 1.4;
}}
.document-info {{
    text-align: right;
    font-size: 8px;
    color: #666;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid #ddd;
}}
h2 {{
    color: #1f538d;
    font-size: 13px;
    margin-top: 12px;
    margin-bottom: 8px;
}}
.two-column-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
}}
.two-column-table td {{
    padding: 4px 6px;
    border: 1px solid #ddd;
    font-size: 9px;
    vertical-align: top;
    line-height: 1.2;
}}
.two-column-table td.label {{
    background-color: #e8f0f8;
    font-weight: bold;
    width: 35%;
}}
.two-column-table td.value {{
    background-color: #fff;
    width: 15%;
}}
.notes-section {{
    margin-top: 15px;
    padding-top: 10px;
    border-top: 2px solid #1f538d;
}}
.notes-section ul {{
    margin-top: 8px;
    padding-left: 18px;
    font-size: 8px;
    line-height: 1.4;
    margin-bottom: 10px;
}}
.notes-section li {{
    margin-bottom: 3px;
}}
.signature-section {{
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #1f538d;
    display: flex;
    justify-content: space-around;
    align-items: flex-start;
}}
.signature-box {{
    text-align: center;
    width: 45%;
}}
.signature-box div {{
    margin-bottom: 30px;
    font-size: 9px;
}}
.signature-line {{
    border-top: 1px solid #333;
    width: 100%;
    margin: 0 auto;
    padding-top: 3px;
}}
</style>
</head>
<body>
    <h1>İŞ EVRAKI</h1>
    <div class="company-info">
        <div class="company-name">Ali Usta Ağır Vasıta Fren Servisi</div>
        <div class="company-details">
            Adres: Sevindik Mah. 2292/1 Sokak No:11 Merkezefendi - Denizli<br>
            Telefon: +90 507 794 38 19
        </div>
    </div>
    <div class="document-info">
        Belge Oluşturma: {olusturma_tarihi} {olusturma_saati}
    </div>
    <table class="two-column-table">
        <tr>
            <td class="label">1. İş Emri No:</td>
            <td class="value">{is_emri_no}</td>
            <td class="label">2. Tarih:</td>
            <td class="value">{evrak.tarih}</td>
        </tr>
        <tr>
            <td class="label">3. Müşteri Ünvanı:</td>
            <td class="value" colspan="3">{musteri_unvan}</td>
        </tr>
        <tr>
            <td class="label">4. Telefon:</td>
            <td class="value">{telefon_temiz or "-"}</td>
            <td class="label">5. Araç Plakası:</td>
            <td class="value">{evrak.arac_plakasi or "-"}</td>
        </tr>
        <tr>
            <td class="label">6. Çekici / Dorse:</td>
            <td class="value">{evrak.cekici_dorse or "-"}</td>
            <td class="label">7. Marka / Model:</td>
            <td class="value">{evrak.marka_model or "-"}</td>
        </tr>
        <tr>
            <td class="label">8. Talep Edilen İşler:</td>
            <td class="value" colspan="3">{isler_str}</td>
        </tr>'''
        
        if sikayet:
            html_content += f'''
        <tr>
            <td class="label">9. Müşteri Şikayeti:</td>
            <td class="value" colspan="3">{sikayet}</td>
        </tr>'''
        
        if yapilan:
            html_content += f'''
        <tr>
            <td class="label">10. Yapılan İş Açıklaması:</td>
            <td class="value" colspan="3">{yapilan}</td>
        </tr>'''
        
        html_content += f'''
        <tr>
            <td class="label">11. İşe Başlama Saati:</td>
            <td class="value">{baslama}</td>
            <td class="label">12. İş Bitiş Saati:</td>
            <td class="value">{bitis}</td>
        </tr>
    </table>
    {urun_tablo_html}
    <div class="notes-section">
        <h2>NOTLAR / UYARILAR</h2>
        <ul>
            <li>İş emrinde belirtilen fiyatlar KDV hariçtir.</li>
            <li>Sadece iş emrinde belirtilen işlemler yapılmış olup, diğer mekanik ve elektronik aksamlar bu kapsam dışında bırakılmıştır.</li>
            <li>Bu iş emrinde belirtilen işlemler müşteri onayı ile yapılmıştır.</li>
            <li>Kontrol edilmeyen aksamlar, gizli arızalar, kullanım hataları ve çevresel şartlardan kaynaklanan sorunlardan servisimiz sorumlu değildir.</li>
            <li>Kullanılan parçaların garanti şartları üretici firma koşullarıyla sınırlıdır.</li>
            <li>Fren ve yürüyen aksamlar, aracın kullanım koşullarına doğrudan bağlı sistemlerdir. Aşırı yük, uygunsuz kullanım ve ihmal edilen bakım durumlarında servis sorumluluğu kabul edilmez.</li>
        </ul>
        <div class="signature-section">
            <div class="signature-box">
                <div>Müşterinin Adı Soyadı:</div>
                <div class="signature-line"></div>
            </div>
            <div class="signature-box">
                <div>İmza:</div>
                <div class="signature-line"></div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        api_url = "https://api.html2pdf.app/v1/generate"
        payload = {"html": html_content, "apiKey": api_key, "format": "A4", "landscape": False}
        
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()
        
        with open(dosya_yolu, 'wb') as f:
            f.write(response.content)
        
        return dosya_yolu
        
    except Exception as e:
        raise Exception(f"PDF oluşturma hatası: {str(e)}")


async def email_gonder_api(evrak: IsEvrakiCreateWithEmail, pdf_dosyasi: str) -> bool:
    """E-posta gönder - Gmail SMTP"""
    try:
        # Environment variable'lardan SMTP ayarlarını al
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        email_from = os.getenv("EMAIL_FROM", smtp_user)
        email_to = os.getenv("EMAIL_TO", "")
        
        if not smtp_user or not smtp_password:
            raise Exception("SMTP_USER ve SMTP_PASSWORD environment variable'ları tanımlı olmalı")
        if not email_to:
            raise Exception("EMAIL_TO environment variable tanımlı olmalı")
        
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = f"Servis İş Emri - {evrak.arac_plakasi or 'N/A'} - {evrak.musteri_unvan}"
        
        body = f"""{datetime.now().strftime('%d.%m.%Y')} tarihine ait iş emri PDF olarak ekte gönderilmiştir."""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with open(pdf_dosyasi, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(pdf_dosyasi)}'
            )
            msg.attach(part)
        
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        raise Exception(f"E-posta gönderme hatası: {str(e)}")
