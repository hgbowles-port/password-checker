import os
import sqlite3
import joblib
import pandas as pd
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from features import extract_features
from predict import predict_password_strength
from breach_lookup import check_password_in_breach

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")
DB_PATH = os.path.join(BASE_DIR, "breach.db")

LABEL_MAP = {0: "WEAK", 1: "MEDIUM", 2: "STRONG"}

TEST_PASSWORDS = [
    # Should be WEAK
    ("password123",     "WEAK"),
    ("123456",          "WEAK"),
    ("qwerty",          "WEAK"),
    ("letmein",         "WEAK"),
    ("admin",           "WEAK"),
    # Should be MEDIUM
    ("P@ssw0rd123!",    "MEDIUM"),
    ("Adm1n!99",        "MEDIUM"),
    ("Welcome1!",       "MEDIUM"),
    ("Dr@g0n55",        "MEDIUM"),
    ("thisisaverylongpassword", "MEDIUM"),
    # Should be STRONG
    ("correct-horse-battery-staple", "STRONG"),
    ("xK9#mQ2$vL7!nP4@",            "STRONG"),
    ("maple-river-stone-7!",         "STRONG"),
    ("Tz#9wqL!mP2@kXv",             "STRONG"),
    ("golden-brick-sunset-42!",      "STRONG"),
]


def section(title: str):
    print(f"\n{'=' * 40}")
    print(f" {title}")
    print(f"{'=' * 40}")


def evaluate_model_performance():
    section("Model Performance Metrics")

    model = joblib.load(MODEL_PATH)
    correct = 0
    results = {"WEAK": {"correct": 0, "total": 0},
               "MEDIUM": {"correct": 0, "total": 0},
               "STRONG": {"correct": 0, "total": 0}}

    for password, expected in TEST_PASSWORDS:
        result = predict_password_strength(password)
        predicted = result["prediction"]
        is_correct = predicted == expected

        results[expected]["total"] += 1
        if is_correct:
            results[expected]["correct"] += 1
            correct += 1

    print(f"\n{'Class':<10} {'Correct':<10} {'Total':<10} {'Accuracy':<10}")
    print("-" * 40)
    for label, stats in results.items():
        acc = round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
        print(f"{label:<10} {stats['correct']:<10} {stats['total']:<10} {acc}%")

    overall = round(correct / len(TEST_PASSWORDS) * 100, 1)
    print(f"\nOverall accuracy on test set: {overall}%")


def evaluate_feature_importance():
    section("Feature Importance Analysis")

    model = joblib.load(MODEL_PATH)
    sample_features = extract_features("example")
    feature_names = list(sample_features.keys())

    importances = model.feature_importances_
    paired = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)

    print(f"\n{'Feature':<30} {'Importance':<10}")
    print("-" * 40)
    for feature, importance in paired:
        bar = "█" * int(importance * 100)
        print(f"{feature:<30} {round(importance, 4):<10} {bar}")


def evaluate_password_analysis():
    section("Password Analysis Report")

    print(f"\n{'Password':<35} {'Predicted':<10} {'Expected':<10} {'Confidence':<12} {'Match'}")
    print("-" * 80)

    for password, expected in TEST_PASSWORDS:
        result = predict_password_strength(password)
        predicted = result["prediction"]
        confidence = result["confidence"]
        match = "✓" if predicted == expected else "✗"
        # truncate long passwords for display
        display_pwd = password if len(password) <= 32 else password[:29] + "..."
        print(f"{display_pwd:<35} {predicted:<10} {expected:<10} {confidence:<12} {match}")


def evaluate_breach_db():
    section("Breach Database Statistics")

    if not os.path.exists(DB_PATH):
        print("\nNo breach database found. Run update_breach_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM breached_passwords")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(inserted_at), MAX(inserted_at) FROM breached_passwords")
    oldest, newest = cursor.fetchone()

    cursor.execute("SELECT source, COUNT(*) FROM breached_passwords GROUP BY source")
    sources = cursor.fetchall()

    conn.close()

    print(f"\nTotal cached hashes:  {total:,}")
    print(f"First entry:          {oldest}")
    print(f"Latest entry:         {newest}")
    print(f"\n{'Source':<20} {'Count':<10}")
    print("-" * 30)
    for source, count in sources:
        print(f"{source:<20} {count:,}")


def main():
    print("\n" + "=" * 40)
    print(" Password Checker — Full Evaluation")
    print("=" * 40)

    evaluate_model_performance()
    evaluate_feature_importance()
    evaluate_password_analysis()
    evaluate_breach_db()

    print("\n" + "=" * 40)
    print(" Evaluation Complete")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    main()