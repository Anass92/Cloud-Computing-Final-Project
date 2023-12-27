import configparser
import boto3
from Setup_functions import *
import base64
import os
import json
from threading import Thread
import re

if __name__ == '__main__':
    # Get credentials from the config file :
    path = os.path.dirname(os.getcwd())
    config_object = configparser.ConfigParser()
    with open(path+"/credentials.ini","r") as file_object:
        #Loading of the aws tokens
        config_object.read_file(file_object)
        key_id = config_object.get("resource","aws_access_key_id")
        access_key = config_object.get("resource","aws_secret_access_key")
        session_token = config_object.get("resource","aws_session_token")
        ami_id = config_object.get("ami","ami_id")


    print('============================>SETUP Begins')

    #--------------------------------------Creating ec2 resource and client ----------------------------------------
    
    #Create ec2 resource with our credentials:
    ec2_serviceresource = resource_ec2(key_id, access_key, session_token)
    print("============> ec2 resource creation has been made succesfuly!!!!<=================")
    #Create ec2 client with our credentials:
    ec2_serviceclient = client_ec2(key_id, access_key, session_token)
    print("============> ec2 client creation has been made succesfuly!!!!<=================")

    #--------------------------------------Creating a keypair, or check if it already exists-----------------------------------
    
    key_pair_name = create_keypair('lab1_keypair', ec2_serviceclient)

    #---------------------------------------------------Get default VPC ID-----------------------------------------------------
    #Get default vpc description : 
    default_vpc = ec2_serviceclient.describe_vpcs(
        Filters=[
            {'Name':'isDefault',
             'Values':['true']},
        ]
    )
    default_vpc_desc = default_vpc.get("Vpcs")
   
    # Get default vpc id : 
    vpc_id = default_vpc_desc[0].get('VpcId')


    #--------------------------------------Try create a security group with all traffic inbouded--------------------------------
  
    try:
        security_group_id = create_security_group("All traffic sec_group","lab1_security_group",vpc_id,ec2_serviceresource)  
    
    except :
        #Get the standard security group from the default VPC :
        sg_dict = ec2_serviceclient.describe_security_groups(Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    vpc_id,
                ]
            },

        {
                'Name': 'group-name',
                'Values': [
                    "lab1_security_group",
                ]
            },

        ])

        security_group_id = (sg_dict.get("SecurityGroups")[0]).get("GroupId")
    

    #--------------------------------------Pass Server and Database deployment script into the user_data parameter ------------------------------
    with open('standalone_server.sh', 'r') as f :
        setup_script_Standalone_MySQL = f.read()

    ud_Standalone_MySQL = str(setup_script_Standalone_MySQL)

    with open('proxy.sh', 'r') as f :
        setup_script_proxy = f.read()

    ud_proxy = str(setup_script_proxy)

    with open('master_mysql_setup.sh', 'r') as f :
        setup_script_MySQL_Master = f.read()

    ud_MySQL_Master = str(setup_script_MySQL_Master)

    with open('slave_mysql_setup.sh', 'r') as f :
        server_script_MySQL_Slave = f.read()

    ud_MySQL_Slave = str(server_script_MySQL_Slave)
    

    #--------------------------------------Create Instances of orchestrator and workers ------------------------------------------------------------

    # Create 4 intances with t2.micro as MySQL Clusters:
    Availabilityzons_Cluster1=['us-east-1a','us-east-1b','us-east-1a','us-east-1b','us-east-1a']
    instance_type = "t2.micro"

    print("\n Creating instances : Standalone MySQL ")
    # Creation of the Standalone MySQL
    Standalone_MySQL=create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"Sakila_Standalone",ud_Standalone_MySQL)
    #print('\n Waiting for deployement of MYSQL Standalone server ....\n')
    #time.sleep(66)

    print("\n Creating instances : MySQL Cluster ")
    # Creation of 1 manager as master
    MySQL_Master= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"manager",ud_MySQL_Master)
    #print('\n Waiting for deployement of MYSQL server on manager ....\n')
    #time.sleep(120)
    MASTER_PRIVATE_IP = MySQL_Master[0][1]
    # Creation of 3 workers or slaves
    MySQL_Slaves= create_instance_ec2(3,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"worker",ud_MySQL_Slave)
    #print('\n Waiting for deployement of MYSQL server on workers ....\n')
    #time.sleep(330)
    PRIVATE_IP_SLAVES=[]
    for i in range(len(MySQL_Slaves)):
        # Get ip adress for each worker
        PRIVATE_IP_SLAVES[i]=MySQL_Slaves[i][1]

    print("\n Creating instances : Proxy ")
    instance_type = "t2.large"
    Proxy= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"proxy",ud_MySQL_Master)
    # print('\n Waiting for deployement of MYSQL server on clusters ....\n')
    # time.sleep(330)

 
    print("\n Standalone MySQL, the MySQL Cluster, Proxy, created successfuly")
    


    #----------------------------Get mapping between availability zones and Ids of default vpc subnets -------------------------------

    #Get the standard subnets discription from the default VPC :
    subnets_discription= ec2_serviceclient.describe_subnets(Filters=[
         {
            'Name': 'vpc-id',
            'Values': [
                vpc_id,
            ]
        }
    ])
    #Get mapping dictionary between Availability zones and subnets Ids
    mapping_AZ_subnetid={subnet['AvailabilityZone']:subnet['SubnetId'] for subnet in subnets_discription['Subnets']}
    
    
    print('============================>SETUP ends')
