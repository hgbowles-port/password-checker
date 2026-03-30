import sqlite3
import os
import hashlib
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "breach.db")


def sha1_hash(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def fetch_and_cache_prefix(prefix: str):
    """
    Query HIBP API for a given 5-char prefix and cache
    all returned hashes into the local DB.
    """
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url, headers={"User-Agent": "password-checker-project"})

    if response.status_code != 200:
        raise RuntimeError(f"HIBP API error: {response.status_code}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS breached_passwords (
            hash TEXT PRIMARY KEY,
            source TEXT,
            inserted_at TIMESTAMP
        )
    """)

    for line in response.text.splitlines():
        suffix, _ = line.split(":")
        full_hash = prefix + suffix
        try:
            cursor.execute("""
                INSERT INTO breached_passwords (hash, source, inserted_at)
                VALUES (?, 'HIBP', datetime('now'))
            """, (full_hash,))
        except sqlite3.IntegrityError:
            pass  # already cached

    conn.commit()
    conn.close()


def check_password_in_breach(password: str) -> bool:
    """
    Check password against local DB first, then fall back
    to HIBP API and cache the results.
    """
    hashed = sha1_hash(password)
    prefix = hashed[:5]

    # Check local DB first
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM breached_passwords WHERE hash = ? LIMIT 1",
            (hashed,)
        )
        result = cursor.fetchone()
        conn.close()

        if result is not None:
            return True

    # Not found locally — query HIBP and cache
    fetch_and_cache_prefix(prefix)

    # Now check again after caching
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM breached_passwords WHERE hash = ? LIMIT 1",
        (hashed,)
    )
    result = cursor.fetchone()
    conn.close()

    return result is not None