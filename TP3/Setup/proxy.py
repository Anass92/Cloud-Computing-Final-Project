#!/usr/bin/env python3

import mysql.connector
import pythonping
import random

from pythonping import ping
from flask import Flask
from flask import jsonify, request


# master
MASTER_PUBLIC_IP="__MASTER_IP__"
# slave 1
SLAVES_PUBLIC_IP[1]="__SLAVE_IP1__"
# slave 2
SLAVES_PUBLIC_IP[2]="__SLAVE_IP2__"
# slave 3
SLAVES_PUBLIC_IP[3]="__SLAVE_IP3__"


app = Flask(__name__)

# Disabling the automatic sorting of JSON keys when generating JSON responses
app.config["JSON_SORT_KEYS"] = False


# This is a Direct endpoint for inserting data into a specified table. 
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/direct", methods=["POST"])
def add():
    request_data = request.get_json()
    cnx = mysql_cnx(MASTER_PUBLIC_IP)
    # Send query to the targeted server
    insert(cnx, request_data["query"])
    return jsonify(message="The addition of the item was successful"), 200



# This is a Direct endpoint for selecting data from a specified table through master node.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/direct", methods=["GET"])
def direct_read():
    request_data = request.get_json()
    cnx = mysql_cnx(MASTER_PUBLIC_IP)
    # Send query to the targeted server
    result = select(cnx, request_data["query"])
    return jsonify(server="master", ip=MASTER_PUBLIC_IP, result=result)



# This is a Customized endpoint for selecting data from a specified table by determining the minimum ping time among cluster nodes.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/custom", methods=["GET"])
def custom_call():
    request_data = request.get_json()
    # Retrieve the min ping time and the node ip
    best_cnx, ping_time = get_best_cnx(MASTER_PUBLIC_IP, SLAVES_PUBLIC_IP)
    cnx = mysql_cnx(best_cnx)
    # Send query to the targeted server
    result = select(cnx, request_data["query"])
    if best_cnx == MASTER_PUBLIC_IP:
        server = "master"
    else:
        server = "slave"
    return jsonify(server=server, ip=best_cnx, ping_time=ping_time, result=result)



# This is a Random endpoint for selecting data from a specified table through slave node.
# Parameter: JSON data containing the query.
# Return: Output of the query.

@app.route("/random", methods=["GET"])
def random_read():
    request_data = request.get_json()
    # Retrieve query from data json
    query = request_data["query"]
    # Select a random slave ip from th given slaves list
    random_target = random.choice(SLAVES_PUBLIC_IP)
    cnx = mysql_cnx(random_target)
    # Send query to the targeted server
    result = select(cnx, query)
    return jsonify(server="slave", ip=random_target, result=result)



# Function establishes a connection with a sibling node.
# Parameter: JSON data containing the query.
# Return: Output of the query.

def mysql_cnx(target_ip):
    try:
        # User proxy is used since we created a specific one for proxy. The database sakila will also be used
        cnx = mysql.connector.connect(user="proxy",host=target_ip,database="sakila",)
        print("Cnx established with the database")
        return cnx
    except Exception as ex:
        print(f"Failed to connect to database due to {ex}")



# Function that execute given query and fetch existing items
# Parameters:
# mysql_cnx: Fatabse connector
# query: insertion query
# Return: query result

def select(mysql_cnx, query):
    cursor = mysql_cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result



# Function that retrieves (fetch) the cluster node with the lowest response time.
# Parameters:
# master_ip: Master private IP
# slaves_ip: List of slaves' IP addresses
# Return: Node IP and ping time

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



# Function that executes a provided query (write or update) using a database connector and saves the result of the query.
# Function that execute given query (write or update) and save it
# Param mysql_cnx: Fatabse connector
# Param query: insertion query
# Return: query result

def insert(mysql_cnx, query):
    cursor = mysql_cnx.cursor()
    cursor.execute(query)
    mysql_cnx.commit()





if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8082)