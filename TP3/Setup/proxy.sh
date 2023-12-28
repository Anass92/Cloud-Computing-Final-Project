#!/bin/bash

#Install Python Virtualenv

sudo apt-get -y update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv 

#Create directory

mkdir /home/ubuntu/proxy_app && cd /home/ubuntu/proxy_app 

#Create the virtual environment

python3 -m venv venv

#Activate the virtual environment

source venv/bin/activate

#Install Flask and other libraries

pip install Flask

pip install flask-restful

pip install ec2_metadata

pip install mysql-connector-python-rf

pip install pythonping

#Create of a simple Flask app:

cat <<EOL > /home/ubuntu/proxy_app/proxy.py
from ec2_metadata import ec2_metadata
from flask import Flask
import mysql.connector
import pythonping
import random
from pythonping import ping
from flask import jsonify, request

from Setup_main import MASTER_PRIVATE_IP, PRIVATE_IP_SLAVE

app = Flask(__name__)

# Disabling the automatic sorting of JSON keys when generating JSON responses
app.config["JSON_SORT_KEYS"] = False


"""
Direct endpoint that insert data into a given table 
:param json: json data that contains query
:return: Query output
"""
@app.route("/direct", methods=["POST"])
def add():
    request_data = request.get_json()
    cnx = mysql_cnx(MASTER_PRIVATE_IP)
    # Send query to the targeted server
    insert(cnx, request_data["query"])
    return jsonify(message="Item added successfully"), 201


"""
Direct endpoint that select data from a given table through master node
:param json: json data that contains query
:return: Query output
"""
@app.route("/direct", methods=["GET"])
def direct_read():
    request_data = request.get_json()
    cnx = mysql_cnx(MASTER_PRIVATE_IP)
    # Send query to the targeted server
    result = select(cnx, request_data["query"])
    return jsonify(server="master", ip=MASTER_PRIVATE_IP, result=result)


"""
Random endpoint that select data from a given table through slave nodes
:param json: json data that contains query
:return: Query output
"""
@app.route("/random", methods=["GET"])
def random_call():
    request_data = request.get_json()
    # Retrieve query from data json
    query = request_data["query"]
    # Select a random slave ip from th given slaves list
    random_target = random.choice(PRIVATE_IP_SLAVES)
    cnx = mysql_cnx(random_target)
    # Send query to the targeted server
    result = select(cnx, query)
    return jsonify(server="slave", ip=random_target, result=result)


"""
Random endpoint that select data from a given table through min ping time between cluster nodes
:param json: json data that contains query
:return: Query output
"""
@app.route("/custom", methods=["GET"])
def custom_call():
    request_data = request.get_json()
    # Retrieve the min ping time and the node ip
    best_cnx, ping_time = get_best_cnx(MASTER_PRIVATE_IP, PRIVATE_IP_SLAVES)
    cnx = mysql_cnx(best_cnx)
    # Send query to the targeted server
    result = select(cnx, request_data["query"])
    if best_cnx == MASTER_PRIVATE_IP:
        server = "master"
    else:
        server = "slave"
    return jsonify(server=server, ip=best_cnx, ping_time=ping_time, result=result)


"""
Function opens a connexion with cibling node 
:parameter target_ip: Ip node to open connexion with
:return: node connector
"""
def mysql_cnx(target_ip):
    try:
        # User proxy is used since we created a specific one for proxy. The database sakila will also be used
        cnx = mysql.connector.connect(
            user="proxy",
            host=target_ip,
            database="sakila",
        )
        print("Cnx established with the database")
        return cnx
    except Exception as ex:
        print(f"Failed to connect to database due to {ex}")


"""
Function that execute given query (write or update) and save it
:param mysql_cnx: databse connector
:param query: insertion query
:return: result of the query
"""
def insert(mysql_cnx, query):
    cursor = mysql_cnx.cursor()
    cursor.execute(query)
    mysql_cnx.commit()


"""
Function that execute given query and fetch existing items
:param mysql_cnx: databse connector
:param query: insertion query
:return: query result
"""
def select(mysql_cnx, query):
    cursor = mysql_cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


"""
Function that fetch the cluster node with less response time 
:param master_ip: master private ip
:param slaves_ip: list of slaves ip
:return: node ip and ping time
"""
def get_best_cnx(master_ip, slaves_ip):
    cnx_repsonses = {}
    # Get manager (master) ping time
    cnx_repsonses[master_ip] = ping(master_ip).rtt_avg_ms

    # Get workers (slaves) ping time
    for slave in slaves_ip:
        cnx_repsonses[slave] = ping(slave).rtt_avg_ms

    # Get the min between collected ping time
    best_cnx = min(cnx_repsonses, key=cnx_repsonses.get)

    return str(best_cnx), cnx_repsonses[best_cnx]

EOL


#Install Gunicorn:

pip install gunicorn

#Run Gunicorn to show the message in the running script for the log management:

#gunicorn -b 0.0.0.0:8082 flask_app:app 

#pkill -f "gunicorn -b 0.0.0.0:8082 flask_app:app"

#Create a file system containing service instructions:

sudo cat <<EOL > /etc/systemd/system/flaskapp.service
[Unit]
Description=None
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/flaskapp
ExecStart=/home/ubuntu/flaskapp/venv/bin/gunicorn -b localhost:8082 flask_app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOL

#Enable the service:

sudo systemctl daemon-reload
sudo systemctl start flaskapp
sudo systemctl enable flaskapp

#Check the app is running using:

curl localhost:8082

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
    server 127.0.0.1:8082;
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