import configparser
import boto3
from Setup_functions import *
import base64
import os


if __name__ == '__main__':
    # Get credentials from the config file :
    path = os.path.dirname(os.getcwd())
    config_object = configparser.ConfigParser()
    with open(path+"/credentials.ini","r") as file_object:
        config_object.read_file(file_object)
        key_id = config_object.get("resource","aws_access_key_id")
        access_key = config_object.get("resource","aws_secret_access_key")
        session_token = config_object.get("resource","aws_session_token")
        ami_id = config_object.get("ami","ami_id")


    print('============================>SETUP Begins')

    #--------------------------------------Creating ec2 and elbv2 resource and client ----------------------------------------
    
    #Create ec2 resource with our credentials:
    ec2_serviceresource = resource_ec2(key_id, access_key, session_token)
    print("============> ec2 resource creation has been made succesfuly!!!!<=================")
    #Create ec2 client with our credentials:
    ec2_serviceclient = client_ec2(key_id, access_key, session_token)
    print("============> ec2 client creation has been made succesfuly!!!!<=================")
    #Create elbv2 client with our credentials:
    elbv2_serviceclient = client_elbv2(key_id, access_key, session_token)
    print("============> elbv2 client creation has been made succesfuly!!!!<=================")

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
    
    with open('flask_deployment.sh', 'r') as f :
        flask_script = f.read()

    ud = str(flask_script)


    #--------------------------------------Create Instances of cluster 1 ------------------------------------------------------------

    # Create 5 instances with m4.large as instance type:
    'By choice, we create the 5 EC2 instances for Cluster 1 in avaibility zones us-east-1a and us-east-1b'
    Availabilityzons_Cluster1=['us-east-1a','us-east-1b','us-east-1a','us-east-1b','us-east-1a']
    instance_type = "m4.large"
    print("\n Creating instances of Cluster 1 with type : m4.large")
    instances_m4= create_instance_ec2(5,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1,ud)
    #print(instances_m4)
    print("\n Instances created succefuly instance type  : m4.large")

    #--------------------------------------Create Instances of cluster 2 -----------------------------------------------------------

    # Create 4 instances with t2.large as intance type,
    'By choice, we create the 4 EC2 instances for Cluster 2 in availability zones us-east-1c and us-east-1d'
    Availabilityzons_Cluster2=['us-east-1c','us-east-1d','us-east-1c','us-east-1d']
    instance_type = "t2.large"
    print("\n Creating instances of Cluster 2 with type : t2.large")
    instances_t2= create_instance_ec2(4,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster2,ud)
    #print(instances_t2)
    print("\n Instances created succefuly instance type : t2.large")

    
    #--------------------------------------------Create Target groups ----------------------------------------------------------------

    #Create the two targets groups (Clusters)
    TargetGroup1_name='Cluster1-m4-large'
    target_group_1=create_target_group(TargetGroup1_name,vpc_id,80, elbv2_serviceclient)
    TargetGroup2_name='Cluster2-t2-large'
    target_group_2=create_target_group(TargetGroup2_name,vpc_id,80, elbv2_serviceclient)
    print("\nTarget groups created")

    
    #---------------------------------------------Register Targets on target groups --------------------------------------------------

    #time to wait for update ec2 running status before registration in target groups
    print("\nWaiting for EC2 instances to become on running status before registration in Target groups...")
    time.sleep(180)
    #Targets registration on target groups
    register_targets(elbv2_serviceclient,instances_m4,target_group_1) 
    register_targets(elbv2_serviceclient,instances_t2,target_group_2)
    print("Targets registred")

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
    mapping_AZ_subnetid


    #--------------------------------------Create Load balancer with appropriate subnets ----------------------------------------------

    #Define appropriate subnets associated with used availabilty zones
    subnetsIds=[mapping_AZ_subnetid[AZ] for AZ in set(Availabilityzons_Cluster1).union(Availabilityzons_Cluster2)]
    #Create Load balancer 
    LoadBalancerName='OurALB'
    load_balancerarn=create_load_balancer(elbv2_serviceclient,LoadBalancerName,subnetsIds,security_group_id)
    print('Load balancer created')

    #Create listeners listener
    listener_group=create_listener(elbv2_serviceclient,load_balancerarn) 
    print('Listener created')

    #Create listeners rules
    rules=[]
    rule_list_1=create_listener_rule(elbv2_serviceclient,listener_group,target_group_1,'/cluster1',2)
    rule_list_2=create_listener_rule(elbv2_serviceclient,listener_group,target_group_2,'/cluster2',3)
    
    rules.append(rule_list_1)
    rules.append(rule_list_2)

    print('Listner rules created')
    
    print('============================>SETUP ends')
