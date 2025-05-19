import os
import shutil  # <- wird für Ordner gebraucht

def clear_everything():
    local_database_path = "../meine_datenbank.db"
    public_keys_path = "./temp_keys"

    if os.path.exists(local_database_path):
        os.remove(local_database_path)
        print(f" {local_database_path} wurde gelöscht.")
    else:
        print(f" {local_database_path} existiert nicht.")

    if os.path.isdir(public_keys_path):
        shutil.rmtree(public_keys_path)
        print(f"{public_keys_path} (Ordner) wurde gelöscht.")
    else:
        print(f" {public_keys_path} existiert nicht.")

