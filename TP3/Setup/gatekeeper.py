import re
import requests
import json

from flask import Flask
from flask import jsonify, request

from Setup_main import Trusted_Host_IP


app = Flask(__name__)
# Disable json keys sorting
app.config["JSON_SORT_KEYS"] = False


# Regex to match restricted queries. Only select and insert operations from/into actor table are authorized

select_validator = re.compile(r"(?i)(^SELECT \* FROM film .)")
insert_validator = re.compile(r"(?i)(^INSERT INTO film ?\((first_name,\s{0,}last_name)\) VALUES)")


# This is a Direct endpoint responsible for validating queries before forwarding them to the trusted host. 
# If a query fails to match the predefined rules, the request is terminated, and an "Access denied" message is returned.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/direct", methods=["POST"])
def add():
    request_data = request.get_json()
    if validate("insert", request_data["query"]):
        try:
            url="http://{}:{}/{}".format(Trusted_Host_IP, 8081,'direct')
            # La methode post pour transmettre la requête
            trusted_host_response = requests.post(url, json=request_data) 
            return json.loads(trusted_host_response.content)
        
        except Exception as e:
            return jsonify(message=e)
    else:
        response = "Warning: The gatekeeper has denied access"
        return jsonify(message=response), 403



# This is a Direct endpoint responsible for validating queries before forwarding them to the trusted host. 
# If a query fails to match the predefined rules, the request is terminated, and an "Access denied" message is returned.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/direct", methods=["GET"])
def direct_read():
    request_data = request.get_json()
    if validate("select", request_data["query"]):
        try:
            url="http://{}:{}/{}".format(Trusted_Host_IP, 8081,'direct')
            # method post pour transmettre la requête
            trusted_host_response = requests.get(url, json=request_data) 
            return json.loads(trusted_host_response.content)
        
        except Exception as e:
            return jsonify(message=e)
    else:
        response = "Warning: The gatekeeper has denied access"
        return jsonify(message=response), 403


# This is a Customized endpoint responsible for validating queries before forwarding them to the trusted host. 
# If a query fails to match the predefined rules, the request is terminated, and an "Access denied" message is returned.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/custom", methods=["GET"])
def custom_read():
    request_data = request.get_json()
    if validate("select", request_data["query"]):
        try:
            url="http://{}:{}/{}".format(Trusted_Host_IP, 8081,'custom')
            # method post pour transmettre la requête
            trusted_host_response = requests.get(url, json=request_data) 
            return json.loads(trusted_host_response.content)
        
        except Exception as e:
            return jsonify(message=e)
    else:
        response = "Warning: The gatekeeper has denied access"
        return jsonify(message=response), 403




# This is a Random endpoint responsible for validating queries before forwarding them to the trusted host. 
# If a query fails to match the predefined rules, the request is terminated, and an "Access denied" message is returned.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/random", methods=["GET"])
def random_read():
    request_data = request.get_json()
    if validate("select", request_data["query"]):
        try:
            url="http://{}:{}/{}".format(Trusted_Host_IP, 8081,'random')
            # method post pour transmettre la requête
            trusted_host_response = requests.get(url, json=request_data) 
            return json.loads(trusted_host_response.content)
        
        except Exception as e:
            return jsonify(message=e)
    else:
        response = "Warning: The gatekeeper has denied access"
        return jsonify(message=response), 403



# This is a Delete endpoint designed to enforce the restriction that only select and insert operations are permitted. 
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/delete", methods=["DELETE"])
def delete():
    request_data = request.get_json()
    if validate("delete", request_data["query"]):
        print("Do Nothing")
    else:
        response = "Warning: The gatekeeper has denied access."
        return jsonify(message=response), 403



# This function employs regular expressions to validate whether a query is permissible for transmission to trusted host. 
# If the query is deemed unauthorized, the request is halted, and an "Access denied" message is generated
# Parameter: JSON data containing the query.
# Return: Output of the query.

def validate(mode, query):
    if mode == "select":
        return bool(select_validator.match(" ".join(query.split())))
    if mode == "insert":
        return bool(insert_validator.match(" ".join(query.split())))
    return False


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)