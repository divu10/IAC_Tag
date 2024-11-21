import boto3

def lambda_handler(event, context):
    # Initialize clients for EFS and S3
    efs_client = boto3.client('efs')
    s3_client = boto3.client('s3')

    print(f"Received event: {event}")

    try:
        # Handle two possible structures: with or without 'detail'
        event_detail = event.get('detail', event)

        # Identify the event source
        event_source = event_detail.get('eventSource')
        if not event_source:
            print("Event source not found in event")
            return {"statusCode": 400, "body": "Event source not found"}

        print(f"Event source: {event_source}")

        # Capture event name
        event_name = event_detail.get('eventName')
        if not event_name:
            print("Event name not found in event")
            return {"statusCode": 400, "body": "Event name not found"}

        print(f"Event name: {event_name}")

        # Avoid infinite loops for auto-applied tags
        user_identity = event_detail.get('userIdentity', {})
        if user_identity.get('type') == "AssumedRole" and "autotag" in user_identity.get('arn', ''):
            print("Event triggered by Lambda itself; skipping to avoid loop.")
            return {"statusCode": 200, "body": "Ignored event to prevent infinite loop"}

        # Define mandatory tags
        mandatory_tags = [
            {'Key': 'Division', 'Value': 'CD'},
            {'Key': 'Studio', 'Value': 'Ajax'}
        ]

        # Handle S3 events
        if event_source == 's3.amazonaws.com':
            return handle_s3_event(event_detail, s3_client, mandatory_tags)

        # Handle EFS events
        elif event_source == 'elasticfilesystem.amazonaws.com':
            return handle_efs_event(event_detail, efs_client, mandatory_tags)

        else:
            print(f"Unsupported event source: {event_source}")
            return {"statusCode": 400, "body": f"Unsupported event source: {event_source}"}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}


def handle_s3_event(event_detail, s3_client, mandatory_tags):
    # Retrieve bucket name
    bucket_name = event_detail.get("requestParameters", {}).get("bucketName")
    if not bucket_name:
        print("Bucket name not found in the event")
        return {"statusCode": 400, "body": "Bucket name not found in the event"}

    print(f"Bucket name: {bucket_name}")

    # Get current tags
    try:
        current_tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        current_tags = current_tags_response.get('TagSet', [])
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchTagSet':
            current_tags = []
        else:
            print(f"Error fetching current tags: {e}")
            return {"statusCode": 500, "body": str(e)}

    print(f"Current tags: {current_tags}")

    # Filter out AWS-reserved tags
    valid_tags = [tag for tag in current_tags if not tag['Key'].startswith('aws:')]

    # Add mandatory tags if missing
    current_tags_set = {tag['Key']: tag['Value'] for tag in valid_tags}
    for mandatory_tag in mandatory_tags:
        if mandatory_tag['Key'] not in current_tags_set:
            print(f"Mandatory tag {mandatory_tag['Key']} not found, adding...")
            valid_tags.append(mandatory_tag)

    # Apply tags back to the bucket
    try:
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': valid_tags}
        )
        print(f"Tags applied to S3 bucket {bucket_name}: {valid_tags}")
        return {"statusCode": 200, "body": f"Tags handled for S3 bucket {bucket_name}"}
    except Exception as e:
        print(f"Error applying tags: {e}")
        return {"statusCode": 500, "body": str(e)}


def handle_efs_event(event_detail, efs_client, mandatory_tags):
    # Retrieve ResourceId
    resource_id = event_detail.get("requestParameters", {}).get("resourceId")
    if not resource_id:
        print("ResourceId not found in the event")
        return {"statusCode": 400, "body": "ResourceId not found in the event"}

    print(f"ResourceId: {resource_id}")

    # Get current tags
    try:
        current_tags_response = efs_client.describe_tags(FileSystemId=resource_id)
        current_tags = current_tags_response.get('Tags', [])
    except efs_client.exceptions.ClientError as e:
        print(f"Error fetching current tags: {e}")
        return {"statusCode": 500, "body": str(e)}

    print(f"Current tags: {current_tags}")

    # Filter out AWS-reserved tags
    valid_tags = [tag for tag in current_tags if not tag['Key'].startswith('aws:')]

    # Add mandatory tags if missing
    current_tags_set = {tag['Key']: tag['Value'] for tag in valid_tags}
    for mandatory_tag in mandatory_tags:
        if mandatory_tag['Key'] not in current_tags_set:
            print(f"Mandatory tag {mandatory_tag['Key']} not found, adding...")
            valid_tags.append(mandatory_tag)

    # Apply tags back to the EFS resource
    try:
        efs_client.tag_resource(
            ResourceId=resource_id,
            Tags=valid_tags
        )
        print(f"Tags applied to EFS resource {resource_id}: {valid_tags}")
        return {"statusCode": 200, "body": f"Tags handled for EFS resource {resource_id}"}
    except Exception as e:
        print(f"Error applying tags: {e}")
        return {"statusCode": 500, "body": str(e)}
