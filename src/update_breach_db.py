import sqlite3
import os
import time
from datetime import datetime, timezone
import hashlib
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "breach.db")
ROCKYOU_PATH = os.path.join(BASE_DIR, "data", "rockyou.txt")


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
            pass

    conn.commit()
    conn.close()
    return new_entries


def sha1_hash(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def fetch_hibp_range(prefix: str):
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url, headers={"User-Agent": "password-checker-project"})

    if response.status_code != 200:
        raise RuntimeError(f"HIBP API error: {response.status_code}")

    return response.text.splitlines()


def load_prefixes_from_rockyou(n_passwords: int = 10000) -> set:
    """
    Read the top n passwords from rockyou.txt, compute their
    SHA1 prefix, and return a deduplicated set of prefixes.
    """
    prefixes = set()
    try:
        with open(ROCKYOU_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= n_passwords:
                    break
                pwd = line.strip()
                if pwd:
                    full_hash = sha1_hash(pwd)
                    prefixes.add(full_hash[:5])
    except FileNotFoundError:
        print(f"rockyou.txt not found at {ROCKYOU_PATH}")
        print("Falling back to common password prefixes only.")

    return prefixes


def seed_from_common_passwords() -> set:
    """
    Fallback set of prefixes derived from well known
    common passwords in case rockyou.txt is unavailable.
    """
    common = [
        "password", "123456", "qwerty", "letmein", "admin",
        "welcome", "monkey", "dragon", "master", "sunshine",
        "password1", "iloveyou", "princess", "football", "shadow"
    ]
    return {sha1_hash(p)[:5] for p in common}


def main():
    init_db()

    print("Loading prefixes from rockyou.txt...")
    prefixes = load_prefixes_from_rockyou(n_passwords=10000)

    # always include common password prefixes
    prefixes.update(seed_from_common_passwords())

    total_prefixes = len(prefixes)
    print(f"Fetching {total_prefixes} unique prefixes from HIBP...")
    print("This may take a few minutes.\n")

    total_inserted = 0
    failed = 0

    for i, prefix in enumerate(sorted(prefixes), 1):
        try:
            lines = fetch_hibp_range(prefix)
            hash_list = [prefix + line.split(":")[0] for line in lines]
            inserted = insert_hashes(hash_list)
            total_inserted += inserted

            # progress update every 100 prefixes
            if i % 100 == 0:
                print(f"  [{i}/{total_prefixes}] prefixes processed — {total_inserted:,} hashes inserted so far")

            # be respectful to the API — small delay between requests
            time.sleep(0.05)

        except RuntimeError as e:
            print(f"  Failed on prefix {prefix}: {e}")
            failed += 1
            time.sleep(1)  # longer pause on error
            continue

    print(f"\nBulk seeding complete.")
    print(f"Prefixes processed:  {total_prefixes - failed:,}")
    print(f"Prefixes failed:     {failed}")
    print(f"Total hashes inserted: {total_inserted:,}")


if __name__ == "__main__":
    main()