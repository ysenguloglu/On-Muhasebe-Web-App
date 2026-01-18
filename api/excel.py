"""
Excel import/export API endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
import tempfile
from datetime import datetime
from db_instance import db

router = APIRouter(prefix="/api/stok", tags=["excel"])


@router.get("/excel-export")
async def stok_excel_export():
    """Export stock data to Excel file"""
    try:
        import pandas as pd
        
        urunler = db.stok_listele("")
        
        if not urunler:
            raise HTTPException(status_code=404, detail="Dışa aktarılacak stok kaydı bulunamadı")
        
        data = []
        for urun in urunler:
            data.append({
                "Ürün Kodu": urun.get("urun_kodu") or "",
                "Ürün Adı": urun.get("urun_adi", ""),
                "Marka": urun.get("marka", ""),
                "Birim": urun.get("birim", ""),
                "Stok Miktarı": urun.get("stok_miktari", 0),
                "Birim Fiyat": urun.get("birim_fiyat", 0),
                "Açıklama": urun.get("aciklama", "")
            })
        
        df = pd.DataFrame(data)
        
        # Geçici dosya oluştur
        temp_dir = tempfile.gettempdir()
        filename = f"stok_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        tmp_file_path = os.path.join(temp_dir, filename)
        
        # Dosyayı oluştur
        df.to_excel(tmp_file_path, index=False, engine='openpyxl')
        
        # Dosyanın var olduğundan emin ol
        if not os.path.exists(tmp_file_path):
            raise HTTPException(status_code=500, detail="Excel dosyası oluşturulamadı")
        
        return FileResponse(
            path=tmp_file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
    
    except ImportError:
        raise HTTPException(status_code=500, detail="pandas modülü bulunamadı")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        raise HTTPException(status_code=500, detail=f"Excel dışa aktarma hatası: {error_detail}")


@router.post("/excel-import")
async def stok_excel_import(file: UploadFile = File(...)):
    """Import stock data from Excel file"""
    try:
        import pandas as pd
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            df = pd.read_excel(tmp_file_path)
            
            def normalize_text(text):
                replacements = {
                    'ü': 'u', 'Ü': 'U', 'ı': 'i', 'İ': 'I',
                    'ğ': 'g', 'Ğ': 'G', 'ş': 's', 'Ş': 'S',
                    'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
                }
                result = str(text)
                for tr, en in replacements.items():
                    result = result.replace(tr, en)
                return result.lower().strip()
            
            sutun_eslestirme = {}
            mevcut_sutunlar_normalized = {normalize_text(col): col for col in df.columns}
            
            eslestirme_kurallari = {
                "urun_adi": ["urun", "adi", "adı", "isim", "name", "product", "urun adi", "ürün adı", "urun_adi"],
                "urun_kodu": ["kod", "code", "urun_kodu", "ürün kodu", "urun kodu", "product code"],
                "marka": ["marka", "brand"],
                "birim": ["birim", "unit"],
                "miktar": ["miktar", "adet", "quantity", "stok", "stok miktari", "stok_miktari"],
                "fiyat": ["fiyat", "price", "birim_fiyat", "birim fiyat", "birimfiyat", "fiyati", "fiyatı", "unit price"],
                "aciklama": ["aciklama", "açıklama", "description", "not", "notlar", "notes"]
            }
            
            for hedef, anahtar_kelimeler in eslestirme_kurallari.items():
                for normalized_col, original_col in mevcut_sutunlar_normalized.items():
                    for anahtar in anahtar_kelimeler:
                        normalized_anahtar = normalize_text(anahtar)
                        if normalized_anahtar == normalized_col:
                            sutun_eslestirme[hedef] = original_col
                            break
                    if hedef in sutun_eslestirme:
                        break
            
            eksikler = []
            if "urun_adi" not in sutun_eslestirme:
                eksikler.append("Ürün Adı")
            if "miktar" not in sutun_eslestirme:
                eksikler.append("Miktar")
            if "fiyat" not in sutun_eslestirme:
                eksikler.append("Fiyat")
            
            if eksikler:
                raise HTTPException(
                    status_code=400,
                    detail=f"Excel dosyasında şu sütunlar bulunamadı: {', '.join(eksikler)}"
                )
            
            basarili = 0
            hatali = 0
            hata_mesajlari = []
            
            for index, row in df.iterrows():
                try:
                    urun_adi_col = sutun_eslestirme.get("urun_adi")
                    if not urun_adi_col:
                        hatali += 1
                        hata_mesajlari.append(f"Satır {index + 2}: Ürün adı sütunu bulunamadı")
                        continue
                    
                    urun_adi_val = row[urun_adi_col]
                    if pd.isna(urun_adi_val):
                        continue
                    urun_adi = str(urun_adi_val).strip()
                    if not urun_adi or urun_adi.lower() in ["nan", "none", "null", ""]:
                        continue
                    
                    urun_kodu = ""
                    if "urun_kodu" in sutun_eslestirme:
                        urun_kodu_col = sutun_eslestirme["urun_kodu"]
                        if urun_kodu_col != urun_adi_col:
                            urun_kodu_val = row[urun_kodu_col]
                            if pd.notna(urun_kodu_val):
                                urun_kodu = str(urun_kodu_val).strip()
                                if urun_kodu.lower() in ["nan", "none", "null", ""]:
                                    urun_kodu = ""
                    
                    marka = ""
                    if "marka" in sutun_eslestirme:
                        marka_val = row[sutun_eslestirme["marka"]]
                        if pd.notna(marka_val):
                            marka = str(marka_val).strip()
                            if marka.lower() in ["nan", "none", "null"]:
                                marka = ""
                    
                    birim = "Adet"
                    if "birim" in sutun_eslestirme:
                        birim_val = row[sutun_eslestirme["birim"]]
                        if pd.notna(birim_val):
                            birim_str = str(birim_val).strip()
                            if birim_str.lower() not in ["nan", "none", "null", ""]:
                                birim = birim_str
                    
                    miktar = 0.0
                    if "miktar" in sutun_eslestirme:
                        miktar_val = row[sutun_eslestirme["miktar"]]
                        if pd.notna(miktar_val):
                            try:
                                miktar = float(miktar_val)
                            except (ValueError, TypeError):
                                try:
                                    miktar = float(str(miktar_val).replace(",", "."))
                                except:
                                    miktar = 0.0
                    
                    fiyat = 0.0
                    if "fiyat" in sutun_eslestirme:
                        fiyat_col = sutun_eslestirme["fiyat"]
                        fiyat_val = row[fiyat_col]
                        if pd.notna(fiyat_val):
                            try:
                                if isinstance(fiyat_val, (int, float)):
                                    fiyat = float(fiyat_val)
                                else:
                                    fiyat_str = str(fiyat_val).strip().replace(",", ".").replace(" ", "")
                                    fiyat_str = ''.join(c for c in fiyat_str if c.isdigit() or c in ['.', '-'])
                                    if fiyat_str:
                                        fiyat = float(fiyat_str)
                            except (ValueError, TypeError):
                                fiyat = 0.0
                    
                    aciklama = ""
                    if "aciklama" in sutun_eslestirme:
                        aciklama_val = row[sutun_eslestirme["aciklama"]]
                        if pd.notna(aciklama_val):
                            aciklama = str(aciklama_val).strip()
                            if aciklama.lower() in ["nan", "none", "null"]:
                                aciklama = ""
                    
                    sonuc = db.stok_ekle(urun_kodu, urun_adi, marka, birim, miktar, fiyat, aciklama)
                    if sonuc:
                        basarili += 1
                    else:
                        hatali += 1
                        if urun_kodu:
                            hata_mesajlari.append(f"Satır {index + 2}: {urun_adi} (Kod: {urun_kodu}) - Ürün kodu zaten mevcut")
                        else:
                            mevcut_urun = db.stok_urun_adi_ile_ara(urun_adi)
                            if mevcut_urun:
                                hata_mesajlari.append(f"Satır {index + 2}: {urun_adi} - Aynı isimde ürün zaten mevcut")
                            else:
                                hata_mesajlari.append(f"Satır {index + 2}: {urun_adi} - Eklenemedi")
                
                except Exception as e:
                    hatali += 1
                    hata_mesajlari.append(f"Satır {index + 2}: {str(e)}")
            
            return {
                "success": True,
                "basarili": basarili,
                "hatali": hatali,
                "hata_mesajlari": hata_mesajlari[:10]  # Limit to first 10 errors
            }
        
        finally:
            os.unlink(tmp_file_path)
    
    except ImportError:
        raise HTTPException(status_code=500, detail="pandas modülü bulunamadı")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
