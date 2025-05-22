import hashlib
import secrets
import random
from faker import Faker

faker = Faker()


def generate_passphrase(length=6):
    """This function generates a passphrase using the EFF wordlist.
    It follows the EFF's diceware method, described here: https://www.eff.org/dice
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
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((seed_phrase + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"

def verify_passphrase(input_phrase, stored_hash):
    if not stored_hash or "$" not in stored_hash:
        return False

    salt, hash_value = stored_hash.split("$", 1)
    hash_obj = hashlib.sha256((input_phrase + salt).encode())
    return hash_obj.hexdigest() == hash_value