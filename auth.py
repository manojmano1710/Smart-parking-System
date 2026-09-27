import hashlib, secrets
TOKENS = {}
def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    return salt + '$' + hashlib.sha256((salt + password).encode()).hexdigest()
def verify_password(password, stored):
    try:
        salt, digest = stored.split('$', 1)
        return secrets.compare_digest(hashlib.sha256((salt + password).encode()).hexdigest(), digest)
    except Exception: return False
def create_token(username):
    token = secrets.token_urlsafe(32); TOKENS[token] = username; return token
def get_username_from_token(token): return TOKENS.get(token) if token else None
def token_matches_user(token, username): return get_username_from_token(token) == username
