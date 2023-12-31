import configparser
import boto3
import time
import requests

#Function to create a service resource for ec2: 
def resource_ec2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    ec2_serviceresource =  boto3.resource('ec2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
    
    return(ec2_serviceresource)

#Function to create a service client for ec2
def client_ec2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    ec2_serviceclient =  boto3.client('ec2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
   
    
    return(ec2_serviceclient)

#Function to create and check a KeyPair : 
def create_keypair(key_pair_name, client):
    try:
        keypair = client.create_key_pair(KeyName=key_pair_name)
        print(keypair['KeyMaterial'])
        with open('lab1_keypair.pem', 'w') as f:
            f.write(keypair['KeyMaterial'])

        return(key_pair_name)

    except:
        print("\n\n============> Warning :  Keypair already created !!!!!!!<==================\n\n")
        return(key_pair_name)


#---------------------------------------------To re check----------------------------------------------
'Function to create a new vpc (Maybe no need for this, just use default vpc)'
def create_vpc(CidrBlock,resource):
   VPC_Id=resource.create_vpc(CidrBlock=CidrBlock).id
   return VPC_Id

'Function to create security group (Maybe no need for this, just use get securty group of default vpc)'
def create_security_group(Description,Groupe_name,vpc_id,resource,ip_range):
    Security_group_ID=resource.create_security_group(
        Description=Description,
        GroupName=Groupe_name,
        VpcId=vpc_id).id
    
    Security_group=resource.SecurityGroup(Security_group_ID)
    
    #Add an inbounded allowing inbounded traffics of tcp protocol, and ports 22,80, and all Ipranges.  
    Security_group.authorize_ingress(
         IpPermissions=[
            {'FromPort':22,
             'ToPort':22,
             'IpProtocol':'tcp',
             'IpRanges':[{'CidrIp':ip_range}]
            },
            {'FromPort':80,
             'ToPort':80,
             'IpProtocol':'tcp',
             'IpRanges':[{'CidrIp':ip_range}]
            },
            {'FromPort':443,
             'ToPort':443,
             'IpProtocol':'tcp',
             'IpRanges':[{'CidrIp':ip_range}]
            }
            ]
    ) 
    return Security_group_ID

#------------------------------------------------End----------------------------------------------------


#Function to create ec2 instances :  The function a list containing the [id of instance,public_ip_address]

def create_instance_ec2(num_instances,ami_id,
    instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons,instance_function,user_data):
    instances=[]
    for i in range(num_instances):
        instance=ec2_serviceresource.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_pair_name,
            MinCount=1,
            MaxCount=1,
            Placement={'AvailabilityZone':Availabilityzons[i]},
            SecurityGroupIds=[security_group_id] if security_group_id else [],
            UserData=user_data,
            TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'lab3-'+str(instance_function)+"-"+str(i + 1)
                            },
                        ]
                    },
                ]
        )

        #Wait until the instance is running to get its public_ip adress
        instance[0].wait_until_running()
        instance[0].reload()
        # Get the public ip address of the instance and add it in the return
        # And replace "." format with "-" format
        public_ip = str(instance[0].public_ip_address).replace(".","-")
        instances.append([instance[0].id,public_ip])
        print ('Instance: '+str(instance_function)+str(i+1),' having the Id: ',instance[0].id,'and having the ip',public_ip,' in Availability Zone: ', Availabilityzons[i], 'is created')
    return instances

def modify_script_ip_adress(shell_script_path,placeholder,IP_adress):
    # Read the content of the master script
    with open(shell_script_path, "r") as f:
        script_content = f.read()

    # Replace placeholders with actual IP addresses
    script_content = script_content.replace(placeholder, IP_adress)

    # Write the modified script content back to the shell script
    with open(shell_script_path, "w") as f:
        f.write(script_content)


    
    