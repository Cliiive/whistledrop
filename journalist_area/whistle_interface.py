import argparse

from src.rsa_key_generator import generate_multiple_keys, write_keys_to_database
from src.rsa_key_uploader import get_public_keys, create_temp_key_file, upload_key_file
from src.clear_my_database import clear_everything
import requests

def upload(count: int, token: str):

    DEFAULT_SIZE = 2048
    key = generate_multiple_keys(count=count, key_size=DEFAULT_SIZE)

    write_keys_to_database(keys=key)
    print(count, "RSA Key(s) created ")


    print(f"{len(key)} Found key.")
    for index, k in enumerate(key):
        filename = create_temp_key_file(k, index)
        upload_key_file(filename)

    print("..und auf den Server hochgeladen")

def download():
    print("noch implementieren")

def cleanup():
    clear_everything()
    print("Es wurde alles gelöscht")

def authenticate_user():
    passphrase = input("Please enter your passphrase: ")

    auth_url = "http://localhost:8000/api/v1/auth/login"

    print("Authenticating user...")
    # Send the POST request
    login_response = requests.post(auth_url, json={"passphrase": passphrase})

    if login_response.status_code != 200:
        print("Login failed:", login_response.text)
        return None
    else:
        print("Login successful.")
        return login_response.json()["access_token"]

def main():
    parser = argparse.ArgumentParser(description="Here you have full control, Mr. Journalist. "
                                                 "First, you need to provide your public keys to the whistleblower (-> upload --count X), then you can download the files (if any are available) with the download command. "
                                                 "If you get fired or resign, we ask you to delete your local data with cleanup. Thank you for using our tool. Your Cyber Espionage Team")

    subparsers = parser.add_subparsers(title="Functions", dest="command", required=True)

    # Upload
    upload_parser = subparsers.add_parser("upload", help="Creates & uploads all your public RSA keys to the server | Please specify the number of keys")
    upload_parser.add_argument("--count", type=int, default=1, help="Number of keys to generate (default: 1)")

    # Download
    download_parser = subparsers.add_parser("download", help="Downloads all files from the server")

    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Deletes RSA keys, local database & local files")

    args = parser.parse_args()


    if args.command == "upload":
        token = authenticate_user()
        upload(args.count, token)
    elif args.command == "download":
        print("download")
        #download()
    elif args.command == "cleanup":
        cleanup()


if __name__ == "__main__":
    main()
