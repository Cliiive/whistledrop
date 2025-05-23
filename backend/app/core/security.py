"""
Security utilities for the application.
Provides functions for passphrase generation and verification.
"""
import hashlib
import secrets
import random
from faker import Faker

faker = Faker()


def generate_passphrase(length=6):
    """
    Generate a secure passphrase using the EFF wordlist.
    
    Uses the EFF's diceware method (https://www.eff.org/dice) to create
    a memorable but secure passphrase by combining random words.
    
    Args:
        length: Number of words in the passphrase
        
    Returns:
        Space-separated string of random words
    """
    # Use eff wordlist to generate a passphrase
    wordlist_path = "storage/wordlist/eff_large_wordlist.txt"

    # Load the wordlist from the file
    wordlist = {}
    with open(wordlist_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 2:
                key, word = parts[0], parts[1]
                wordlist[key] = word

    words = []

    for _ in range(length):
        # roll 5 dice using secrets
        dice = [(secrets.randbelow(6) + 1) for _ in range(5)]
        # convert dice rolls to lookup key
        dice_key = ''.join(map(str, dice))
        # lookup word in wordlist
        if dice_key in wordlist:
            words.append(wordlist[dice_key])

    pass_phrase = ' '.join(words)
    return pass_phrase

def hash_passphrase(seed_phrase):
    """
    Create a secure hash of a passphrase.
    
    Args:
        seed_phrase: Original passphrase to hash
        
    Returns:
        String in format "salt$hash"
    """
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((seed_phrase + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"

def verify_passphrase(input_phrase, stored_hash):
    """
    Verify a passphrase against a stored hash.
    
    Args:
        input_phrase: Passphrase to verify
        stored_hash: Previously hashed passphrase in format "salt$hash"
        
    Returns:
        Boolean indicating if the passphrase matches
    """
    if not stored_hash or "$" not in stored_hash:
        return False

    salt, hash_value = stored_hash.split("$", 1)
    hash_obj = hashlib.sha256((input_phrase + salt).encode())
    return hash_obj.hexdigest() == hash_value
