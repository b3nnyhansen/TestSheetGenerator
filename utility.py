import os
import hashlib
from datetime import datetime

def get_text_hash(original_text):
    return hashlib.sha256(original_text.encode('utf-8')).hexdigest()

def makedirs(dirpath, exist_ok=True):
    os.makedirs(dirpath, exist_ok=exist_ok)

def get_current_timestamp(format="%Y-%m-%d"):
    return datetime.now().strftime(format);