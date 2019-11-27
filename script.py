import boto3
from botocore.exceptions import ClientError
import time
import paramiko

#Projeto de CLOUD
# SEM VPN, 2 REGIOES DA AWS


# Seta o nome da KeyPair
NOME_KEY_PAIR_NV = 'KEY_PROJECT_NV_CHICO'
NOME_KEY_PAIR_OH = 'KEY_PROJECT_OH_CHICO'

NOME_INSTANCIA_RED_OH = "RED_OHIO"
NOME_INSTANCIA_RED_NV = "RED_NORTH_VIRGINIA"
NOME_INSTANCIA_DB_OH = "DB_OHIO"
NOME_INSTANCIA_AS = "AS_NORT"

NOME_SECURITY_GROUP_DB = 'DB_SG_OH'
NOME_SECURITY_GROUP_RED_OH = 'RED_SG_OH'
NOME_SECURITY_GROUP_RED_NV = 'RED_SG_NV'
NOME_SECURITY_GROUP_LB_NV = "LBNV"

ELASTIC_IP_OH = "OH_CHICO"
ELASTIC_IP_NV = "NV_CHICO"

NOME_DB = "DB_COUCH"
NOME_LOADBALANCER = "LOADAPS"
NOME_AUTO_SCALLING = "AUTOSCALLINGAPS"


# DICT INSTANCIAS
instancias_DICTS = {'RED_OH': None, 'DB_OH': None}

# Inicial o boto3
ec2_client_NV = boto3.client('ec2',region_name='us-east-1')
ec2_resource_NV = boto3.resource('ec2',region_name='us-east-1')
waiterTerminate_NV = ec2_client_NV.get_waiter('instance_terminated')
waiterInicialize_NV = ec2_client_NV.get_waiter('instance_status_ok')
lb_client_NV = boto3.client('elb',region_name='us-east-1')
aa_client_NV = boto3.client('autoscaling')

ec2_client_OH = boto3.client('ec2',region_name='us-east-2')
ec2_resource_OH = boto3.resource('ec2',region_name='us-east-2')
waiterTerminate_OH = ec2_client_OH.get_waiter('instance_terminated')
waiterInicialize_OH = ec2_client_OH.get_waiter('instance_status_ok')


# Apaga Instancias já existentes
instances = ec2_resource_OH.instances.filter(Filters=[{'Name':'tag:Name', 'Values':[NOME_INSTANCIA_RED_OH]},{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in instances:
    print("%s\nTerminating instance %s" % (instance,instance.id))
    ec2_resource_OH.instances.filter(InstanceIds=[instance.id]).terminate()
    waiterTerminate_OH.wait(InstanceIds=[instance.id])

instances = ec2_resource_OH.instances.filter(Filters=[{'Name':'tag:Name', 'Values':[NOME_INSTANCIA_DB_OH]},{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in instances:
    print("%s\nTerminating instance %s" % (instance,instance.id))
    ec2_resource_OH.instances.filter(InstanceIds=[instance.id]).terminate()
    waiterTerminate_OH.wait(InstanceIds=[instance.id])

instances = ec2_resource_NV.instances.filter(Filters=[{'Name':'tag:Name', 'Values':[NOME_INSTANCIA_RED_NV]},{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in instances:
    print("%s\nTerminating instance %s" % (instance,instance.id))
    ec2_resource_NV.instances.filter(InstanceIds=[instance.id]).terminate()
    waiterTerminate_NV.wait(InstanceIds=[instance.id])

instances = ec2_resource_NV.instances.filter(Filters=[{'Name':'tag:Name', 'Values':['AS: XYKO']},{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in instances:
    print("%s\nTerminating instance %s" % (instance,instance.id))
    ec2_resource_NV.instances.filter(InstanceIds=[instance.id]).terminate()
    waiterTerminate_NV.wait(InstanceIds=[instance.id])

instances = ec2_resource_NV.instances.filter(Filters=[{'Name':'tag:Name', 'Values':[NOME_AUTO_SCALLING]},{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in instances:
    print("%s\nTerminating instance %s" % (instance,instance.id))
    ec2_resource_NV.instances.filter(InstanceIds=[instance.id]).terminate()
    waiterTerminate_NV.wait(InstanceIds=[instance.id])
try:
    response = aa_client_NV.delete_auto_scaling_group(AutoScalingGroupName=NOME_AUTO_SCALLING,ForceDelete=True)
except Exception as e:
    print(e)
try:
    response = aa_client_NV.delete_launch_configuration(LaunchConfigurationName=NOME_AUTO_SCALLING)
except Exception as e:
    print(e)
try:    
    response = aa_client_NV.describe_auto_scaling_groups(AutoScalingGroupNames=[NOME_AUTO_SCALLING])
    while response['AutoScalingGroups']:
        print("deletando AS")
        time.sleep(15)
        response = ec2_as.describe_auto_scaling_groups(AutoScalingGroupNames=[NOME_AUTO_SCALLING])

    response = aa_client_NV.describe_auto_scaling_groups(AutoScalingGroupNames=[NOME_AUTO_SCALLING])
except Exception as e:
    print(e)


# Load Balancer

#SG LB
# Security Group DB
print('Searching for existing Security Groups')
response = ec2_client_NV.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

# Verificar e apagar Security Group caso já exista
try:
    print('Deleting existing Security Group %s' % (NOME_SECURITY_GROUP_LB_NV))
    response = ec2_client_NV.describe_security_groups()
    for i in response['SecurityGroups']:
        if(i['GroupName'] == NOME_SECURITY_GROUP_LB_NV):
            security_group_id = i['GroupId']
            response = ec2_client_NV.delete_security_group(GroupId=security_group_id)
            print("Deleted security group succesfully \n",response)
except ClientError as e:
    print(e)

# Criar Security Group
try:
    print("Creating new Security Group '%s'" % (NOME_SECURITY_GROUP_LB_NV))
    response = ec2_client_NV.create_security_group(GroupName=NOME_SECURITY_GROUP_LB_NV,
                                         Description='SG LB',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2_client_NV.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 5000,
             'ToPort': 5000,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)


#LB
response_deleted = lb_client_NV.delete_load_balancer(LoadBalancerName=NOME_LOADBALANCER)
print(response_deleted)

response = lb_client_NV.create_load_balancer(
        LoadBalancerName=NOME_LOADBALANCER,
        Listeners=[
            {
                'Protocol': 'HTTP',
                'LoadBalancerPort': 80,
                'InstanceProtocol': 'HTTP',
                'InstancePort': 5000,
            }
        ],
        AvailabilityZones=[
            'us-east-1a','us-east-1b','us-east-1c', 'us-east-1e', 'us-east-1f', 'us-east-1d'
        ],
        SecurityGroups=[security_group_id,],
        Tags=[
            {
                'Key':'Owner',
                'Value': 'Xykhw'
            }
        ]
    )


# Procura chaves existentes

response = ec2_client_NV.describe_key_pairs(KeyNames=[NOME_KEY_PAIR_NV])
if(response['KeyPairs'][0]['KeyName'] == NOME_KEY_PAIR_NV):
    response = ec2_client_NV.delete_key_pair(KeyName=NOME_KEY_PAIR_NV)

response = ec2_client_OH.describe_key_pairs(KeyNames=[NOME_KEY_PAIR_OH])
if(response['KeyPairs'][0]['KeyName'] == NOME_KEY_PAIR_OH):
    response = ec2_client_OH.delete_key_pair(KeyName=NOME_KEY_PAIR_OH)


# Cria a KeyPair
print("Creating new key %s" % (NOME_KEY_PAIR_NV))
response = ec2_client_NV.create_key_pair(KeyName=NOME_KEY_PAIR_NV)
print("Key pair created")

for i in response:
    if i == 'KeyMaterial':
        f = open(NOME_KEY_PAIR_NV, "w")
        f.write(response[i])
        f.close()

print("Creating new key %s" % (NOME_KEY_PAIR_OH))
response = ec2_client_OH.create_key_pair(KeyName=NOME_KEY_PAIR_OH)
print("Key pair created")

for i in response:
    if i == 'KeyMaterial':
        f = open(NOME_KEY_PAIR_OH, "w")
        f.write(response[i])
        f.close()




# Elastic IPs
filters = [
    {'Name': 'domain', 'Values': ['vpc']}
]
OH_ELASTIC = {'Allocation ID':"","Elastic IP":""}
NV_ELASTIC = {'Allocation ID':"","Elastic IP":""}

    # OH
OH_NEED_CREATE = True
response = ec2_client_OH.describe_addresses(Filters=filters)
try:
    for i in response['Addresses']:
        if 'NetworkInterfaceId' not in i:   
            OH_NEED_CREATE = False 
            OH_ELASTIC["Allocation ID"] = i['AllocationId']
            OH_ELASTIC['Elastic IP'] = i['PublicIp']
except Exception as e: 
    print("ERROR ",e)


    # NV
NV_NEED_CREATE = True
response = ec2_client_NV.describe_addresses(Filters=filters)
try:
    for i in response['Addresses']:
        if 'NetworkInterfaceId' not in i:
            NV_NEED_CREATE = False
            NV_ELASTIC['Allocation ID'] = i['AllocationId']
            NV_ELASTIC['Elastic IP'] = i['PublicIp']
except Exception as e: 
    print("ERROR ",e)



# CREATE IF NOT EXIST ELASTIC IP

if OH_NEED_CREATE:
    response = ec2_client_OH.allocate_address(Domain='vpc')
    OH_ELASTIC["Allocation ID"] = response['AllocationId']
    OH_ELASTIC['Elastic IP'] = response['PublicIp']
    
if NV_NEED_CREATE:
    response = ec2_client_NV.allocate_address(Domain='vpc')
    NV_ELASTIC['Allocation ID'] = response['AllocationId']
    NV_ELASTIC['Elastic IP'] = response['PublicIp']


print("ELASTIC NV : %s" % (NV_ELASTIC['Elastic IP']))
print("             %s" % (NV_ELASTIC['Allocation ID']))

print("ELASTIC OH : %s" % (OH_ELASTIC['Elastic IP']))
print("             %s" % (OH_ELASTIC['Allocation ID']))

# Security Group RED
print('Searching for existing Security Groups')
response = ec2_client_OH.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

# Verificar e apagar Security Group caso já exista
try:
    print('Deleting existing Security Group %s' % (NOME_SECURITY_GROUP_RED_OH))
    response = ec2_client_OH.describe_security_groups()
    for i in response['SecurityGroups']:
        if(i['GroupName'] == NOME_SECURITY_GROUP_RED_OH):
            security_group_id = i['GroupId']
            response = ec2_client_OH.delete_security_group(GroupId=security_group_id)
            print("Deleted security group succesfully \n",response)
except ClientError as e:
    print(e)

# Criar Security Group
try:
    print("Creating new Security Group '%s'" % (NOME_SECURITY_GROUP_RED_OH))
    response = ec2_client_OH.create_security_group(GroupName=NOME_SECURITY_GROUP_RED_OH,
                                         Description='Redirecionamento para DB',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
    print("\n\n\n",NV_ELASTIC['Elastic IP'])
    data = ec2_client_OH.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 5000,
             'ToPort': 5000,
             'IpRanges': [{'CidrIp': '%s/32' % (str(NV_ELASTIC['Elastic IP']))}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])  
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)

# CREATE RED_OH
print("Creating new Instance '%s'" % (NOME_INSTANCIA_RED_OH))
instance = ec2_resource_OH.create_instances(ImageId='ami-0d5d9d301c853a04a',UserData="#! /bin/bash\ngit clone https://github.com/franciol/Projeto_Cloud.git;", MinCount=1, MaxCount=1,InstanceType = 't2.micro', KeyName=NOME_KEY_PAIR_OH, SecurityGroupIds= [security_group_id,],TagSpecifications=[{'ResourceType': 'instance','Tags': [ {'Key': 'Name','Value': NOME_INSTANCIA_RED_OH }]}])
print("Instance %s created" % (NOME_INSTANCIA_RED_OH))
print("Waiting for Instance %s" % (NOME_INSTANCIA_RED_OH))
waiterInicialize_OH.wait(InstanceIds=[instance[0].id])
print("INICIALIZED")
ec2_client_OH.associate_address(DryRun = False,InstanceId = instance[0].id, AllocationId = OH_ELASTIC["Allocation ID"])
instancias_DICTS['RED_OH'] = instance
print("PRIVATEIP: %s"%(instance[0].private_ip_address))
pip_RED = instance[0].private_ip_address


instances = ec2_resource_OH.instances.filter(Filters=[{'Name':'tag:Name', 'Values':[NOME_INSTANCIA_RED_OH]},{'Name': 'instance-state-name', 'Values': ['running']}])

for instance in instances:
    PRIVATE_IP_RED = instance.private_ip_address
    print(instance.id,instance.private_ip_address ,instance.instance_type)



# Security Group DB
print('Searching for existing Security Groups')
response = ec2_client_OH.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

# Verificar e apagar Security Group caso já exista
try:
    print('Deleting existing Security Group %s' % (NOME_SECURITY_GROUP_DB))
    response = ec2_client_OH.describe_security_groups()
    for i in response['SecurityGroups']:
        if(i['GroupName'] == NOME_SECURITY_GROUP_DB):
            security_group_id = i['GroupId']
            response = ec2_client_OH.delete_security_group(GroupId=security_group_id)
            print("Deleted security group succesfully \n",response)
except ClientError as e:
    print(e)

# Criar Security Group
try:
    print("Creating new Security Group '%s'" % (NOME_SECURITY_GROUP_DB))
    response = ec2_client_OH.create_security_group(GroupName=NOME_SECURITY_GROUP_DB,
                                         Description='SG DB',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2_client_OH.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 5000,
             'ToPort': 5000,
             'IpRanges': [{'CidrIp': '%s/32' % (PRIVATE_IP_RED)}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)
    

# CREATE DB_OH
print("Creating new Instance '%s'" % (NOME_INSTANCIA_DB_OH))
userdd = str("#! /bin/bash\ngit clone https://github.com/franciol/Projeto_Cloud.git;sh Projeto_Cloud/SCRIPTS/install_db.sh;")
instance = ec2_resource_OH.create_instances(ImageId='ami-0d5d9d301c853a04a',UserData=userdd, MinCount=1, MaxCount=1,InstanceType = 't2.micro', KeyName=NOME_KEY_PAIR_OH, SecurityGroupIds= [security_group_id,],TagSpecifications=[{'ResourceType': 'instance','Tags': [ {'Key': 'Name','Value': NOME_INSTANCIA_DB_OH }]}])
print("Instance %s created" % (NOME_INSTANCIA_DB_OH))
print("Waiting for Instance %s" % (NOME_INSTANCIA_DB_OH))
waiterInicialize_OH.wait(InstanceIds=[instance[0].id])
print("INICIALIZED")
instancias_DICTS['DB_OH'] = instance    

for i in instancias_DICTS:
    print("%s : \n    %s\n\n" % (i,instancias_DICTS[i]))



# Conect to RED_OH to prepare its IP
k = paramiko.RSAKey.from_private_key_file('./KEY_PROJECT_OH_CHICO')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect( hostname=OH_ELASTIC['Elastic IP'], username="ubuntu", pkey = k )
userdd = str("sudo tmux new -d -s execution 'export IPSERVIDOR=%s;sudo python3 /Projeto_Cloud/server_red_OH.py';" % (instancias_DICTS['DB_OH'][0].private_ip_address))
print(userdd)
commands = ['sh /Projeto_Cloud/SCRIPTS/install_RED_OH.sh',userdd]
for comm in commands:
    print ("\nExecuting {}\n".format(comm))
    stdin , stdout, stderr = c.exec_command(comm)
    print ("\n",stdout.read())
    print( "\nErrors\n")
    print ('\n',stderr.read())
c.close() 

# Create SG_RED_NV

# Security Group DB
print('Searching for existing Security Groups')
response = ec2_client_NV.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

# Verificar e apagar Security Group caso já exista
try:
    print('Deleting existing Security Group %s' % (NOME_SECURITY_GROUP_RED_NV))
    response = ec2_client_NV.describe_security_groups()
    for i in response['SecurityGroups']:
        if(i['GroupName'] == NOME_SECURITY_GROUP_RED_NV):
            security_group_id = i['GroupId']
            response = ec2_client_NV.delete_security_group(GroupId=security_group_id)
            print("Deleted security group succesfully \n",response)
except ClientError as e:
    print(e)

# Criar Security Group
try:
    print("Creating new Security Group '%s'" % (NOME_SECURITY_GROUP_RED_NV))
    response = ec2_client_NV.create_security_group(GroupName=NOME_SECURITY_GROUP_RED_NV,
                                         Description='SG DB',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2_client_NV.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 5000,
             'ToPort': 5000,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)
    

# Criar RED_NV
print("Creating new Instance '%s'" % (NOME_INSTANCIA_RED_NV))

userdd = str("""#! /bin/bash
git clone https://github.com/franciol/Projeto_Cloud.git
sh /Projeto_cloud/SCRIPTS/install_as.sh
""")

instance = ec2_resource_NV.create_instances(ImageId='ami-04b9e92b5572fa0d1',UserData=userdd, MinCount=1, MaxCount=1,InstanceType = 't2.micro', KeyName=NOME_KEY_PAIR_NV, SecurityGroupIds= [security_group_id,],TagSpecifications=[{'ResourceType': 'instance','Tags': [ {'Key': 'Name','Value': NOME_INSTANCIA_RED_NV }]}])
print("Instance %s created" % (NOME_INSTANCIA_RED_NV))
print("Waiting for Instance %s" % (NOME_INSTANCIA_RED_NV))
waiterInicialize_NV.wait(InstanceIds=[instance[0].id])  
print("INICIALIZED")
instancias_DICTS['RED_NV'] = instance 
red_nv_ip = instance[0].private_ip_address
print(NV_ELASTIC["Allocation ID"])
ec2_client_NV.associate_address(DryRun = False,InstanceId = instance[0].id, AllocationId = NV_ELASTIC["Allocation ID"]) 

# Criar Base Autoscalling
print("Creating new Instance '%s'" % (NOME_INSTANCIA_AS))

userdd = str("""#! /bin/bash
git clone https://github.com/franciol/Projeto_Cloud.git
sh Projeto_Cloud/SCRIPTS/install_as.sh
""")
instance = ec2_resource_NV.create_instances(ImageId='ami-04b9e92b5572fa0d1',UserData=userdd, MinCount=1, MaxCount=1,InstanceType = 't2.micro', KeyName=NOME_KEY_PAIR_NV, SecurityGroupIds= [security_group_id,],TagSpecifications=[{'ResourceType': 'instance','Tags': [ {'Key': 'Name','Value': "AS: XYKO" }]}])
print("Instance %s created" % (NOME_INSTANCIA_RED_NV))
print("Waiting for Instance %s" % (NOME_INSTANCIA_RED_NV))
waiterInicialize_NV.wait(InstanceIds=[instance[0].id])
instancias_DICTS['AS_NV'] = instance

NV_NEED_CREATE = True
response = ec2_client_NV.describe_addresses(Filters=filters)
try:
    for i in response['Addresses']:
        if 'NetworkInterfaceId' not in i:
            NV_NEED_CREATE = False
            NV2_ELASTIC['Allocation ID'] = i['AllocationId']
            NV2_ELASTIC['Elastic IP'] = i['PublicIp']
except Exception as e: 
    print("ERROR ",e)

if NV_NEED_CREATE:
    response = ec2_client_NV.allocate_address(Domain='vpc')
    NV2_ELASTIC['Allocation ID'] = response['AllocationId']
    NV2_ELASTIC['Elastic IP'] = response['PublicIp']
ec2_client_NV.associate_address(DryRun = False,InstanceId = instance[0].id, AllocationId = NV2_ELASTIC["Allocation ID"]) 


# levantando servidor RED_NV
k = paramiko.RSAKey.from_private_key_file('./KEY_PROJECT_OH_CHICO')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect( hostname=OH_ELASTIC['Elastic IP'], username="ubuntu", pkey = k )
userdd = str("sudo tmux new -d -s execution 'export IPSERVIDOR=%s;sudo python3 /Projeto_Cloud/server_red_OH.py';" % (instancias_DICTS['DB_OH'][0].private_ip_address))
print(userdd)
commands = ['sh /Projeto_Cloud/SCRIPTS/install_RED_OH.sh',userdd]
for comm in commands:
    print ("\nExecuting {}\n".format(comm))
    stdin , stdout, stderr = c.exec_command(comm)
    print ("\n",stdout.read())
    print( "\nErrors\n")
    print ('\n',stderr.read())
c.close() 

k = paramiko.RSAKey.from_private_key_file('./KEY_PROJECT_NV_CHICO')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect( hostname=NV_ELASTIC['Elastic IP'], username="ubuntu", pkey = k )
userdd = str("sudo tmux new -d -s execution 'export IPSERVIDOR=%s;sudo python3 /Projeto_Cloud/server_rest.py';" % (OH_ELASTIC['Elastic IP']))
print(userdd)
commands = ['sh /Projeto_Cloud/SCRIPTS/install_as.sh',userdd]
for comm in commands:
    print ("\nExecuting {}\n".format(comm))
    stdin , stdout, stderr = c.exec_command(comm)
    print ("\n",stdout.read())
    print( "\nErrors\n")
    print ('\n',stderr.read())
c.close() 

# levantando servidor AS:XYKO
k = paramiko.RSAKey.from_private_key_file('./KEY_PROJECT_NV_CHICO')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect( hostname=NV2_ELASTIC['Elastic IP'], username="ubuntu", pkey = k)
userdd = str("sudo tmux new -d -s execution 'export IPSERVIDOR=%s;sudo python3 /Projeto_Cloud/server_rest.py';" % (NV_ELASTIC['Elastic IP']))
print(userdd)
commands = ['sh /Projeto_Cloud/SCRIPTS/install_as.sh',userdd]
for comm in commands:
    print ("\nExecuting {}\n".format(comm))
    stdin , stdout, stderr = c.exec_command(comm)
    print ("\n",stdout.read())
    print( "\nErrors\n")
    print ('\n',stderr.read())
c.close() 


# AutoScalling 
response = aa_client_NV.create_auto_scaling_group(
        AutoScalingGroupName=NOME_AUTO_SCALLING,
        InstanceId=instance[0].id,
        MinSize=1,
        MaxSize=10,
        HealthCheckGracePeriod=300,
        LoadBalancerNames=[
            NOME_LOADBALANCER,
        ]
    )
print(response)