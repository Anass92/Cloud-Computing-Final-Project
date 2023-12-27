import configparser
import boto3
import time

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

#Function to create a service client for elbv2
def client_elbv2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    elbv2_serviceclient =  boto3.client('elbv2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
    

    
    return(elbv2_serviceclient)

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
def create_security_group(Description,Groupe_name,vpc_id,resource):
    Security_group_ID=resource.create_security_group(
        Description=Description,
        GroupName=Groupe_name,
        VpcId=vpc_id).id
    
    Security_group=resource.SecurityGroup(Security_group_ID)
    
    #Add an inbounded allowing inbounded traffics of all protocols, from and to all ports, and all Ipranges.  
    Security_group.authorize_ingress(
         IpPermissions=[
            {'FromPort':-1,
             'ToPort':-1,
             'IpProtocol':'-1',
             'IpRanges':[{'CidrIp':'0.0.0.0/0'}]
            }]
    )       
    return Security_group_ID

#------------------------------------------------End----------------------------------------------------


#Function to create ec2 instances : 
def create_instance_ec2(num_instances,ami_id,
    instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons, user_data):
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
                                'Value': 'lab1-ec2-instance-'+str(instance_type)+"-"+str(i + 1)
                            },
                        ]
                    },
                ]
        )
        instances.append(instance[0].id)
        print ('Instance: ',i+1,' having the Id: ',instance[0].id, ' in Availability Zone: ', Availabilityzons[i], 'is created')
        #print(f'{instances[i]} is starting')
   
    return instances

#Function to create target groups : 
def create_target_group(targetname,vpc_id,port, elbv2_serviceclient):
    tg_response=elbv2_serviceclient.create_target_group(
        Name=targetname,
        Protocol='HTTP',
        Port=port,
        VpcId=vpc_id,
        TargetType ='instance'
    )
    target_group_arn = tg_response["TargetGroups"][0]["TargetGroupArn"]    
    return target_group_arn

#Function to register targets in target groups : 
def register_targets(elbv2_serviceclient,instances_ids,target_group_arn):
    targets=[]
    for instance_id in instances_ids:
        targets.append({"Id":instance_id,"Port":80})

    tg_registered=elbv2_serviceclient.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=targets
    )
    return tg_registered

#Function to create load balancer : 
def create_load_balancer(elbv2_seviceclient,LB_name,subnets,security_group):
    response = elbv2_seviceclient.create_load_balancer(
        Name=LB_name,
        Subnets=subnets,
        SecurityGroups=[security_group]
                )
    load_balancer_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
  
    return load_balancer_arn

#Function to create listeners:
def create_listener(elbv2_seviceclient,load_balancer_arn):
        response_listener=elbv2_seviceclient.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Port=80,
        Protocol='HTTP',
        DefaultActions=[
            {
            'Type':'fixed-response',
            'FixedResponseConfig':{
                'StatusCode': '200',
                'ContentType':'text/plain',
                'MessageBody': 'ListenerLab'
            }
            }
            ]
        )
        response_listener_arn=response_listener["Listeners"][0]["ListenerArn"]
   
        return response_listener_arn

#Function to create listener rules
def create_listener_rule(elbv2_seviceclient,listener_arn, target_group_arn, path,prio):
        response = elbv2_seviceclient.create_rule(
            ListenerArn=listener_arn,
            Priority=prio,
            Conditions=[
                {
                    'Field': 'path-pattern',
                    'Values': [path]
                }
            ],
            Actions=[
                {
                    'Type': 'forward',
                    'ForwardConfig': {
                        'TargetGroups': [{'TargetGroupArn': target_group_arn}]
                    }
                }
            ]
        )
        response_rule_listener = response['Rules'][0]['RuleArn']
        return response_rule_listener
    


