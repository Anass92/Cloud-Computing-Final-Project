#!/bin/bash

#Install Python Virtualenv

sudo apt-get -y update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv 

#Create directory

mkdir /home/ubuntu/gatekeeper_app && cd /home/ubuntu/gatekeeper_app 

#Create the virtual environment

python3 -m venv venv

#Activate the virtual environment

source venv/bin/activate

#Install Flask and other libraries

pip install Flask

pip install flask-restful

pip install ec2_metadata

#Create of a simple Flask app:

cat <<EOL > /home/ubuntu/gatekeeper_app/gatekeeper.py
from ec2_metadata import ec2_metadata
from flask import Flask
from flask import jsonify, request

import re
import requests
import json

Trusted_Host_IP = "__Trusted_Host_IP__"

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

EOL


#Install Gunicorn:

pip install gunicorn

#Run Gunicorn to show the message in the running script for the log management:

#gunicorn -b 0.0.0.0:8080 flask_app:app 

#pkill -f "gunicorn -b 0.0.0.0:8080 flask_app:app"

#Create a file system containing service instructions:

sudo cat <<EOL > /etc/systemd/system/flaskapp.service
[Unit]
Description=None
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/flaskapp
ExecStart=/home/ubuntu/flaskapp/venv/bin/gunicorn -b localhost:8080 flask_app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOL

#Enable the service:

sudo systemctl daemon-reload
sudo systemctl start flaskapp
sudo systemctl enable flaskapp

#Check the app is running using:

curl localhost:8080

#Install nginx:

sudo DEBIAN_FRONTEND=noninteractive apt-get -y install nginx

#Start the Nginx service :

sudo systemctl start nginx
sudo systemctl enable nginx

#Edition of /etc/nginx/sites-available/default in order to add  :

sudo cat <<EOL > /etc/nginx/sites-available/default

##
# You should look at the following URL's in order to grasp a solid understanding
# of Nginx configuration files in order to fully unleash the power of Nginx.
# https://www.nginx.com/resources/wiki/start/
# https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/
# https://wiki.debian.org/Nginx/DirectoryStructure
#
# In most cases, administrators will remove this file from sites-enabled/ and
# leave it as reference inside of sites-available where it will continue to be
# updated by the nginx packaging team.
#
# This file will automatically load configuration files provided by other
# applications, such as Drupal or Wordpress. These applications will be made
# available underneath a path with that package name, such as /drupal8.
#
# Please see /usr/share/doc/nginx-doc/examples/ for more detailed examples.
##

# Default server configuration
#
upstream flaskhrunninginstance {
    server 127.0.0.1:8080;
}
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        root /var/www/html;

        # Add index.php to the list if you are using PHP
        index index.html index.htm index.nginx-debian.html;

        server_name _;

        location / {
                # First attempt to serve request as file, then
                proxy_pass http://flaskhrunninginstance ;
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
        }


}


EOL

#Restart nginx:

sudo systemctl restart nginx

#Go to the public address of your instance to show the message of the Flask app