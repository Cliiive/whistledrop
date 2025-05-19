import argparse

from src.rsa_key_generator import generate_multiple_keys, write_keys_to_database
from src.rsa_key_uploader import get_public_keys, create_temp_key_file, upload_key_file
from src.clear_my_database import clear_everything

def upload(count: int):

    DEFAULT_SIZE = 2048
    key = generate_multiple_keys(count=count, key_size=DEFAULT_SIZE)

    write_keys_to_database(keys=key)
    print(count, "RSA Key(s) wurde(n) erstellt ")


    print(f"{len(key)} Schlüssel gefunden.")
    for index, k in enumerate(key):
        filename = create_temp_key_file(k, index)
        upload_key_file(filename)

    print("..und auf den Server hochgeladen")

def download():
    print("noch implementieren")

def cleanup():
    clear_everything()
    print("Es wurde alles gelöscht")

def main():
    parser = argparse.ArgumentParser(description="Hier haben sie die volle Kontrolle Herr Journalist. Als erstes müssen sie dem Whistleblower ihre public Keys zur verfügung stellen (-> upload --count X), danach können sie die Dateien (falls welche vorhanden sind) mit dem Befehl download herunterladen. Falls sie gefeuert werden oder kündigen, bitten wir sie darum ihre lokalen Daten mit cleanup zu löschen. Vielen Dank, dass sie unser Tool verwenden. Ihr Cyberspionage Team")

    subparsers = parser.add_subparsers(title="Funktionen", dest="command", required=True)

    # Upload
    upload_parser = subparsers.add_parser("upload", help="Erstellt & lädt all ihre Public-RSA-Schlüssel an den Server hoch | Geben sie dafür bitte die Anzahl der Keys an")
    upload_parser.add_argument("--count", type=int, default=1,
                               help="Anzahl der zu generierenden Schlüssel (Standard: 1)")

    # Download
    download_parser = subparsers.add_parser("download", help="Lädt alle Dateien vom Server herunter")

    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Löscht RSA-Keys, lokale Datenbank & lokale Dateien")

    args = parser.parse_args()

    if args.command == "upload":
            upload(args.count)
    elif args.command == "download":
        print("download")
        #download()
    elif args.command == "cleanup":
        cleanup()


if __name__ == "__main__":
    main()
