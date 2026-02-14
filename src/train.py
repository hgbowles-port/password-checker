import os
import random
import string
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

from features import extract_features

"""
Generating Synthetic Data
"""

def generate_weak_password():
    common = ["password", "123456", "qwerty", "letmein", "admin"]
    patterns = [
        lambda: random.choice(common),
        lambda: random.choice(common) + "123",
        lambda: random.choice(common).capitalize() + "!",
        lambda: random.choice(common) + str(random.randint(0,99))
    ]
    return random.choice(patterns)()

def generate_strong_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def create_dataset(n_samples=1000):
    data = []

    for _ in range(n_samples // 2): ## populating weak data
        pwd = generate_weak_password()
        features = extract_features(pwd)
        features['label'] = 0 ## weak
        data.append(features)

    for _ in range(n_samples // 2): ## populating strong data
        pwd = generate_strong_password()
        features = extract_features(pwd)
        features['label'] = 1 ## strong
        data.append(features)
    
    return pd.DataFrame(data)

"""
Training the Model
"""

def train():
    df = create_dataset(2000)

    X = df.drop("label", axis=1)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\nModel Evaluation:\n")
    print(classification_report(y_test, predictions))

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()