from flask import Flask, request, jsonify
import requests
import json
from functools import wraps
import pyodbc

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
def connect_to_sql_server():
    # Set your server name and database name here
    server_name = '38.66.76.155'  # e.g., 'localhost\SQLEXPRESS' or '192.168.1.5'
    database_name = 'CrushBank'
    username = 'cb_digitalocean'  # Use your username here
    password = '@19digitaL*oceaN$83'  # Use your password here

    # Connection string
    connection_string = f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={server_name};
    DATABASE={database_name};
    UID={username};
    PWD={password};
    Trusted_Connection=yes;
    """

    try:
        # Establishing the connection to the database
        conn = pyodbc.connect(connection_string)
        print("Connection successful!")

        # Example query: Selecting version of the SQL Server
        cursor = conn.cursor()
        cursor.execute("SELECT @@version;")
        row = cursor.fetchone()
        print(f"SQL Server version: {row[0]}")

        # Always close the connection
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")


# Call the function to connect to the SQL Server
connect_to_sql_server()


if __name__ == '__main__':
    app.run(debug=True)
