import argparse
from predict import predict_password_strength

def main():
    parser = argparse.ArgumentParser(
        description="Password Strength and Risk Analyzer"
    )

    parser.add_argument(
        "password",
        type=str,
        help="Password string to evaluate"
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

if __name__ == "__main__":
    main()