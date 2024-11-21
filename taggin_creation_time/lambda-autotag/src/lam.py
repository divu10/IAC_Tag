import boto3
import os
import json
from datetime import datetime, timezone, timedelta
from dateutil import tz

def aws_ec2(event):
    arnList = []
    _account = event['account']
    _region = event['region']
    # ec2ArnTemplate = 'arn:aws:ec2:@region@:@account@:instance/@instanceId@'
    # volumeArnTemplate = 'arn:aws:ec2:@region@:@account@:volume/@volumeId@'
    # vpcArnTemplate = 'arn:aws:ec2:@region@:@account@:vpc/@vpcId@'
    # sgArnTemplate = 'arn:aws:ec2:@region@:@account@:security-group/@securityGroupId@'
    # subnetArnTemplate = 'arn:aws:ec2:@region@:@account@:subnet/@subnetId@'
    # igArnTemplate = 'arn:aws:ec2:@region@:@account@:internet-gateway/@igwId@'
    # ngArnTemplate = 'arn:aws:ec2:@region@:@account@:nat-gateway/@ngwId@'
    # eipArnTemplate = 'arn:aws:ec2:@region@:@account@:allocation-id/@allocationId@'
    vpcEndpointArnTemplate = 'arn:aws:ec2:@region@:@account@:vpc-endpoint/@vpcEndpointId@' 
    transitGatewayArnTemplate = 'arn:aws:ec2:@region@:@account@:transit-gateway/@transitGatewayId@'
    ec2_resource = boto3.resource('ec2')
    if event['detail']['eventName'] == 'RunInstances':
        print("tagging for new EC2...")
        # for item in event['detail']['responseElements']['instancesSet']['items']:
        #     _instanceId = item['instanceId']
        #     arnList.append(ec2ArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@instanceId@', _instanceId))

        #     _instance = ec2_resource.Instance(_instanceId)
        #     for volume in _instance.volumes.all():
        #         arnList.append(volumeArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@volumeId@', volume.id))

    # elif event['detail']['eventName'] == 'CreateVolume':
    #     print("tagging for new EBS...")
    #     volumeId = event['detail']['responseElements']['volumeId']
    #     arnList.append(volumeArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@volumeId@', volumeId))
        
    # elif event['detail']['eventName'] == 'CreateInternetGateway':
    #     print("tagging for new IGW...")
    #     igwId = event['detail']['responseElements']['internetGateway']['internetGatewayId']
    #     arnList.append(igArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@igwId@', igwId))

    # elif event['detail']['eventName'] == 'CreateNatGateway':
    #     print("tagging for new Nat Gateway...")
    #     natGatewayId = event['detail']['responseElements']['natGateway']['natGatewayId']
    #     arnList.append(ngArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@ngwId@', natGatewayId))
        
    # elif event['detail']['eventName'] == 'AllocateAddress':
    #     print("tagging for new EIP...")
    #     allocationId = event['detail']['responseElements']['allocationId']
    #     arnList.append(eipArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@allocationId@', allocationId))
        
    elif event['detail']['eventName'] == 'CreateVpcEndpoint':
        print("tagging for new VPC Endpoint...")
        vpcEndpointId = event['detail']['responseElements']['CreateVpcEndpointResponse']['vpcEndpoint']['vpcEndpointId']
        arnList.append(vpcEndpointArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@vpcEndpointId@', vpcEndpointId))
        
    # elif event['detail']['eventName'] == 'CreateTransitGateway':
    #     print("tagging for new Transit Gateway...")
    #     transitGatewayId = event['detail']['responseElements']['transitGateway']['transitGatewayId']
    #     arnList.append(transitGatewayArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@transitGatewayId@', transitGatewayId))

    # elif event['detail']['eventName'] == 'CreateVpc':
    #     print("tagging for new VPC...")
    #     vpcId = event['detail']['responseElements']['vpc']['vpcId']
    #     arnList.append(vpcArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@vpcId@', vpcId))
    
    # elif event['detail']['eventName'] == 'CreateSecurityGroup':
    #     print("tagging for new Security Group...")
    #     securityGroupId = event['detail']['responseElements']['groupId']
    #     arnList.append(sgArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@securityGroupId@', securityGroupId))

    # elif event['detail']['eventName'] == 'CreateSubnet':
    #     print("tagging for new Subnet...")
    #     subnetId = event['detail']['responseElements']['subnet']['subnetId']
    #     arnList.append(subnetArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@subnetId@', subnetId))
        
    return arnList

# def aws_elasticloadbalancing(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateLoadBalancer':
#         print("tagging for new LoadBalancer...")
#         lbs = event['detail']['responseElements']
#         for lb in lbs['loadBalancers']:
#             arnList.append(lb['loadBalancerArn'])
#     return arnList

# def aws_rds(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateDBInstance':
#         print("tagging for new RDS...")
#         arnList.append(event['detail']['responseElements']['dBInstanceArn'])
    # return arnList

def aws_s3(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateBucket':
        print("tagging for new S3...")
        _bkcuetName = event['detail']['requestParameters']['bucketName']
        arnList.append('arn:aws:s3:::' + _bkcuetName)
    return arnList
        
# def aws_lambda(event):
#     arnList = []
#     _exist1 = event['detail']['responseElements']
#     _exist2 = event['detail']['eventName'] == 'CreateFunction20150331'
#     if  _exist1!= None and _exist2:
#         function_name = event['detail']['responseElements']['functionName']
#         print('Functin name is :', function_name)
#         arnList.append(event['detail']['responseElements']['functionArn'])
#     return arnList

def aws_dynamodb(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateTable':
        table_name = event['detail']['responseElements']['tableDescription']['tableName']
        waiter = boto3.client('dynamodb').get_waiter('table_exists')
        waiter.wait(
            TableName=table_name,
            WaiterConfig={
                'Delay': 123,
                'MaxAttempts': 123
            }
        )
        arnList.append(event['detail']['responseElements']['tableDescription']['tableArn'])
    return arnList
        
# def aws_kms(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateKey':
#         arnList.append(event['detail']['responseElements']['keyMetadata']['arn'])
#     return arnList

# def aws_sns(event):
#     arnList = []
#     _account = event['account']
#     _region = event['region']
#     snsArnTemplate = 'arn:aws:sns:@region@:@account@:@topicName@'
#     if event['detail']['eventName'] == 'CreateTopic':
#         print("tagging for new SNS...")
#         _topicName = event['detail']['requestParameters']['name']
#         arnList.append(snsArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@topicName@', _topicName))
#     return arnList
        
# def aws_sqs(event):
#     arnList = []
#     _account = event['account']
#     _region = event['region']
#     sqsArnTemplate = 'arn:aws:sqs:@region@:@account@:@queueName@'
#     if event['detail']['eventName'] == 'CreateQueue':
#         print("tagging for new SQS...")
#         _queueName = event['detail']['requestParameters']['queueName']
#         arnList.append(sqsArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@queueName@', _queueName))
#     return arnList
        
def aws_elasticfilesystem(event):
    arnList = []
    _account = event['account']
    _region = event['region']
    efsArnTemplate = 'arn:aws:elasticfilesystem:@region@:@account@:file-system/@fileSystemId@'
    if event['detail']['eventName'] == 'CreateMountTarget':
        print("tagging for new efs...")
        _efsId = event['detail']['responseElements']['fileSystemId']
        arnList.append(efsArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@fileSystemId@', _efsId))
    return arnList
        
# def aws_es(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateDomain':
#         print("tagging for new open search...")
#         arnList.append(event['detail']['responseElements']['domainStatus']['aRN'])
#     return arnList

# def aws_elasticache(event):
#     arnList = []
#     _account = event['account']
#     _region = event['region']
#     ecArnTemplate = 'arn:aws:elasticache:@region@:@account@:cluster:@ecId@'

#     if event['detail']['eventName'] == 'CreateReplicationGroup' or event['detail']['eventName'] == 'ModifyReplicationGroupShardConfiguration':
#         print("tagging for new ElastiCache cluster...")
#         _replicationGroupId = event['detail']['requestParameters']['replicationGroupId']
#         waiter = boto3.client('elasticache').get_waiter('replication_group_available')
#         waiter.wait(
#             ReplicationGroupId = _replicationGroupId,
#             WaiterConfig={
#                 'Delay': 123,
#                 'MaxAttempts': 123
#             }
#         )
#         _clusters = event['detail']['responseElements']['memberClusters']
#         for _ec in _clusters:
#             arnList.append(ecArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@ecId@', _ec))

#     elif event['detail']['eventName'] == 'CreateCacheCluster':
#         print("tagging for new ElastiCache node...")
#         _cacheClusterId = event['detail']['responseElements']['cacheClusterId']
#         waiter = boto3.client('elasticache').get_waiter('cache_cluster_available')
#         waiter.wait(
#             CacheClusterId = _cacheClusterId,
#             WaiterConfig={
#                 'Delay': 123,
#                 'MaxAttempts': 123
#             }
#         )
#         arnList.append(event['detail']['responseElements']['aRN'])
#     return arnList

# def aws_redshift(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateClusterV2':
#         print("tagging for new Redshift Cluster...")
#         _clusterId = event['detail']['responseElements']['cluster']['clusterIdentifier']
#         arnList.append('arn:aws:redshift:{}:{}:cluster:{}'.format(event['region'], event['account'], _clusterId))
#     return arnList

# def aws_sagemaker(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateNotebookInstance':
#         print("tagging for new SageMaker Notebook Instance...")
#         _instanceName = event['detail']['responseElements']['notebookInstanceName']
#         arnList.append('arn:aws:sagemaker:{}:{}:notebook-instance/{}'.format(event['region'], event['account'], _instanceName))
    
#     elif event['detail']['eventName'] == 'CreateWorkgroup' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker Workgroup...")
#         workgroup_name = event['detail']['requestParameters']['workgroupName']
#         arnList.append('arn:aws:sagemaker:{}:{}:workgroup/{}'.format(event['region'], event['account'], workgroup_name))

#     elif event['detail']['eventName'] == 'CreateProcessingJob' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker Processing Job...")
#         processing_job_name = event['detail']['responseElements']['processingJobName']
#         arnList.append('arn:aws:sagemaker:{}:{}:processing-job/{}'.format(event['region'], event['account'], processing_job_name))

#     elif event['detail']['eventName'] == 'CreateEndpoint' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker Endpoint...")
#         endpoint_name = event['detail']['responseElements']['endpoint']['endpointName']
#         arnList.append('arn:aws:sagemaker:{}:{}:endpoint/{}'.format(event['region'], event['account'], endpoint_name))

#     elif event['detail']['eventName'] == 'CreateModel' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker Model...")
#         model_name = event['detail']['responseElements']['model']['modelName']
#         arnList.append('arn:aws:sagemaker:{}:{}:model/{}'.format(event['region'], event['account'], model_name))

#     elif event['detail']['eventName'] == 'CreateLabelingJob' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker Labeling Job...")
#         labeling_job_name = event['detail']['responseElements']['labelingJobName']
#         arnList.append('arn:aws:sagemaker:{}:{}:labeling-job/{}'.format(event['region'], event['account'], labeling_job_name))

#     elif event['detail']['eventName'] == 'CreateTrainingJob' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker Training Job...")
#         training_job_name = event['detail']['responseElements']['trainingJobName']
#         arnList.append('arn:aws:sagemaker:{}:{}:training-job/{}'.format(event['region'], event['account'], training_job_name))

#     elif event['detail']['eventName'] == 'CreateTransformJob' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker Transform Job...")
#         transform_job_name = event['detail']['responseElements']['transformJobName']
#         arnList.append('arn:aws:sagemaker:{}:{}:transform-job/{}'.format(event['region'], event['account'], transform_job_name))

#     elif event['detail']['eventName'] == 'CreateUserProfile' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker User Profile...")
#         user_profile_name = event['detail']['responseElements']['userProfileName']
#         arnList.append('arn:aws:sagemaker:{}:{}:user-profile/{}'.format(event['region'], event['account'], user_profile_name))

#     elif event['detail']['eventName'] == 'CreateWorkteam' and event['source'] == 'aws.sagemaker':
#         print("tagging for new SageMaker Workteam...")
#         workteam_name = event['detail']['responseElements']['workteam']['workteamName']
#         arnList.append('arn:aws:sagemaker:{}:{}:workteam/{}'.format(event['region'], event['account'], workteam_name))
#     return arnList

# def aws_ecs(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateCluster':
#         print("tagging for new ECS Cluster...")
#         _clusterName = event['detail']['responseElements']['cluster']['clusterName']
#         arnList.append('arn:aws:ecs:{}:{}:cluster/{}'.format(event['region'], event['account'], _clusterName))
#     return arnList

# def aws_monitoring(event):
#     arnList = []
#     if event['detail']['eventName'] == 'PutMetricAlarm':
#         print("tagging for new CloudWatch Alarm...")
#         _alarmName = event['detail']['requestParameters']['alarmName']
#         arnList.append('arn:aws:cloudwatch:{}:{}:alarm:{}'.format(event['region'], event['account'], _alarmName))
#     return arnList

# def aws_logs(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateLogGroup':
#         print("tagging for new CloudWatch Log Group...")
#         _logGroupName = event['detail']['requestParameters']['logGroupName']
#         arnList.append('arn:aws:logs:{}:{}:log-group:{}'.format(event['region'], event['account'], _logGroupName))
#     return arnList

# def aws_kafka(event):
#     arnList = []
#     if (
#         event['detail']['eventName'] == 'CreateBroker'
#         and event['source'] == 'aws.kafka'
#     ):
#         print("tagging for new MSK Broker...")
#         _brokerId = event['detail']['responseElements']['broker']['brokerId']
#         arnList.append('arn:aws:kafka:{}:{}:cluster/b-{}'.format(event['region'], event['account'], _brokerId))
#     return arnList

# def aws_amazonmq(event):
#     arnList = []
#     if (
#         event['detail']['eventName'] == 'CreateBroker'
#         and event['source'] == 'aws.amazonmq'
#     ):
#         print("tagging for new Amazon MQ Broker...")
#         _brokerId = event['detail']['responseElements']['broker']['brokerId']
#         arnList.append('arn:aws:mq:{}:{}:broker:{}'.format(event['region'], event['account'], _brokerId))
#     return arnList

# def aws_glue(event):
#     arnList = []
#     if event['detail']['eventName'] == 'CreateNamespace' and event['source'] == 'aws.glue':
#         print("tagging for new Glue Namespace...")
#         namespace_name = event['detail']['requestParameters']['name']
#         arnList.append('arn:aws:glue:{}:{}:namespace/{}'.format(event['region'], event['account'], namespace_name))
#     return arnList
  
def get_created_by_identity(event):
    if event['detail']['userIdentity']['type'] == 'IAMUser':
        return event['detail']['userIdentity']['userName']
    else:
        arn_parts = event['detail']["userIdentity"]["arn"].split(":")
        return "/".join(arn_parts[5:])

def convert_to_ist_time(utc_time_str):
    from_zone = tz.gettz("UTC")
    to_zone = tz.gettz("Asia/Kolkata")  # IST timezone

    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=from_zone)

    ist_time = utc_time.astimezone(to_zone)
    return ist_time.strftime("%Y-%m-%d %H:%M:%S %Z")

def lambda_handler(event, context):
    print(f"input event is: {event}")
    print("new source is ", event['source'])
    _method = event['source'].replace('.', "_")

    resARNs = globals()[_method](event)
    print("resource arn is: ", resARNs)

    event_time_utc_str = event["detail"]["eventTime"]

    _res_tags = {
        'CreatedBy': get_created_by_identity(event),
        'CreatedOn': convert_to_ist_time(event_time_utc_str),
        'Division': 'CD',  
        'Studio': 'Ajax'}
    boto3.client('resourcegroupstaggingapi').tag_resources(
        ResourceARNList=resARNs,
        Tags=_res_tags
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Finished tagging with ' + event['source'])
    }
