from flask import Flask, request, jsonify, render_template
import requests
import json
from functools import wraps
import pymssql
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib

app = Flask(__name__)

# Error Handling
@app.errorhandler(404)
def not_found(error):
    return jsonify(message='Resource not found'), 404
@app.errorhandler(500)
def server_error(error):
    return jsonify(message='Internal server error'), 500

# Static key and IV
ENCRYPTION_KEY = "ef0279dd07e4563b509f340337f92fe92237ca1f84f721dc"
ENCRYPTION_IV = "8407fc663dbf02f19b48bdc5ce9ba7ed8f4ce324503dd5b4"

# AES Key size and IV size
KeySize = 32
InitialVectorSize = 16

def make_key():
    """Generates the AES key by hashing and adjusting its length."""
    # SHA-512 hash of the base encryption key
    sha512 = hashlib.sha512()
    sha512.update(base64.b64decode(ENCRYPTION_KEY))
    key = sha512.digest()

    # Truncate or pad the key to fit 32 bytes (AES-256)
    return key[:KeySize]


def make_iv():
    """Generates the IV by ensuring its length is 16 bytes."""
    iv = base64.b64decode(ENCRYPTION_IV.encode('utf-8'))
    return iv[:InitialVectorSize]


def encrypt(src):
    """Encrypts a plaintext string using AES/CBC/PKCS7Padding."""
    try:
        key = make_key()
        iv = make_iv()

        # Create AES cipher in CBC mode with PKCS7 padding
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Pad the plaintext to a multiple of 16 bytes
        padded_src = pad(src.encode('utf-8'), AES.block_size)

        # Encrypt and encode the result as base64
        encrypted = cipher.encrypt(padded_src)
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        raise RuntimeError(e)

def require_apikey(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        json_data = request.get_json()
        clientid = json_data.get('clientid')
        plaintext = clientid + api_key
        encrypted_text = encrypt(plaintext)
        #print(clientid)
        #print(plaintext)
        #print(encrypted_text)
        if api_key and encrypted_text[:105] == fetch_secret(clientid)[:105]:
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "Invalid or missing API key"}), 403

    return decorated_function

def require_apikey_halo(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        json_data = request.get_json()
        ###clientid = json_data.get('clientid')
        webhookid = json_data.get('webhook_id')
        #plaintext = clientid + api_key
        #encrypted_text = encrypt(plaintext)
        print(webhookid)
        print(api_key)
        ###print(encrypted_text)
        if api_key: #and encrypted_text[:105] == fetch_secret(clientid)[:105]:
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "Invalid or missing API key"}), 403

    return decorated_function


def fetch_secret(company_id):
    # Connect to the database# Replace these with your database details
    server = '38.66.76.155'  # e.g., 'yourserver.database.windows.net'
    username = 'cb_digitalocean'
    password = '@19digitaL*oceaN$83'
    database = 'CrushBank'

    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    print("Connection successful!")
    #cursor = conn.cursor(as_dict=True)  # Use `as_dict=True` to get results as dictionaries
    cursor = conn.cursor()

    # Execute a query
    cursor.execute('select CompanySecret from vwSecretLookup where CompanyUuId = %s', (company_id,))
    

    # Fetch all results
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    print("Connection closed.")

    if result:
        column_value = result[0]  # Access the first (and only) column value
        return column_value
    else:
        return "No results found."
    #return results


@app.route('/v1/analyze', methods=['POST'])
@require_apikey
def process_data():
    # Get input data from the user
    #user_input = request.json.get('input')
    json_data = request.get_json()
    model = json_data.get('model')
    text = json_data.get('text')
    clientid = json_data.get('clientid')


    # Send the input to another API
    api_url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/v1/analyze?version=2022-04-07"
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic YXBpa2V5Om1sZXJUTHNXTmYxYWJoajhoWWl2RWxrRUxlUHJ1Z1R6cmZLWVFwZGVRNWc3'
    }

    payload = json.dumps({
        "text": text,
        "features": {
            "classifications": {
                "model": model
                }
            }
        })
    response = requests.request("POST", api_url, headers=headers, data=payload)

    #response = requests.post(api_url) #, json={'data': user_input})

    # Process the response from the other API
    result = response.json()

    # Return the result to the user
    return jsonify(result)

@app.route('/test')
def index():
    return "Hello World!"

@app.route('/v2/classification', methods=['POST'])  #Halo ticket classifier
@require_apikey_halo
def halo_classification():
    # Get input data from the user
    #user_input = request.json.get('input')
    json_data = request.get_json()
    model = json_data.get('model')
    text = json_data.get('text')
    clientid = json_data.get('clientid')
    mode = json_data.get('mode')

    # Send the input to another API
    api_url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/v1/analyze?version=2022-04-07"
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic YXBpa2V5Om1sZXJUTHNXTmYxYWJoajhoWWl2RWxrRUxlUHJ1Z1R6cmZLWVFwZGVRNWc3'
    }

    payload = json.dumps({
        "text": text,
        "features": {
            "classifications": {
                "model": model
                }
            }
        })
    response = requests.request("POST", api_url, headers=headers, data=payload)

    #response = requests.post(api_url) #, json={'data': user_input})

    # Process the response from the other API
    result = response.json()

    # Return the result to the user
    return jsonify(result)
    

if __name__ == '__main__':
    app.run(debug=True)
