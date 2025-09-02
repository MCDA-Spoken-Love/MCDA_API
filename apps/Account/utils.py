import hashlib


def email_to_code(email):
    # Hash the email using SHA-256
    hash_object = hashlib.sha256(email.encode())
    digest = hash_object.digest()

    # Convert hash bytes to an integer
    hash_int = int.from_bytes(digest, 'big')

    # Convert the integer to base36 (0-9 + A-Z)
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base36 = ''
    while hash_int > 0:
        hash_int, i = divmod(hash_int, 36)
        base36 = alphabet[i] + base36

    # Pad or truncate to ensure 6 characters
    base36 = base36.zfill(6)  # ensure at least 6 chars
    return base36[:6].upper()
