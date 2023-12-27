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
    with open('flask_orchestrator.sh', 'r') as f :
        flask_script_orchestrator = f.read()

    ud_orchestrator = str(flask_script_orchestrator)

    with open('flask_workers.sh', 'r') as f :
        flask_script_worker = f.read()

    ud_workers = str(flask_script_worker)
    

    #--------------------------------------Create Instances of orchestrator and workers ------------------------------------------------------------

    # Create 4 intances with m4.large as workers:
    Availabilityzons_Cluster1=['us-east-1a','us-east-1b','us-east-1a','us-east-1b','us-east-1a']
    instance_type = "m4.large"
    print("\n Creating instances : the workers ")

    # Creation of the 4 workers
    workers_m4= create_instance_ec2(4,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"worker",ud_workers)

    # Modifier le fichier test.json en fonction pour modifier les IP
    with open("test.json","r") as f:
            data=json.load(f)

    # Modify the ip in the test.json
    container_count = 0
    for i in range(len(workers_m4)):
        # Get one worker and map it to two containers with different ports :port 5000 and 5001
        for _ in range(2):
            container_count += 1
            container_id = "container" + str(container_count)
            data[container_id]["ip"]=workers_m4[i][1]
    with open ("test.json","w") as f:
        json.dump(data,f)

    print("\n\n json file updated succesfully \n\n")
    
    print('\n Waiting for deployement of flask application on workers containers ....\n')

    time.sleep(330)

    print("\n Creating instances : Orchestrator ")

    ##Once the test json is updated (with new ip), modify automatically the IP in orchestrator_user data 
    with open("test.json","r") as f:
            data=json.load(f)
    #get the modified IP
    new_ip=str(data)
    new_ip=new_ip.replace("'", '"')
    #Get the content of the old test.json content  in the previous user id
    pattern = re.compile(r'test\.json\n(.*?)\nEOL', re.DOTALL)
    result = re.search(pattern, ud_orchestrator)
    old_ip = result.group(1)

    #Replace the content of the updated ip in the ud_orchestrator
    ud_orchestrator=ud_orchestrator.replace(old_ip,new_ip)
    #Rewrite the updated file 
    with open('flask_orchestrator.sh', 'w') as file:
        file.write(ud_orchestrator)

    print("\n flask_orchestrator with the new containers ip ")

    # Creation of the orchestrator
    orchestrator_m4=create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,"orchestrator","")

    print("\n Orchestrator and the 4 workers created successfuly")
    


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
