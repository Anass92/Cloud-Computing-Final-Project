#!/bin/bash -i


# master
MASTER_PUBLIC_IP="__MASTER_IP__"
# slave 1
SLAVES_PUBLIC_IP[1]="__SLAVE_IP1__"
# slave 2
SLAVES_PUBLIC_IP[2]="__SLAVE_IP2__"
# slave 3
SLAVES_PUBLIC_IP[3]="__SLAVE_IP3__"


# Update apt package list
sudo apt update -y

# Create the Sakila directory with write permissions
sudo mkdir -p  /opt/mysqlcluster/home

# Change to the Sakila directory
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


# Setup MySQL Cluster directories and configuration
mkdir -p /opt/mysqlcluster/deploy
cd /opt/mysqlcluster/deploy
mkdir -p conf
mkdir -p mysqld_data
mkdir -p ndb_data
sudo chmod +w ./conf

# Create and write to my.cnf file
sudo cat <<EOL > conf/my.cnf
[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306
EOL


# Create and write to config.ini file
sudo cat <<EOL > conf/config.ini
[ndb_mgmd]
hostname=MASTER_PUBLIC_IP
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=3
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname=SLAVES_PUBLIC_IP[1]
nodeid=2

[ndbd]
hostname=SLAVES_PUBLIC_IP[2]
nodeid=3

[ndbd]
hostname=SLAVES_PUBLIC_IP[3]
nodeid=4

[mysqld]
nodeid=50
EOL


# Initialize the Database
cd /opt/mysqlcluster/home/mysqlc
sudo scripts/mysql_install_db -no-defaults -datadir=/opt/mysqlcluster/deploy/mysqld_data
# START MANAGEMENT NODE
sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/

# Display the current state of the MGMT SERVER : IT RUNS LISTENING ON PORT 1186
ndb_mgm -e show
# START SQL NODE
sudo /opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &
# CHECK STATUS OF MGMT/DATA/SQL NODES
ndb_mgm -e show


while ! mysqladmin ping --silent; do
    sleep 1
done



# Download Sakila database files
sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz  -O sakila-db.tar.gz
# Extract Sakila database files
sudo tar -xvzf sakila-db.tar.gz

# Change to the Sakila directory
cd /home/sakila/sakila-db

# Sakila config
sudo mysql -Bse "SOURCE sakila-schema.sql"
sudo mysql -Bse "SOURCE sakila-data.sql"

# Perform specific actions on Sakila database
mysql -u root -e "USE sakila; SHOW FULL TABLES;"
mysql -u root -e "USE sakila; SELECT COUNT(*) FROM film;"


mysql -u root -e "GRANT ALL PRIVILEGES ON sakila.* TO 'root'@'%' IDENTIFIED BY '' WITH GRANT OPTION;"
#Flush restrictions
mysql -u root -e "FLUSH PRIVILEGES"
mysql -u root -e "FLUSH TABLES WITH READ LOCK"
mysql -u root -e "UNLOCK TABLES"

# Install sysbench
sudo apt install sysbench -y
sudo sysbench /usr/share/sysbench/oltp_read_write.lua prepare --db-driver=mysql --mysql-host=ip-${MASTER_PUBLIC_IP//./-}.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password --table-size=1000000 
sudo sysbench /usr/share/sysbench/oltp_read_write.lua run --db-driver=mysql --mysql-host=ip-${MASTER_PUBLIC_IP//./-}.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password --table-size=1000000 --threads=8 --time=20 --events=0 > mycluster_results
sudo sysbench /usr/share/sysbench/oltp_read_write.lua cleanup --db-driver=mysql --mysql-host=ip-${MASTER_PUBLIC_IP//./-}.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password 






# Brouillon
#Create MySQL users and grant privileges:
# mysql -Bse "CREATE USER 'slave1'@'%';GRANT ALL ON *.* TO 'slave1'@'%'; CREATE USER 'slave2'@'%';GRANT ALL  ON *.* TO 'slave2'@'%'; CREATE USER 'slave3'@'%';GRANT ALL ON *.* TO 'slave3'@'%';CREATE USER 'proxy'@'%';GRANT ALL ON *.* TO 'proxy'@'%';"
