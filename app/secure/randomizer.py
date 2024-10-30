# key generator function 
import hashlib
import secrets
import string
from flask import current_app as app

def generate_key(length=128):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

#generate token based on data, key and key2 for session
def generate_token(data, key, key2):
    combined_data = str(data) + app.config['SECRET_KEY'] + key + key2
    hashed_data = hashlib.sha256(combined_data.encode()).hexdigest()
    return hashed_data

#verify the token and return true
def check_token(token, data, key, key2):
    expected_token = generate_token(data, key, key2)
    return token == expected_token

def randomChar(length):
    rand = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(length))
    return rand
