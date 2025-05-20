import os
import configparser
import requests
import zipfile
import io
from datetime import datetime, timedelta
import os.path
from dotenv import load_dotenv

load_dotenv()

DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "../downloads")

CONFIG_FILE = "../last_fetch.ini"

# Hilfsfunktion zum Formatieren von Datum/Zeit
def format_datetime(dt):
    # add one second to the datetime object
    if isinstance(dt, datetime):
        dt = dt + timedelta(seconds=1)
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return None

# Hilfsfunktion zum Parsen von Datum/Zeit-Strings
def parse_datetime(dt_str):
    if dt_str:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    return None

# Lese das letzte Abrufdatum aus der INI-Datei
def get_last_fetch_date():
    config = configparser.ConfigParser()
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'fetch' in config and 'last_date' in config['fetch']:
            return config['fetch']['last_date']
    
    return None

# Speichere das neueste Abrufdatum in der INI-Datei
def save_last_fetch_date(last_date):
    config = configparser.ConfigParser()
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    
    if 'fetch' not in config:
        config['fetch'] = {}
    
    config['fetch']['last_date'] = last_date
    
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Stelle sicher, dass der Download-Ordner existiert
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def start_fetching():
    # Hole das letzte Abrufdatum
    last_fetch_date = get_last_fetch_date()
    
    # Wenn kein letztes Abrufdatum vorhanden ist, setzen wir es auf ein frühes Datum
    if not last_fetch_date:
        print("No previous fetch date found. Will fetch all files.")
        # ISO Format für das API: YYYY-MM-DD
        fetch_date_for_api = "2000-01-01"
    else:
        # Konvertiere das gespeicherte Datum ins ISO-Format für die API
        parsed_date = parse_datetime(last_fetch_date)
        fetch_date_for_api = parsed_date.strftime('%Y-%m-%d')
        print(f"Fetching files newer than {fetch_date_for_api}")

    login_response = requests.post(
        "http://127.0.0.1:8000/api/v1/auth/login/",
        json={"passphrase": os.getenv("POSTGRES_ADMIN_PASSWORD")}
    )

    # Überprüfe die Antwort des Login-Requests
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        exit(1)

    # Extrahiere den API-Token aus der Antwort
    login_data = login_response.json()
    API_TOKEN = login_data.get("access_token")

    # API-Anfrage vorbereiten
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    # API-Anfrage senden
    response = requests.get(
        f"http://127.0.0.1:8000/api/v1/download/new-files/?since_date={fetch_date_for_api}",
        headers=headers
    )
    
    # Fehlerbehandlung
    if response.status_code == 404:
        print("No new files found since the specified date")
    elif response.status_code != 200:
        print(f"Error fetching files: {response.status_code} - {response.text}")
    else:
        # Extrahiere die ZIP-Datei
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # Liste der Dateien, die wir extrahieren
            file_list = zip_ref.namelist()
            print(f"Found {len([f for f in file_list if not f.endswith('_key_info.txt')])} new file(s)")
            
            # Extrahiere alle Dateien
            zip_ref.extractall(DOWNLOAD_FOLDER)
            
            print(f"All files have been downloaded to {DOWNLOAD_FOLDER}")
        
        # Aktualisiere das Datum auf heute
        current_date = format_datetime(datetime.now())
        save_last_fetch_date(current_date)
        print(f"Updated last fetch date to {current_date}")
