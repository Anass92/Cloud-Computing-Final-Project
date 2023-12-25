#!/bin/bash

# Update apt package list
sudo apt update -y
# sudo apt-get -y install ca-certificates curl gnupg
# sudo install -m 0755 -d /etc/apt/keyrings
# sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv 


#Install Mysql Server
sudo apt install mysql-server -y


# Create the Sakila directory with write permissions
# mkdir /home/sakila
sudo chmod 777 /home/sakila
# Change to the Sakila directory
cd /home/sakila
# Download Sakila database files
sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz  -O sakila-db.tar.gz
# Extract Sakila database files
# tar -xvzf sakila-db.tar.gz
sudo tar -xvzf sakila-db.tar.gz


# Change to the Sakila directory
cd /home/sakila/sakila-db

#Sakila config
sudo mysql -Bse "SOURCE sakila-schema.sql"
sudo mysql -Bse "SOURCE sakila-data.sql"

#Install sysbench
# apt install sysbench -y
sudo apt install sysbench -y # For Debian/Ubuntu

