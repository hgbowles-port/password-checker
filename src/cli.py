import argparse
from predict import predict_password_strength
from breach_lookup import check_password_in_breach

def main():
    parser = argparse.ArgumentParser(
        description="Password Strength and Risk Analyzer"
    )

    parser.add_argument(
        "password",
        type=str,
        help="Password string to evaluate"
    )

    parser.add_argument(
        "--check-breach",
        action="store_true",
        help="Check password against breach database"
    )


    args = parser.parse_args()

    result = predict_password_strength(args.password)

    print("\n==============================")
    print(" Password Strength Evaluation ")
    print("==============================")
    print(f"Password:   {result['password']}")
    print(f"Strength:   {result['prediction']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Entropy:    {result['features']['entropy']}")
    print("=============================\n")

    if args.check_breach:
        breached = check_password_in_breach(args.password)

        if breached:
            print("⚠ Found in breach database")
        else:
            print("✓ Not found in breach database")


if __name__ == "__main__":
    main()