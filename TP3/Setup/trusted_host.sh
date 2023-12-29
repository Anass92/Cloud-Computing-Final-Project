#!/bin/bash

#Install Python Virtualenv

sudo apt-get -y update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv 

#Create directory

mkdir /home/ubuntu/trusted_host_app && cd /home/ubuntu/trusted_host_app 

#Create the virtual environment

python3 -m venv venv

#Activate the virtual environment

source venv/bin/activate

#Install Flask and other libraries

pip install Flask

pip install flask-restful

pip install ec2_metadata

#Create of a simple Flask app:

cat <<EOL > /home/ubuntu/trusted_host_app/trusted_host.py

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



# Forwarding incoming and validated requests to Proxy

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



# Forwarding incoming and validated requests to Proxy

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



# Forwarding incoming and validated requests to Proxy

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

EOL

#Install Gunicorn:

pip install gunicorn

#Run Gunicorn to show the message in the running script for the log management:

#gunicorn -b 0.0.0.0:8081 flask_app:app 

#pkill -f "gunicorn -b 0.0.0.0:8081 flask_app:app"

#Create a file system containing service instructions:

sudo cat <<EOL > /etc/systemd/system/flaskapp.service
[Unit]
Description=None
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/flaskapp
ExecStart=/home/ubuntu/flaskapp/venv/bin/gunicorn -b localhost:8081 flask_app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOL

#Enable the service:

sudo systemctl daemon-reload
sudo systemctl start flaskapp
sudo systemctl enable flaskapp

#Check the app is running using:

curl localhost:8081

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
    server 127.0.0.1:8081;
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