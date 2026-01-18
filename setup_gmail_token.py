"""
Gmail API Token Oluşturma Script'i
Bu script'i yerel bilgisayarınızda çalıştırın (tek seferlik)
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
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
    
    print("\n" + "="*70)
    print("✅ TOKEN BAŞARIYLA OLUŞTURULDU!")
    print("="*70)
    print("\nAŞAĞIDAKI JSON'U KOPYALAYIN VE RENDER.COM'A EKLEYIN:")
    print("\nKey: GMAIL_TOKEN_JSON")
    print("Value:")
    print("-"*70)
    print(json.dumps(token_data))
    print("-"*70)
    print("\n⚠️  ÖNEMLİ:")
    print("1. Bu JSON'u Render.com dashboard'dan Environment Variables'a ekleyin")
    print("2. JSON'u tek satır olarak yapıştırın (tüm tırnak işaretleri korunmalı)")
    print("3. credentials.json dosyasını git'e commit etmeyin (güvenlik)")
    print("="*70)

if __name__ == '__main__':
    main()
