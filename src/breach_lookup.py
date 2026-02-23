import sqlite3
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "breach.db")


def sha1_hash(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def check_password_in_breach(password: str) -> bool:
    hashed = sha1_hash(password)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM breached_passwords WHERE hash = ? LIMIT 1",
        (hashed,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None
