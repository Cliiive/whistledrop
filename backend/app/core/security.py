import hashlib
import secrets
import random
from faker import Faker

faker = Faker()

def generate_passphrase(length=4):
    seed_phrase = ' '.join(faker.words(nb=8))
    return seed_phrase

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