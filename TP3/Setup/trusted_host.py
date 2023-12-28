import re
import requests
import json

from flask import Flask
from flask import jsonify, request

from Setup_main import PROXY_IP


app = Flask(__name__)
# Disable json keys sorting
app.config["JSON_SORT_KEYS"] = False


# This is a Direct endpoint responsible for validating queries before forwarding them to the trusted host. 
# If a query fails to match the predefined rules, the request is terminated, and an "Access denied" message is returned.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/direct", methods=["POST"])
def save():
    request_data = request.get_json()
    try:
            url="http://{}:{}/{}".format(PROXY_IP, 8082,'direct')
            # method post pour transmettre la requête
            proxy_response = requests.post(url, json=request_data) 
            return json.loads(proxy_response.content)
        
    except Exception as e:
        return jsonify(message=e)



# This is a Direct endpoint responsible for validating queries before forwarding them to the trusted host. 
# If a query fails to match the predefined rules, the request is terminated, and an "Access denied" message is returned.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/direct", methods=["GET"])
def direct_call():
    request_data = request.get_json()
    try:
            url="http://{}:{}/{}".format(PROXY_IP, 8082,'direct')
            # method post pour transmettre la requête
            proxy_response = requests.post(url, json=request_data) 
            return json.loads(proxy_response.content)
        
    except Exception as e:
        return jsonify(message=e)



# This is a Random endpoint responsible for validating queries before forwarding them to the trusted host. 
# If a query fails to match the predefined rules, the request is terminated, and an "Access denied" message is returned.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/random", methods=["GET"])
def random_call():
    request_data = request.get_json()
    try:
            url="http://{}:{}/{}".format(PROXY_IP, 8082,'random')
            # method post pour transmettre la requête
            proxy_response = requests.post(url, json=request_data) 
            return json.loads(proxy_response.content)
        
    except Exception as e:
        return jsonify(message=e)



# This is a Customized endpoint responsible for validating queries before forwarding them to the trusted host. 
# If a query fails to match the predefined rules, the request is terminated, and an "Access denied" message is returned.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/custom", methods=["GET"])
def custom_call():
    request_data = request.get_json()
    try:
            url="http://{}:{}/{}".format(PROXY_IP, 8082,'custom')
            # method post pour transmettre la requête
            proxy_response = requests.post(url, json=request_data) 
            return json.loads(proxy_response.content)
        
    except Exception as e:
        return jsonify(message=e)




if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8081)