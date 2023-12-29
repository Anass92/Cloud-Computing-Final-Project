import re
import requests
import json

from flask import Flask
from flask import jsonify, request


PROXY_IP = "__PROXY_IP__"


app = Flask(__name__)
# Disable json keys sorting
app.config["JSON_SORT_KEYS"] = False


# Forwarding incoming and validated requests to Proxy

@app.route("/direct", methods=["POST"])
def send_to_proxy_1():
    request_data = request.get_json()
    try:
            url="http://{}:{}/{}".format(PROXY_IP, 8082,'direct')
            # method post pour transmettre la requête
            proxy_response = requests.post(url, json=request_data) 
            return json.loads(proxy_response.content)
        
    except Exception as e:
        return jsonify(message=e)



# Forwarding incoming and validated requests to Proxy.

@app.route("/direct", methods=["GET"])
def send_to_proxy_2():
    request_data = request.get_json()
    try:
            url="http://{}:{}/{}".format(PROXY_IP, 8082,'direct')
            # method post pour transmettre la requête
            proxy_response = requests.get(url, json=request_data) 
            return json.loads(proxy_response.content)
        
    except Exception as e:
        return jsonify(message=e)



# Forwarding incoming and validated requests to Proxy.

@app.route("/custom", methods=["GET"])
def send_to_proxy_4():
    request_data = request.get_json()
    try:
            url="http://{}:{}/{}".format(PROXY_IP, 8082,'custom')
            # method post pour transmettre la requête
            proxy_response = requests.get(url, json=request_data) 
            return json.loads(proxy_response.content)
        
    except Exception as e:
        return jsonify(message=e)



# Forwarding incoming and validated requests to Proxy.

@app.route("/random", methods=["GET"])
def send_to_proxy_3():
    request_data = request.get_json()
    try:
            url="http://{}:{}/{}".format(PROXY_IP, 8082,'random')
            # method post pour transmettre la requête
            proxy_response = requests.get(url, json=request_data) 
            return json.loads(proxy_response.content)
        
    except Exception as e:
        return jsonify(message=e)



if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8081)