import boto3

def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamodb_client = boto3.client('dynamodb')

    print(f"Received event: {event}")

    try:
        # Extract event details
        event_detail = event.get('detail', event)
        
        # Capture event name
        event_name = event_detail.get('eventName')
        if not event_name:
            print("Event name not found in event")
            return {"statusCode": 400, "body": "Event name not found"}

        print(f"Event name: {event_name}")

        # Prevent infinite loops
        user_identity = event_detail.get('userIdentity', {})
        if user_identity.get('type') == "AssumedRole" and "autotag" in user_identity.get('arn', '') and event_name == "TagResource":
            print("Event triggered by Lambda itself; skipping to avoid loop.")
            return {"statusCode": 200, "body": "Ignored event to prevent infinite loop"}

        # Supported events
        if event_name not in ['TagResource', 'UntagResource']:
            print(f"Unsupported event: {event_name}")
            return {"statusCode": 400, "body": f"Unsupported event: {event_name}"}

        # Retrieve resource ARN
        resource_arn = event_detail.get("requestParameters", {}).get("resourceArn")
        if not resource_arn:
            print("ResourceArn not found in the event")
            return {"statusCode": 400, "body": "ResourceArn not found in the event"}

        print(f"ResourceArn: {resource_arn}")

        # Get current tags
        try:
            current_tags_response = dynamodb_client.list_tags_of_resource(ResourceArn=resource_arn)
            current_tags = current_tags_response.get('Tags', [])
        except dynamodb_client.exceptions.ClientError as e:
            print(f"Error fetching current tags: {e}")
            return {"statusCode": 500, "body": f"Error fetching tags: {str(e)}"}

        # Define mandatory tags
        mandatory_tags = [
            {'Key': 'Division', 'Value': 'CD'},
            {'Key': 'Studio', 'Value': 'Ajax'}
        ]
        current_tags_dict = {tag['Key']: tag['Value'] for tag in current_tags}

        # Handle UntagResource
        if event_name == 'UntagResource':
            print(f"Handling UntagResource for {resource_arn}")
            # Reapply mandatory tags
            dynamodb_client.tag_resource(
                ResourceArn=resource_arn,
                Tags=mandatory_tags
            )
            print(f"Re-applied tags for {resource_arn}")
            return {"statusCode": 200, "body": f"Tags re-applied for {resource_arn}"}

        # Handle TagResource
        elif event_name == 'TagResource':
            print(f"Handling TagResource for {resource_arn}")
            # Ensure mandatory tags are present
            tags_to_apply = current_tags.copy()
            for mandatory_tag in mandatory_tags:
                if mandatory_tag['Key'] not in current_tags_dict:
                    print(f"Adding missing mandatory tag: {mandatory_tag}")
                    tags_to_apply.append(mandatory_tag)

            dynamodb_client.tag_resource(
                ResourceArn=resource_arn,
                Tags=tags_to_apply
            )
            print(f"Tags applied for {resource_arn}: {tags_to_apply}")
            return {"statusCode": 200, "body": f"Tags handled for {resource_arn}"}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}
