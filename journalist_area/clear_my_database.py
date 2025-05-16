import sqlite3

def clear_table():
    conn = sqlite3.connect("meine_datenbank.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schluesselpaare;")
    conn.commit()
    conn.close()
