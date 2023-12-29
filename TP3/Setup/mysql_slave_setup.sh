#!bin/bash

# ******************************** GET ip adress*************************
# master
MASTER_PUBLIC_IP="__MASTER_IP__"

mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home

# Download MySQL Cluster
sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz -O mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz 
# Extract MySQL Cluster
sudo tar -xvzf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
# Creates a symbolic link named mysqlc that points to the previous directory My
ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

# Set environment variables for the current shell
echo 'export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc' > /etc/profile.d/mysqlc.sh
echo 'export PATH=$MYSQLC_HOME/bin:$PATH' >> /etc/profile.d/mysqlc.sh
source /etc/profile.d/mysqlc.sh
sudo apt-get update && sudo apt-get -y install libncurses5




# Create NDB DATA directory
mkdir -p /opt/mysqlcluster/deploy/ndb_data

# CHANGE IP HERE
ndbd -c ip-${MASTER_PUBLIC_IP//./-}.ec2.internal:1186