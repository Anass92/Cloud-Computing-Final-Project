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

#Create of a simple Flask app: