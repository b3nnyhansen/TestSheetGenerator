import hashlib

def get_text_hash(original_text):
    return hashlib.sha256(original_text.encode('utf-8')).hexdigest()