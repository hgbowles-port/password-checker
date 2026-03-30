import os
import joblib
import pandas as pd

from features import extract_features

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model file not found. Please train the model first.")

model = joblib.load(MODEL_PATH)

LABEL_MAP = {0: "WEAK", 1: "MEDIUM", 2: "STRONG"}

def predict_password_strength(password: str) -> dict:
    features = extract_features(password)
    df = pd.DataFrame([features])

    prediction = model.predict(df)[0]
    probabilities = model.predict_proba(df)[0]
    confidence = round(probabilities[prediction] * 100, 2)

    return {
        "password": password,
        "prediction": LABEL_MAP[prediction],
        "confidence": confidence,
        "features": features
    }

if __name__ == "__main__":
    test_pw = "P@ssw0rd123!"
    result = predict_password_strength(test_pw)

    print("\nPrediction Result:")
    print(f"Password: {result['password']}")
    print(f"Strength: {result['prediction']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Entropy: {result['features']['entropy']}")