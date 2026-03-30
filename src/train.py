import os
import random
import string
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

from features import extract_features

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROCKYOU_PATH = os.path.join(BASE_DIR, "data", "rockyou.txt")
DICT_PATH = "/usr/share/dict/words"
LEET_SUBS = str.maketrans("aeiost", "@310$7")

"""
Loading RockYou weak passwords
"""

def load_weak_passwords(n_samples: int) -> list:
    passwords = []
    with open(ROCKYOU_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            pwd = line.strip()
            if pwd:
                passwords.append(pwd)
            if len(passwords) >= n_samples * 5:
                break

    random.shuffle(passwords)
    return passwords[:n_samples]

"""
Generating medium difficulty passwords
"""

def generate_medium_password() -> str:
    common = [
        "password", "admin", "welcome", "letmein", "monkey",
        "dragon", "master", "shadow", "sunshine", "princess",
        "football", "baseball", "superman", "batman", "iloveyou"
    ]
    patterns = [
        # leet substitutions on common word + number + symbol
        lambda: random.choice(common).capitalize().translate(LEET_SUBS) + str(random.randint(1, 999)) + random.choice("!@#$"),
        # leet substitutions only
        lambda: random.choice(common).translate(LEET_SUBS),
        # capitalized common word with padding
        lambda: random.choice(common).capitalize() + str(random.randint(10, 999)) + random.choice("!@#$"),
        # short but complex
        lambda: ''.join(random.choice(string.ascii_letters + string.digits + "!@#$") for _ in range(random.randint(5, 7))),
        # long but only lowercase
        lambda: ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(12, 16))),
        # two common words joined with symbol
        lambda: random.choice(common) + random.choice("!@#$") + random.choice(common),
        # common word with year
        lambda: random.choice(common).capitalize() + str(random.randint(1970, 2024)),
        # keyboard walks
        lambda: random.choice(["qwerty", "asdfgh", "zxcvbn", "qwerty123", "asdf1234"]) + random.choice("!@#$"),
        # long but single character class
        lambda: ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(15, 25))),
        # long with only letters, no symbols or digits
        lambda: ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(15, 20))),
        # repeated word pattern
        lambda: random.choice(common) * random.randint(2, 3),
    ]
    return random.choice(patterns)()

"""
Generating strong passwords
"""

def load_wordlist(min_length=3, max_length=8) -> list:
    """
    Load dictionary words within a length range to keep
    passphrases readable but not too long
    """
    words = []
    with open(DICT_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            word = line.strip().lower()
            if min_length <= len(word) <= max_length and word.isalpha():
                words.append(word)
    return words

WORDLIST = load_wordlist()

def generate_strong_password() -> str:
    separators = ["-", "_", ".", "!", "@", "#", ""]
    patterns = [
        # classic passphrase — 4 random words with separator
        lambda: random.choice(separators).join(
            random.choice(WORDLIST) for _ in range(4)
        ),
        # passphrase with numbers interspersed
        lambda: random.choice(separators).join(
            random.choice(WORDLIST) for _ in range(3)
        ) + str(random.randint(100, 9999)),
        # capitalized passphrase with symbol
        lambda: random.choice(separators).join(
            random.choice(WORDLIST).capitalize() for _ in range(3)
        ) + random.choice("!@#$%^&*"),
        # acronym style — first letters of words uppercased with padding
        lambda: ''.join(
            random.choice(WORDLIST)[0].upper() for _ in range(6)
        ) + str(random.randint(10, 999)) + random.choice("!@#$"),
        # purely random string — keep some of the original approach
        lambda: ''.join(
            random.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(random.randint(12, 20))
        ),
        # mixed — word + random chars + word
        lambda: random.choice(WORDLIST).capitalize() + ''.join(
            random.choice(string.ascii_letters + string.digits + "!@#$")
            for _ in range(4)
        ) + random.choice(WORDLIST).capitalize(),
    ]
    return random.choice(patterns)()

"""
Building the dataset
"""

def create_dataset(n_samples=10000):
    data = []
    per_class = n_samples // 3

    # Weak — from rockyou
    weak_passwords = load_weak_passwords(per_class)
    for pwd in weak_passwords:
        features = extract_features(pwd)
        features['label'] = 0  # weak
        data.append(features)

    # Medium — generated
    for _ in range(per_class):
        pwd = generate_medium_password()
        features = extract_features(pwd)
        features['label'] = 1  # medium
        data.append(features)

    # Strong — random
    for _ in range(per_class):
        pwd = generate_strong_password()
        features = extract_features(pwd)
        features['label'] = 2  # strong
        data.append(features)

    return pd.DataFrame(data)

"""
Training the Model
"""

def train():
    df = create_dataset(10000)

    X = df.drop("label", axis=1)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\nModel Evaluation:\n")
    print(classification_report(y_test, predictions, target_names=["WEAK", "MEDIUM", "STRONG"]))

    MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()