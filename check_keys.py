import os, requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('backend/.env'))

print("=" * 40)
print("  DIAGNOSTIC DES CLES API - AgriVigil")
print("=" * 40)

# Test OpenWeatherMap
ow_key = os.environ.get('OPENWEATHER_API_KEY', '')
print("\n[1] OpenWeatherMap (Meteo)")
if not ow_key:
    print("    STATUT : VIDE - clé non configurée")
    print("    IMPACT  : L'écran météo retourne une erreur")
    print("    FIX     : Ajouter OPENWEATHER_API_KEY dans backend/.env")
    print("    URL     : https://openweathermap.org/api")
else:
    try:
        r = requests.get(
            'https://api.openweathermap.org/data/2.5/weather',
            params={'q': 'Abidjan', 'appid': ow_key, 'units': 'metric'},
            timeout=8
        )
        if r.status_code == 200:
            data = r.json()
            print(f"    STATUT : OK - {data['main']['temp']}C a Abidjan")
        elif r.status_code == 401:
            print("    STATUT : ERREUR 401 - Cle invalide ou pas encore activee (attendre 2h)")
        else:
            print(f"    STATUT : ERREUR {r.status_code} - {r.json().get('message', '')}")
    except Exception as e:
        print(f"    STATUT : ERREUR reseau - {e}")

# Test Gemini
gem_key = os.environ.get('GEMINI_API_KEY', '')
print("\n[2] Gemini AI (Scan IA)")
if not gem_key:
    print("    STATUT : VIDE - mode SIMULE actif (fonctionne sans cle)")
    print("    IMPACT  : Diagnostic de simulation uniquement (pas le vrai Gemini)")
    print("    FIX     : Ajouter GEMINI_API_KEY dans backend/.env")
    print("    URL     : https://aistudio.google.com/apikey")
else:
    try:
        r = requests.get(
            f'https://generativelanguage.googleapis.com/v1beta/models?key={gem_key}',
            timeout=8
        )
        if r.status_code == 200:
            print(f"    STATUT : OK - cle valide ({gem_key[:10]}...)")
        elif r.status_code == 400:
            print("    STATUT : ERREUR 400 - Cle malformee")
        elif r.status_code == 403:
            print("    STATUT : ERREUR 403 - Cle non autorisee / API non activee")
        else:
            print(f"    STATUT : ERREUR {r.status_code}")
    except Exception as e:
        print(f"    STATUT : ERREUR reseau - {e}")

# Africa's Talking
at_key = os.environ.get('AFRICAS_TALKING_API_KEY', '')
print("\n[3] Africa's Talking (OTP SMS)")
if not at_key:
    print("    STATUT : VIDE")
    print("    IMPACT  : OTP affiché dans la console Django uniquement (pas de SMS reel)")
    print("    FIX     : Optionnel pour le dev - SMS fonctionnent quand meme en console")
else:
    print(f"    STATUT : Configuree ({at_key[:8]}...)")

print("\n" + "=" * 40)
