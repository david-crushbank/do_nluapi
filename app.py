from flask import Flask, request, jsonify, render_template
import requests
import json
from functools import wraps
import pymssql

app = Flask(__name__)

# Error Handling
@app.errorhandler(404)
def not_found(error):
    return jsonify(message='Resource not found'), 404
@app.errorhandler(500)
def server_error(error):
    return jsonify(message='Internal server error'), 500

# Store API key securely
VALID_API_KEY = "MzE2LWJiMzllYTQyLWI1MGUtNGRlZS1hNDFhLWQ2ZDBiMjYxOWQwMQ=="
VALID_API_KEY2 = "NTYwLTIzMmJkZTU0LTk2OTMtNGUyYy1iMzFmLWVlMTg0NmY5ZTE5Zg=="

def require_apikey(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key and api_key == VALID_API_KEY:
            return f(*args, **kwargs)
        else:
            if api_key and api_key == VALID_API_KEY2:
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Invalid or missing API key"}), 403

    return decorated_function

def test_apikey(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key and api_key == VALID_API_KEY:
            return f(*args, **kwargs)
        else:
            if api_key and api_key == VALID_API_KEY2:
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Invalid or missing API key"}), 403

    return decorated_function

def fetch_secret():
    # Connect to the database# Replace these with your database details
    server = '38.66.76.155'  # e.g., 'yourserver.database.windows.net'
    username = 'cb_digitalocean'
    password = '@19digitaL*oceaN$83'
    database = 'CrushBank'

    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    print("Connection successful!")
    cursor = conn.cursor(as_dict=True)  # Use `as_dict=True` to get results as dictionaries

    # Execute a query
    cursor.execute("select companyID from company where CompanyUuId = 'ce299ec9-0a9e-4fd9-bf80-00c542c36d8c'")

    # Fetch all results
    results = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    print("Connection closed.")

    return results

def fetch_data():
    # Connect to the database# Replace these with your database details
    server = '38.66.76.155'  # e.g., 'yourserver.database.windows.net'
    username = 'cb_digitalocean'
    password = '@19digitaL*oceaN$83'
    database = 'CrushBank'

    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    print("Connection successful!")
    cursor = conn.cursor(as_dict=True)  # Use `as_dict=True` to get results as dictionaries

    # Execute a query
    cursor.execute("SELECT TOP 10 * FROM Company")

    # Fetch all results
    results = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    print("Connection closed.")

    return results


@app.route('/v1/analyze', methods=['POST'])
@require_apikey
def process_data():
    # Get input data from the user
    user_input = request.json.get('input')
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
    # Fetch data from the database
    data = fetch_secret()

    # Pass data to the HTML template
    #return data
    companyid = data.companyID
    return companyid
    #return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
