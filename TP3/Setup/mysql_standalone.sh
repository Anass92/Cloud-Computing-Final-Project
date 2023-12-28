#!/bin/bash

# Update apt package list
sudo apt update -y
# sudo apt-get -y install ca-certificates curl gnupg
# sudo install -m 0755 -d /etc/apt/keyrings
# sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv 


#Install Mysql Server
sudo apt install mysql-server -y


# Create the Sakila directory with write permissions
#sudo chmod 777 /home/sakila
sudo mkdir -p /home/sakila
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
sudo apt install sysbench -y # For Debian/Ubuntu

# Change the MySQL root password
sudo mysql -e "CREATE USER 'anass'@'localhost' IDENTIFIED BY '2121';"
# Add all privileges
sudo mysql -e "GRANT ALL PRIVILEGES ON sakila.* TO 'anass'@'localhost';"


# Run sysbench benchmarks
sysbench --db-driver=mysql --mysql-db=sakila --mysql-user=anass --mysql_password=2121 --table-size=20000 --tables=7 /usr/share/sysbench/oltp_read_write.lua prepare
sysbench --db-driver=mysql --mysql-db=sakila --mysql-user=anass --mysql_password=2121 --table-size=20000 --tables=7 --threads=18 --max-time=20 /usr/share/sysbench/oltp_read_write.lua run

sysbench --db-driver=mysql --mysql-db=sakila --mysql-user=anass --mysql_password=2121 /usr/share/sysbench/oltp_read_write.lua cleanup

