import os
import configparser
from email.feedparser import headerRE

import requests
import zipfile
import io
from datetime import datetime, timedelta
import os.path
from dotenv import load_dotenv

load_dotenv()

DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "./downloads")

CONFIG_FILE = "./config.ini"

# Helper function for formatting date/time
def format_datetime(dt):
    # add one second to the datetime object
    if isinstance(dt, datetime):
        dt = dt + timedelta(seconds=1)
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return None

# Helper function for parsing date/time strings
def parse_datetime(dt_str):
    if dt_str:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    return None

# Read the last fetch date from the INI file
def get_last_fetch_date():
    config = configparser.ConfigParser()
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'fetch' in config and 'last_date' in config['fetch']:
            return config['fetch']['last_date']
    
    return None

# Save the latest fetch date to the INI file
def save_last_fetch_date(last_date):
    config = configparser.ConfigParser()
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    
    if 'fetch' not in config:
        config['fetch'] = {}
    
    config['fetch']['last_date'] = last_date
    
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Ensure that the download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def start_fetching(token, tor_get):
    # Get the last fetch date
    last_fetch_date = get_last_fetch_date()
    
    # If no last fetch date is available, we set it to an early date
    if not last_fetch_date:
        print("No previous fetch date found. Will fetch all files.")
        # ISO Format for the API: YYYY-MM-DD
        fetch_date_for_api = "2000-01-01"
    else:
        # Convert the saved date to ISO format for the API
        parsed_date = parse_datetime(last_fetch_date)
        fetch_date_for_api = parsed_date.strftime('%Y-%m-%d')
        print(f"Fetching files newer than {fetch_date_for_api}")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Send API request
    response = tor_get(
        f"/download/new-files/?since_date={fetch_date_for_api}",
        headers=headers
    )
    
    # Error handling
    if response.status_code == 404:
        print("No new files found since the specified date")
    elif response.status_code != 200:
        print(f"Error fetching files: {response.status_code} - {response.text}")
    else:
        # Extract the ZIP file
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # List of files we extract
            file_list = zip_ref.namelist()
            print(f"Found {len([f for f in file_list if not f.endswith('_key_info.txt')])} new file(s)")
            
            # Extract all files
            zip_ref.extractall(DOWNLOAD_FOLDER)
            
            print(f"All files have been downloaded to {DOWNLOAD_FOLDER}")
        
        # Update the date to today
        current_date = format_datetime(datetime.now())
        save_last_fetch_date(current_date)
        print(f"Updated last fetch date to {current_date}")
