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
    

    #--------------------------------------Pass flask deployment script into the user_data parameter ------------------------------
    with open('standalone_server.sh', 'r') as f :
        setup_script_Standalone_MySQL = f.read()

    ud_Standalone_MySQL = str(setup_script_Standalone_MySQL)

    with open('cluster_mysql_server.sh', 'r') as f :
        server_script_MySQL_Cluster = f.read()

    ud_MySQL_Cluster = str(server_script_MySQL_Cluster)
    

    #--------------------------------------Create Instances of orchestrator and workers ------------------------------------------------------------

    # Create 4 intances with t2.micro as MySQL Clusters:
    Availabilityzons_Cluster1=['us-east-1a','us-east-1b','us-east-1a','us-east-1b','us-east-1a']
    instance_type = "t2.micro"
    # print("\n Creating instances : MySQL Clusters ")

    # Creation of the 4 MySQL Clusters
    # 3 workers
    # MySQL_Clusters= create_instance_ec2(3,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"worker",ud_MySQL_Cluster)
    # 1 manager
    # MySQL_Clusters= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"manager",ud_MySQL_Cluster)




    
    # print('\n Waiting for deployement of MYSQL server on clusters ....\n')
    
    # time.sleep(330)

    print("\n Creating instances : Standalone MySQL ")





    # Creation of the Standalone MySQL
    Standalone_MySQL=create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"Sakila_Standalone",ud_Standalone_MySQL)

    print("\n Standalone MySQL and the 4 MySQL Clusters created successfuly")
    


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
