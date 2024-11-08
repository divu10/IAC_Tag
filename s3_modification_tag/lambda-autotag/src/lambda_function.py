import boto3

def lambda_handler(event, context):
    # Initialize EFS client
    efs_client = boto3.client('efs')

    print(f"Received event: {event}")

    try:
        # Handle two possible structures: with or without 'detail'
        event_detail = event.get('detail', event)
        
        # Capture event name
        event_name = event_detail.get('eventName')
        if not event_name:
            print("Event name not found in event")
            return {"statusCode": 400, "body": "Event name not found"}

        print(f"Event name: {event_name}")

        # Avoid infinite loop
        user_identity = event_detail.get('userIdentity', {})
        if user_identity.get('type') == "AssumedRole" and "autotag" in user_identity.get('arn', '') and event_name == "TagResource":
            print("Event triggered by Lambda itself; skipping to avoid loop.")
            return {"statusCode": 200, "body": "Ignored event to prevent infinite loop"}

        # Handle specific events
        if event_name not in ['TagResource', 'UntagResource']:
            print(f"Unsupported event: {event_name}")
            return {"statusCode": 400, "body": f"Unsupported event: {event_name}"}

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

        # Define mandatory tags
        mandatory_tags = [
            {'Key': 'Division', 'Value': 'CD'},
            {'Key': 'Studio', 'Value': 'Ajax'}
        ]

        current_tags_set = {tag['Key']: tag['Value'] for tag in current_tags}

        # Handle UntagResource
        if event_name == 'UntagResource':
            efs_client.tag_resource(
                ResourceId=resource_id,
                Tags=mandatory_tags
            )
            print(f"Re-applied tags for {resource_id}")
            return {"statusCode": 200, "body": f"Tags re-applied for {resource_id}"}

        # Handle TagResource
        elif event_name == 'TagResource':
            for mandatory_tag in mandatory_tags:
                if mandatory_tag['Key'] not in current_tags_set:
                    print(f"Mandatory tag {mandatory_tag['Key']} not found, adding...")
                    current_tags.append(mandatory_tag)

            efs_client.tag_resource(
                ResourceId=resource_id,
                Tags=current_tags
            )
            print(f"Tags applied for {resource_id}: {current_tags}")
            return {"statusCode": 200, "body": f"Tags handled for {resource_id}"}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}
