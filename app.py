from flask import Flask, request, jsonify
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
    # Replace these with your database details
    server = '38.66.76.155'  # e.g., 'yourserver.database.windows.net'
    username = 'cb_digitalocean'
    password = '@19digitaL*oceaN$83'
    database = 'CrushBank'

    try:
        # Establish a connection to the remote SQL Server
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        print("Connection successful!")

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Example query
        cursor.execute("SELECT TOP 10 * FROM Company")

        # Fetch and display results
        for row in cursor:
            return row

        # Close the cursor and connection
        cursor.close()
        conn.close()
        print("Connection closed.")

    except pymssql.Error as e:
        print("Error connecting to the SQL Server:", e)

# Call the function to connect to the SQL Server
connect_to_sql_server()


if __name__ == '__main__':
    app.run(debug=True)
