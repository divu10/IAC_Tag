import boto3
import os
import json
from datetime import datetime
from dateutil import tz

def aws_ec2(event):
    arnList = []
    _account = event['account']
    _region = event['region']
    vpcEndpointArnTemplate = 'arn:aws:ec2:@region@:@account@:vpc-endpoint/@vpcEndpointId@' 
    #ec2_resource = boto3.resource('ec2')
    if event['detail']['eventName'] == 'RunInstances':
        print("tagging for new EC2...")
    
    elif event['detail']['eventName'] == 'CreateVpcEndpoint':
        print("tagging for new VPC Endpoint...")
        vpcEndpointId = event['detail']['responseElements']['CreateVpcEndpointResponse']['vpcEndpoint']['vpcEndpointId']
        arnList.append(vpcEndpointArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@vpcEndpointId@', vpcEndpointId))
        
   

def aws_s3(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateBucket':
        print("tagging for new S3...")
        _bkcuetName = event['detail']['requestParameters']['bucketName']
        arnList.append('arn:aws:s3:::' + _bkcuetName)
    return arnList
        


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
