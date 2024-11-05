from flask import Flask, request, jsonify
import requests
import json
from functools import wraps

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
def test_page():
    return '''
<html>
<head>
    <title>Simple Menu</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        ul {
            list-style-type: none;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #333;
        }
        li {
            float: left;
        }
        li a {
            display: block;
            color: white;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none;
        }
        li a:hover {
            background-color: #111;
        }
    </style>
</head>
<body>
    <ul>
        <li><a href="#choice1">Choice 1</a></li>
        <li><a href="#choice2">Choice 2</a></li>
        <li><a href="#choice3">Choice 3</a></li>
        <li><a href="#choice4">Choice 4</a></li>
        <li><a href="#choice5">Choice 5</a></li>
    </ul>
</body>
</html>
        '''


if __name__ == '__main__':
    app.run(debug=True)
