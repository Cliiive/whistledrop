import secrets

def generate_auth_secret():
    """
    Generate a secure JWT secret key.

    Uses the secrets module to create a random URL-safe base64-encoded string.

    Returns:
        A string representing the JWT secret key.
    """
    jwt_secret = secrets.token_hex(32)
    return jwt_secret