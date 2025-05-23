import os
import shutil  # <- needed for directories

def clear_everything():
    local_database_path = "../meine_datenbank.db"
    public_keys_path = "./temp_keys"
    local_files_path = "../downloads"
    decrypted_files_path = "../decrypted_files"

    if os.path.exists(local_database_path):
        os.remove(local_database_path)
        print(f" {local_database_path} has been deleted.")
    else:
        print(f" {local_database_path} does not exist.")

    if os.path.isdir(public_keys_path):
        shutil.rmtree(public_keys_path)
        print(f"{public_keys_path} (directory) has been deleted.")
    else:
        print(f" {public_keys_path} does not exist.")

    if os.path.isdir(local_files_path):
        shutil.rmtree(local_files_path)
        print(f"{local_files_path} (directory) has been deleted.")
    else:
        print(f" {local_files_path} does not exist.")

    if os.path.isdir(decrypted_files_path):
        shutil.rmtree(decrypted_files_path)
        print(f"{decrypted_files_path} (directory) has been deleted.")
    else:
        print(f" {decrypted_files_path} does not exist.")
