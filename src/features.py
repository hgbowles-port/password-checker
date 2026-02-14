import math
import string

COMMON_WORDS = ["password", "admin", "login", "welcome", "qwerty"]

def calculate_entropy(password: str) -> float:
    """
    Estimate Shannon entropy of a given password
    """

    if not password:
        return 0.0
    
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in string.punctuation for c in password):
        pool += len(string.punctuation)

    entropy = len(password) * math.log2(pool) if pool > 0 else 0
    return round(entropy, 2)

def character_stats(password: str) -> dict:
    """
    Return compositional stats of the password
    """

    return{
        "length": len(password),
        "lowercase_count": sum(c.islower() for c in password),
        "uppercase_count": sum(c.isupper() for c in password),
        "digit_count": sum(c.isdigit() for c in password),
        "symbol_count": sum(c in string.punctuation for c in password)
    }

def repeated_char_ratio(password: str) -> float:
    """
    Calculates the ratio of repeated characters in a given password
    """
    if not password:
        return 0.0
    
    repeats = 0
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            repeats += 1
    return repeats / len(password)

def sequential_pattern_score(password: str) -> int:
    """
    checks for common sequences of characters in a password
    """

    sequences = ["123", "abc", "qwerty", "password"]
    score = 0
    lower_pwd = password.lower()

    for seq in sequences:
        if seq in lower_pwd:
            score += 1
    return score

def contains_common_word(password: str) -> int:
    """
    Checks if password contains entries from COMMON_WORDS
    """

    lower_pwd = password.lower()
    for word in COMMON_WORDS:
        if word in lower_pwd:
            return 1
    return 0

def extract_features(password: str) -> dict:
    """
    Put it all together
    """
    stats = character_stats(password)
    stats["entropy"] = calculate_entropy(password)
    stats["repeat_ratio"] = repeated_char_ratio(password)
    stats["sequence_score"] = sequential_pattern_score(password)
    stats["common_word"] = contains_common_word(password)
    return stats
