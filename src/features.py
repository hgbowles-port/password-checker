import math
import string

COMMON_WORDS = ["password", "admin", "login", "welcome", "qwerty", "monkey", "dragon", "letmein"]

LEET_MAP = {
    "@": "a",
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "$": "s",
    "!": "i",
}

def deleet(password: str) -> str:
    """
    Reverse leet-speak substitutions to recover the base word
    """
    result = password.lower()
    for symbol, letter in LEET_MAP.items():
        result = result.replace(symbol, letter)
    return result

def calculate_entropy(password: str) -> float:
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
    return {
        "length": len(password),
        "lowercase_count": sum(c.islower() for c in password),
        "uppercase_count": sum(c.isupper() for c in password),
        "digit_count": sum(c.isdigit() for c in password),
        "symbol_count": sum(c in string.punctuation for c in password)
    }

def repeated_char_ratio(password: str) -> float:
    if not password:
        return 0.0
    
    repeats = 0
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            repeats += 1
    return repeats / len(password)

def sequential_pattern_score(password: str) -> int:
    sequences = ["123", "abc", "qwerty", "password"]
    score = 0
    lower_pwd = password.lower()

    for seq in sequences:
        if seq in lower_pwd:
            score += 1
    return score

def contains_common_word(password: str) -> int:
    lower_pwd = password.lower()
    for word in COMMON_WORDS:
        if word in lower_pwd:
            return 1
    return 0

def contains_leet_common_word(password: str) -> int:
    """
    Checks if the password contains a common word after reversing
    leet-speak substitutions
    """
    deleeted = deleet(password)
    for word in COMMON_WORDS:
        if word in deleeted:
            return 1
    return 0

def leet_substitution_count(password: str) -> int:
    """
    Counts how many leet substitution characters are present,
    giving the model a sense of how much the password relies
    on symbol swapping
    """
    return sum(1 for c in password if c in LEET_MAP)

def complexity_ratio(password: str) -> float:
    """
    Ratio of character class variety to length.
    A long password using only one character class
    scores very low, penalizing passwords like
    'thisisaverylongpassword'
    """
    classes_used = sum([
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(c in string.punctuation for c in password)
    ])
    return round(classes_used / 4, 2)

def char_class_count(password: str) -> int:
    """
    Raw count of how many character classes are present (0-4).
    Gives the model a direct signal of variety.
    """
    return sum([
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(c in string.punctuation for c in password)
    ])

def extract_features(password: str) -> dict:
    stats = character_stats(password)
    stats["entropy"] = calculate_entropy(password)
    stats["repeat_ratio"] = repeated_char_ratio(password)
    stats["sequence_score"] = sequential_pattern_score(password)
    stats["common_word"] = contains_common_word(password)
    stats["leet_common_word"] = contains_leet_common_word(password)
    stats["leet_substitution_count"] = leet_substitution_count(password)
    stats["complexity_ratio"] = complexity_ratio(password)
    stats["char_class_count"] = char_class_count(password)
    return stats