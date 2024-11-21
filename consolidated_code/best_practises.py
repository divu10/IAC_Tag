import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main handler for the Lambda function.
    Handles tagging events for EC2, DynamoDB, S3, and EFS resources.
    """
    # Initialize clients for AWS services
    ec2_client = boto3.client('ec2')
    dynamodb_client = boto3.client('dynamodb')
    efs_client = boto3.client('efs')
    s3_client = boto3.client('s3')

    logger.info("Received event: %s", event)

    try:
        # Extract event details
        event_detail = event.get('detail', event)

        # Identify the event source
        event_source = event_detail.get('eventSource')
        if not event_source:
            logger.error("Event source not found in event")
            return {"statusCode": 400, "body": "Event source not found"}

        logger.info("Event source: %s", event_source)

        # Capture event name
        event_name = event_detail.get('eventName')
        if not event_name:
            logger.error("Event name not found in event")
            return {"statusCode": 400, "body": "Event name not found"}

        logger.info("Event name: %s", event_name)

        # Avoid infinite loops for auto-applied tags
        user_identity = event_detail.get('userIdentity', {})
        if user_identity.get('type') == "AssumedRole" and "autotag" in user_identity.get('arn', ''):
            logger.info("Event triggered by Lambda itself; skipping to avoid loop.")
            return {"statusCode": 200, "body": "Ignored event to prevent infinite loop"}

        # Define mandatory tags
        mandatory_tags = [
            {'Key': 'Division', 'Value': 'CD'},
            {'Key': 'Studio', 'Value': 'Ajax'}
        ]

        # Handle events based on their source
        event_handlers = {
            'ec2.amazonaws.com': handle_ec2_event,
            'dynamodb.amazonaws.com': handle_dynamodb_event,
            's3.amazonaws.com': handle_s3_event,
            'elasticfilesystem.amazonaws.com': handle_efs_event,
        }

        handler = event_handlers.get(event_source)
        if handler:
            return handler(event_detail, ec2_client, dynamodb_client, s3_client, efs_client, mandatory_tags)
        else:
            logger.error("Unsupported event source: %s", event_source)
            return {"statusCode": 400, "body": f"Unsupported event source: {event_source}"}

    except Exception as e:
        logger.exception("Error processing event")
        return {"statusCode": 500, "body": str(e)}


def handle_ec2_event(event_detail, ec2_client, *args):
    """
    Handles EC2 resource events and applies mandatory tags.
    """
    resource_items = event_detail.get("requestParameters", {}).get("resourcesSet", {}).get("items", [])
    if not resource_items or "resourceId" not in resource_items[0]:
        logger.error("Resource ID not found in the event")
        return {"statusCode": 400, "body": "Resource ID not found in the event"}

    resource_id = resource_items[0]["resourceId"]
    logger.info("Resource ID: %s", resource_id)

    try:
        ec2_client.create_tags(
            Resources=[resource_id],
            Tags=[{"Key": tag['Key'], "Value": tag['Value']} for tag in args[-1]]
        )
        logger.info("Tags applied to EC2 instance %s: %s", resource_id, args[-1])
        return {"statusCode": 200, "body": f"Tags handled for EC2 instance {resource_id}"}
    except Exception as e:
        logger.exception("Error applying tags to EC2 instance")
        return {"statusCode": 500, "body": str(e)}


def handle_dynamodb_event(event_detail, *args):
    """
    Handles DynamoDB resource events and applies mandatory tags.
    """
    dynamodb_client = args[1]
    mandatory_tags = args[-1]
    
    request_parameters = event_detail.get("requestParameters", {})
    resource_arn = request_parameters.get("resourceArn")
    if not resource_arn:
        logger.error("ResourceArn not found in the event")
        return {"statusCode": 400, "body": "ResourceArn not found in the event"}

    logger.info("ResourceArn: %s", resource_arn)

    tags = request_parameters.get("tags", [])
    if not isinstance(tags, list):
        logger.error("Tags are missing or invalid in the event")
        return {"statusCode": 400, "body": "Tags are missing or invalid in the event"}

    current_tags_set = {tag['key']: tag['value'] for tag in tags if 'key' in tag and 'value' in tag}
    for mandatory_tag in mandatory_tags:
        if mandatory_tag['Key'] not in current_tags_set:
            logger.info("Mandatory tag %s not found, adding...", mandatory_tag['Key'])
            tags.append({'key': mandatory_tag['Key'], 'value': mandatory_tag['Value']})

    try:
        dynamodb_client.tag_resource(
            ResourceArn=resource_arn,
            Tags=[{'Key': tag['key'], 'Value': tag['value']} for tag in tags]
        )
        logger.info("Tags applied to DynamoDB resource %s: %s", resource_arn, tags)
        return {"statusCode": 200, "body": f"Tags handled for DynamoDB resource {resource_arn}"}
    except Exception as e:
        logger.exception("Error applying tags to DynamoDB resource")
        return {"statusCode": 500, "body": str(e)}


def handle_s3_event(event_detail, *args):
    """
    Handles S3 bucket events and applies mandatory tags.
    """
    s3_client = args[2]
    mandatory_tags = args[-1]

    bucket_name = event_detail.get("requestParameters", {}).get("bucketName")
    if not bucket_name:
        logger.error("Bucket name not found in the event")
        return {"statusCode": 400, "body": "Bucket name not found in the event"}

    logger.info("Bucket name: %s", bucket_name)

    try:
        current_tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        current_tags = current_tags_response.get('TagSet', [])
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchTagSet':
            current_tags = []
        else:
            logger.exception("Error fetching current tags")
            return {"statusCode": 500, "body": str(e)}

    valid_tags = [tag for tag in current_tags if not tag['Key'].startswith('aws:')]
    current_tags_set = {tag['Key']: tag['Value'] for tag in valid_tags}
    for mandatory_tag in mandatory_tags:
        if mandatory_tag['Key'] not in current_tags_set:
            logger.info("Mandatory tag %s not found, adding...", mandatory_tag['Key'])
            valid_tags.append(mandatory_tag)

    try:
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': valid_tags}
        )
        logger.info("Tags applied to S3 bucket %s: %s", bucket_name, valid_tags)
        return {"statusCode": 200, "body": f"Tags handled for S3 bucket {bucket_name}"}
    except Exception as e:
        logger.exception("Error applying tags to S3 bucket")
        return {"statusCode": 500, "body": str(e)}


def handle_efs_event(event_detail, *args):
    """
    Handles EFS resource events and applies mandatory tags.
    """
    efs_client = args[3]
    mandatory_tags = args[-1]

    resource_id = event_detail.get("requestParameters", {}).get("resourceId")
    if not resource_id:
        logger.error("ResourceId not found in the event")
        return {"statusCode": 400, "body": "ResourceId not found in the event"}

    logger.info("ResourceId: %s", resource_id)

    try:
        current_tags_response = efs_client.describe_tags(FileSystemId=resource_id)
        current_tags = current_tags_response.get('Tags', [])
    except efs_client.exceptions.ClientError as e:
        logger.exception("Error fetching current tags")
        return {"statusCode": 500, "body": str(e)}

    valid_tags = [tag for tag in current_tags if not tag['Key'].startswith('aws:')]
    current_tags_set = {tag['Key']: tag['Value'] for tag in valid_tags}
    for mandatory_tag in mandatory_tags:
        if mandatory_tag['Key'] not in current_tags_set:
            logger.info("Mandatory tag %s not found, adding...", mandatory_tag['Key'])
            valid_tags.append(mandatory_tag)

    try:
        efs_client.tag_resource(
            ResourceId=resource_id,
            Tags=valid_tags
        )
        logger.info("Tags applied to EFS resource %s: %s", resource_id, valid_tags)
        return {"statusCode": 200, "body": f"Tags handled for EFS resource {resource_id}"}
    except Exception as e:
        logger.exception("Error applying tags to EFS resource")
        return {"statusCode": 500, "body": str(e)}
