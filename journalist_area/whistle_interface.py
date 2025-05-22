import argparse

from src.rsa_key_generator import generate_multiple_keys, write_keys_to_database
from src.rsa_key_uploader import get_public_keys, create_temp_key_file, upload_key_file, update_local_database
from src.clear_my_database import clear_everything
from src.fetch_all import start_fetching
from src.decrypt_files import decrypt_all
import dotenv
import os
import requests

dotenv.load_dotenv()

session = requests.Session()

# Set default proxy (e.g., for Tor)
session.proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

BASE_URL: str =  f"http://{os.getenv('ONION')}/api/v1"

# Optional: Set a default timeout (via a wrapper function)
def tor_get(url, **kwargs):
    return session.get(BASE_URL + url, timeout=30, **kwargs)

# Optional: Set a default timeout (via a wrapper function)
def tor_post(url, **kwargs):
    # print(BASE_URL + url)
    return session.post(BASE_URL + url, timeout=30, **kwargs)

def upload(count: int, token: str):

    DEFAULT_SIZE = 2048
    key_list = generate_multiple_keys(count=count, key_size=DEFAULT_SIZE)

    write_keys_to_database(keys=key_list)
    print(count, "RSA Key(s) created ")

    keys, ids = get_public_keys()

    print(f"{len(keys)} Found key.")
    for index, key in enumerate(keys):
        filename = create_temp_key_file(key, index)
        upload_key_file(filename, token, tor_post, ids[index])

    print("..und auf den Server hochgeladen")

    update_local_database()

def download(token: str):
    start_fetching(token, tor_get=tor_get)

def cleanup():
    clear_everything()
    print("Es wurde alles gelöscht")

def authenticate_user():
    passphrase = input("Please enter your passphrase: ")

    auth_url = "/auth/login"

    print("Authenticating user...")
    # Send the POST request
    login_response = tor_post(auth_url, json={"passphrase": passphrase})

    if login_response.status_code != 200:
        print("Authentication failed. Exiting.")
        exit(0)
    else:
        print("Authentication successful.")
        return login_response.json()["access_token"]

def main():
    parser = argparse.ArgumentParser(description="Here you have full control, Mr. Journalist. "
                                                 "First, you need to provide your public keys to the whistleblower (-> upload --count X), then you can download the files (if any are available) with the download command. "
                                                 "If you get fired or resign, we ask you to delete your local data with cleanup. Thank you for using our tool. Your Cyber Espionage Team")

    subparsers = parser.add_subparsers(title="Functions", dest="command", required=True)

    # Upload
    upload_parser = subparsers.add_parser("upload", help="Creates & uploads all your public RSA keys to the server | Please specify the number of keys")
    upload_parser.add_argument("--count", type=int, default=1, help="Number of keys to generate (default: 1)")
    upload_parser.add_argument("-d", help="Run in debug mode", action="store_true")
    # Download
    download_parser = subparsers.add_parser("download", help="Downloads all files from the server")
    download_parser.add_argument("-d", help="Run in debug mode", action="store_true")

    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Deletes RSA keys, local database & local files")

    args = parser.parse_args()


    if args.command == "upload":

        token = authenticate_user()
        print(token)
        upload(args.count, token)
    elif args.command == "download":
        token = authenticate_user()
        download(token)
        decrypt_all()
    elif args.command == "cleanup":
        cleanup()


if __name__ == "__main__":
    main()
