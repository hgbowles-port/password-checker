import sqlite3
import os
from datetime import datetime, timezone

import hashlib
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "breach.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS breached_passwords (
            hash TEXT PRIMARY KEY,
            source TEXT,
            inserted_at TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def insert_hashes(hash_list, source="HIBP"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_entries = 0

    for h in hash_list:
        try:
            cursor.execute("""
                INSERT INTO breached_passwords (hash, source, inserted_at)
                VALUES (?, ?, ?)
            """, (h, source, datetime.now(timezone.utc)))
            new_entries += 1
        except sqlite3.IntegrityError:
            # repeated hash case
            pass

    conn.commit()
    conn.close()

    return new_entries


def sha1_hash(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()

def fetch_hibp_range(prefix: str):
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError("Error fetching from HIBP API")
    
    return response.text.splitlines()

def main():
    init_db()
    
    sample_password = "password123"
    full_hash = sha1_hash(sample_password)
    prefix = full_hash[:5]
    suffix = full_hash[5:]

    results = fetch_hibp_range(prefix)

    hash_list = []

    for line in results:
        hash_suffix, count = line.split(":")
        hash_list.append(prefix + hash_suffix)

    inserted = insert_hashes(hash_list)
    print(f"Inserted {inserted} new hashes into database.")

if __name__ == "__main__":
    main()