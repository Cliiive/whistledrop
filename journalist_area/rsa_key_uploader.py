#Bib. dotenv
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()  # .env-Datei laden

datenbankpfad = os.getenv("DATABASE_URL")
#print("Datenbankpfad:", datenbankpfad)



def get_public_keys():
    conn = sqlite3.connect("meine_datenbank.db")
    cursor = conn.cursor()

    # Nur die gewünschte Spalte abfragen
    cursor.execute("SELECT public_key FROM schluesselpaare")

    # Alle Zeilen holen (jede ist ein Tupel mit einem Element)
    rows = cursor.fetchall()

    # In eine Liste extrahieren
    public_keys = [row[0] for row in rows]

    conn.close()
    return public_keys

# Beispiel-Aufruf
keys = get_public_keys()
print(keys)