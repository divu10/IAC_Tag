import boto3

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')

    print(f"Received event: {event}")

    try:
        # Capture event name
        if 'detail' not in event:
            print("Missing 'detail' in event")
            return {"statusCode": 400, "body": "Missing 'detail' in event"}

        event_name = event['detail'].get('eventName')
        print(f"Event name: {event_name}")

        # Avoid infinite loops
        user_identity = event['detail'].get('userIdentity', {})
        if user_identity.get('type') == "AssumedRole" and "autotag" in user_identity.get('arn', ''):
            print("Event triggered by Lambda itself; skipping to avoid loop.")
            return {"statusCode": 200, "body": "Ignored event to prevent infinite loop"}

        # Supported events
        if event_name not in ['CreateTags', 'DeleteTags']:
            print(f"Unsupported event: {event_name}")
            return {"statusCode": 400, "body": f"Unsupported event: {event_name}"}

        # Retrieve the resource ID from the event
        resource_items = event["detail"]["requestParameters"]["resourcesSet"]["items"]
        if not resource_items or "resourceId" not in resource_items[0]:
            print("Resource ID not found in the event")
            return {"statusCode": 400, "body": "Resource ID not found in the event"}

        resource_id = resource_items[0]["resourceId"]
        print(f"Resource ID: {resource_id}")

        # Get current tags for the resource
        current_tags_response = ec2_client.describe_tags(
            Filters=[{'Name': 'resource-id', 'Values': [resource_id]}]
        )
        current_tags = current_tags_response.get('Tags', [])
        current_tags_dict = {tag['Key']: tag['Value'] for tag in current_tags}

        # Define mandatory tags
        mandatory_tags = [
            {'Key': 'Division', 'Value': 'CD'},
            {'Key': 'Studio', 'Value': 'Ajax'}
        ]

        if event_name == 'DeleteTags':
            print(f"Handling DeleteTags for {resource_id}")
            # Reapply mandatory tags if they were deleted
            ec2_client.create_tags(
                Resources=[resource_id],
                Tags=[tag for tag in mandatory_tags if tag['Key'] not in current_tags_dict]
            )
            print(f"Re-applied mandatory tags for {resource_id}")
            return {"statusCode": 200, "body": f"Re-applied mandatory tags for {resource_id}"}

        elif event_name == 'CreateTags':
            print(f"Handling CreateTags for {resource_id}")
            # Ensure mandatory tags are present
            tags_to_apply = []
            for mandatory_tag in mandatory_tags:
                if mandatory_tag['Key'] not in current_tags_dict:
                    tags_to_apply.append(mandatory_tag)

            if tags_to_apply:
                ec2_client.create_tags(
                    Resources=[resource_id],
                    Tags=tags_to_apply
                )
                print(f"Added missing mandatory tags: {tags_to_apply}")
            else:
                print("All mandatory tags are already present.")
            return {"statusCode": 200, "body": f"Tags validated for {resource_id}"}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}
